import uuid
from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Wallet, DataBundle, UtilityTransaction
from .vtpass_service import purchase_data, purchase_airtime


# --------------------------------------------------
# LIST DATA BUNDLES
# --------------------------------------------------
class DataBundleListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        network = request.query_params.get("network")
        category = request.query_params.get("category")

        bundles = DataBundle.objects.filter(is_active=True)

        if network:
            bundles = bundles.filter(network=network)

        if category:
            bundles = bundles.filter(category=category)

        data = []

        for b in bundles:
            data.append({
                "id": b.id,
                "network": b.network,
                "name": b.name,
                "volume": b.volume,
                "validity": b.validity,
                "price": float(b.selling_price),
            })

        return Response(data)


# --------------------------------------------------
# PURCHASE DATA BUNDLE
# --------------------------------------------------
class PurchaseDataView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):

        bundle_id = request.data.get("bundle_id")
        phone = request.data.get("phone")

        if not bundle_id or not phone:
            return Response(
                {"error": "bundle_id and phone are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        bundle = get_object_or_404(DataBundle, id=bundle_id, is_active=True)

        wallet = Wallet.objects.select_for_update().get(user=request.user)

        amount = Decimal(bundle.selling_price)

        if wallet.balance < amount:
            return Response(
                {"error": "Insufficient wallet balance"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        wallet.balance -= amount
        wallet.save(update_fields=["balance"])

        try:
            response, reference = purchase_data(
                phone=phone,
                service_id=bundle.network,
                billers_code=phone,
                variation_code=bundle.vtpass_code,
                amount=float(amount),
            )

            status_flag = "success"

        except Exception as e:
            status_flag = "failed"
            response = {"error": str(e)}
            reference = str(uuid.uuid4())

        UtilityTransaction.objects.create(
            user=request.user,
            wallet=wallet,
            transaction_type="data",
            network=bundle.network,
            phone_number=phone,
            amount=amount,
            reference=reference,
            status=status_flag,
            provider_response=response,
        )

        return Response({
            "message": "Data purchase successful" if status_flag == "success" else "Data purchase failed",
            "reference": reference,
            "amount": float(amount),
            "wallet_balance": float(wallet.balance),
        })


# --------------------------------------------------
# PURCHASE AIRTIME
# --------------------------------------------------
class PurchaseAirtimeView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):

        network = request.data.get("network")
        phone = request.data.get("phone")
        amount = request.data.get("amount")

        if not network or not phone or not amount:
            return Response(
                {"error": "network, phone and amount are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        amount = Decimal(amount)

        wallet = Wallet.objects.select_for_update().get(user=request.user)

        if wallet.balance < amount:
            return Response(
                {"error": "Insufficient wallet balance"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        wallet.balance -= amount
        wallet.save(update_fields=["balance"])

        try:
            response, reference = purchase_airtime(
                phone=phone,
                network=network,
                amount=float(amount),
            )

            status_flag = "success"

        except Exception as e:
            status_flag = "failed"
            response = {"error": str(e)}
            reference = str(uuid.uuid4())

        UtilityTransaction.objects.create(
            user=request.user,
            wallet=wallet,
            transaction_type="airtime",
            network=network,
            phone_number=phone,
            amount=amount,
            reference=reference,
            status=status_flag,
            provider_response=response,
        )

        return Response({
            "message": "Airtime purchase successful" if status_flag == "success" else "Airtime purchase failed",
            "reference": reference,
            "wallet_balance": float(wallet.balance),
        })
