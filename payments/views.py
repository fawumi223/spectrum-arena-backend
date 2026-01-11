from decimal import Decimal

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.conf import settings
from django.db import transaction
from django.utils import timezone

import requests

from .models import (
    SavedCard,
    IdempotencyKey,
    Wallet,
    SavingsPlan,
)
from .serializers import (
    SavedCardSerializer,
    SavingsPlanCreateSerializer,
    SavingsWithdrawSerializer,
)
from .services.paystack import charge_authorization
from .tasks import unlock_savings_plan


# --------------------------------------------------
# LIST SAVED CARDS (STEP 3)
# --------------------------------------------------
class SavedCardsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cards = SavedCard.objects.filter(
            user=request.user,
            reusable=True,
            is_active=True,
        ).order_by("-created_at")

        serializer = SavedCardSerializer(cards, many=True)
        return Response(serializer.data)


# --------------------------------------------------
# INIT WALLET FUNDING (FIRST-TIME CARD ENTRY)
# --------------------------------------------------
class InitWalletFundingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")

        if not amount:
            return Response(
                {"detail": "Amount is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = {
            "email": request.user.email,
            "amount": int(float(amount) * 100),  # kobo
            "metadata": {
                "payment_type": "wallet",
                "user_id": request.user.id,
            },
            "callback_url": settings.PAYSTACK_CALLBACK_URL,
        }

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            json=payload,
            headers=headers,
            timeout=30,
        )

        data = response.json()

        if not data.get("status"):
            return Response(
                {"detail": "Unable to initialize wallet funding"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "authorization_url": data["data"]["authorization_url"],
                "reference": data["data"]["reference"],
            },
            status=status.HTTP_200_OK,
        )


# --------------------------------------------------
# INIT SAVINGS FUNDING (FIRST-TIME CARD ENTRY)
# --------------------------------------------------
class InitSavingsFundingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")
        savings_id = request.data.get("savings_id")

        if not amount or not savings_id:
            return Response(
                {"detail": "Amount and savings_id are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = {
            "email": request.user.email,
            "amount": int(float(amount) * 100),  # kobo
            "metadata": {
                "payment_type": "savings",
                "user_id": request.user.id,
                "savings_id": savings_id,
            },
            "callback_url": settings.PAYSTACK_CALLBACK_URL,
        }

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            "https://api.paystack.co/transaction/initialize",
            json=payload,
            headers=headers,
            timeout=30,
        )

        data = response.json()

        if not data.get("status"):
            return Response(
                {"detail": "Unable to initialize savings funding"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "authorization_url": data["data"]["authorization_url"],
                "reference": data["data"]["reference"],
            },
            status=status.HTTP_200_OK,
        )


# --------------------------------------------------
# CREATE SAVINGS / THRIFT PLAN (LEDGER LOCK)
# --------------------------------------------------
class CreateSavingsPlanView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        wallet = Wallet.objects.select_for_update().get(user=request.user)

        serializer = SavingsPlanCreateSerializer(
            data=request.data,
            context={"wallet": wallet},
        )

        if serializer.is_valid():
            savings = serializer.save()

            # ⏰ Schedule auto-unlock
            unlock_savings_plan.apply_async(
                args=[savings.id],
                eta=savings.locked_until,
            )

            return Response(
                {
                    "message": "Savings plan created and locked successfully.",
                    "savings_id": savings.id,
                    "amount": str(savings.amount),
                    "locked_until": savings.locked_until,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --------------------------------------------------
# WITHDRAW SAVINGS (NORMAL OR EARLY BREAK)
# --------------------------------------------------
class WithdrawSavingsView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, savings_id):
        savings = SavingsPlan.objects.select_for_update().get(
            id=savings_id,
            wallet__user=request.user,
        )

        serializer = SavingsWithdrawSerializer(
            data=request.data,
            context={"savings": savings},
        )
        serializer.is_valid(raise_exception=True)

        wallet = savings.wallet
        amount = savings.amount

        # --------------------------------
        # EARLY BREAK PENALTY (10%)
        # --------------------------------
        if savings.status == "locked":
            penalty = (Decimal("0.10") * amount).quantize(Decimal("0.01"))
            payout = amount - penalty

            wallet.balance += payout
            savings.penalty_amount = penalty
            savings.status = "broken"
            savings.broken_at = timezone.now()

        else:
            wallet.balance += amount
            savings.status = "unlocked"
            savings.unlocked_at = timezone.now()

        wallet.save(update_fields=["balance"])
        savings.save()

        return Response(
            {
                "message": "Savings withdrawn successfully.",
                "amount_received": str(wallet.balance),
                "penalty": str(savings.penalty_amount),
            },
            status=status.HTTP_200_OK,
        )


# --------------------------------------------------
# CHARGE SAVED CARD (WALLET OR SAVINGS + IDEMPOTENCY)
# --------------------------------------------------
class ChargeSavedCardView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")
        idem_key = request.headers.get("Idempotency-Key")

        payment_type = request.data.get("payment_type", "wallet")
        savings_id = request.data.get("savings_id")

        if not amount or not idem_key:
            return Response(
                {"detail": "Amount and Idempotency-Key are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------
        # IDEMPOTENCY GUARD
        # --------------------------------
        existing = IdempotencyKey.objects.filter(
            user=request.user,
            key=idem_key,
            endpoint="charge-card",
        ).first()

        if existing:
            return Response(existing.response, status=status.HTTP_200_OK)

        # --------------------------------
        # FETCH SAVED CARD
        # --------------------------------
        card = SavedCard.objects.filter(
            user=request.user,
            reusable=True,
            is_active=True,
        ).first()

        if not card:
            return Response(
                {"detail": "No saved card found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------
        # CHARGE VIA PAYSTACK
        # --------------------------------
        paystack_res = charge_authorization(
            email=request.user.email,
            amount=int(float(amount) * 100),  # kobo
            authorization_code=card.authorization_code,
            metadata={
                "payment_type": payment_type,
                "user_id": request.user.id,
                "savings_id": savings_id,
            },
        )

        if not paystack_res.get("status"):
            response_data = {
                "success": False,
                "message": paystack_res.get("message"),
            }

            IdempotencyKey.objects.create(
                user=request.user,
                key=idem_key,
                endpoint="charge-card",
                response=response_data,
            )

            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        response_data = {
            "success": True,
            "reference": paystack_res["data"]["reference"],
            "message": "Charge initiated. Awaiting confirmation.",
        }

        IdempotencyKey.objects.create(
            user=request.user,
            key=idem_key,
            endpoint="charge-card",
            response=response_data,
        )

        # IMPORTANT:
        # Wallet/Savings crediting happens ONLY in webhook

        return Response(response_data, status=status.HTTP_200_OK)

