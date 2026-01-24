from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Wallet


@extend_schema(
    responses={201: OpenApiResponse(description="Virtual account activated")},
    tags=["Wallet"],
)
class InitNUBANView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        wallet = Wallet.objects.select_for_update().get(user=request.user)

        if wallet.nuban_account_number:
            return Response({
                "message": "Wallet already activated",
                "account_number": wallet.nuban_account_number,
                "account_name": wallet.nuban_account_name,
            }, status=200)

        # PROVIDUS SIMULATION
        from django.utils.crypto import get_random_string
        wallet.nuban_account_number = "23" + get_random_string(8, allowed_chars="0123456789")
        wallet.nuban_account_name = request.user.full_name.upper()
        wallet.providus_customer_id = f"CUST-{wallet.user_id}"
        wallet.providus_ref = f"REF-{get_random_string(10)}"
        wallet.save()

        return Response({
            "message": "Wallet activated successfully",
            "account_number": wallet.nuban_account_number,
            "account_name": wallet.nuban_account_name,
        }, status=201)

