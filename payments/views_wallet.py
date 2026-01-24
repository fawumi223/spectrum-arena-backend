from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.db import transaction
from django.utils.crypto import get_random_string

from .models import Wallet


class InitNUBANView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        wallet = Wallet.objects.select_for_update().get(user=request.user)

        if wallet.nuban_account_number:
            return Response(
                {
                    "message": "Wallet already activated",
                    "account_number": wallet.nuban_account_number,
                    "account_name": wallet.nuban_account_name,
                },
                status=status.HTTP_200_OK,
            )

        # ---- SIMULATE PROVIDUS NUBAN GENERATION FOR NOW ----
        wallet.nuban_account_number = "23" + get_random_string(8, allowed_chars="0123456789")
        wallet.nuban_account_name = request.user.full_name.upper()
        wallet.providus_customer_id = f"CUST-{wallet.user_id}"
        wallet.providus_ref = f"REF-{get_random_string(10)}"
        wallet.save()

        return Response(
            {
                "message": "Wallet activated successfully",
                "account_number": wallet.nuban_account_number,
                "account_name": wallet.nuban_account_name,
            },
            status=status.HTTP_201_CREATED,
        )

