from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import SavedCard, Wallet, SavingsPlan
from .serializers import (
    SavedCardSerializer,
    SavingsPlanCreateSerializer,
    SavingsWithdrawSerializer,
)


# --------------------------------------------------
# LIST SAVED CARDS
# --------------------------------------------------
@extend_schema(
    responses={200: SavedCardSerializer(many=True)},
    tags=["Payments"],
)
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
# INIT WALLET FUNDING (TEST MODE → SIMULATION ONLY)
# --------------------------------------------------
@extend_schema(
    responses={200: OpenApiResponse(description="Returns test pay URL")},
    tags=["Wallet"],
)
class InitWalletFundingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({
            "message": "TEST MODE: Wallet funding simulated.",
            "authorization_url": "https://paystack.com/pay/test-mode",
            "reference": "TEST-WALLET-REF",
        })


# --------------------------------------------------
# CREATE SAVINGS PLAN
# --------------------------------------------------
@extend_schema(
    request=SavingsPlanCreateSerializer,
    responses={201: OpenApiResponse(description="Savings created & locked")},
    tags=["Savings"],
)
class CreateSavingsPlanView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        wallet = Wallet.objects.select_for_update().get(user=request.user)

        serializer = SavingsPlanCreateSerializer(
            data=request.data,
            context={"wallet": wallet},
        )
        serializer.is_valid(raise_exception=True)
        savings = serializer.save()

        return Response({
            "message": "Savings plan created & locked successfully.",
            "savings_id": savings.id,
            "plan_type": savings.plan_type,
            "amount": str(savings.amount),
            "locked_until": savings.locked_until,
        }, status=201)


# --------------------------------------------------
# WITHDRAW SAVINGS (W1: EARLY BREAK PENALTY)
# --------------------------------------------------
@extend_schema(
    request=SavingsWithdrawSerializer,
    responses={200: OpenApiResponse(description="Savings withdrawn")},
    tags=["Savings"],
)
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

        return Response({
            "message": "Savings withdrawn.",
            "savings_id": savings.id,
            "amount": str(amount),
            "penalty": str(savings.penalty_amount or "0"),
            "wallet_balance": str(wallet.balance),
            "status": savings.status,
        }, status=200)


# --------------------------------------------------
# WALLET BALANCE ENDPOINT
# --------------------------------------------------
@extend_schema(
    tags=["Wallet"],
    responses={200: OpenApiResponse(description="Wallet balance")},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def wallet_me(request):
    try:
        wallet = Wallet.objects.get(user=request.user)
        return Response({
            "balance": float(wallet.balance),
            "locked_balance": float(wallet.locked_balance),
            "currency": "NGN",
        })
    except Wallet.DoesNotExist:
        return Response({"detail": "Wallet not found"}, status=404)

