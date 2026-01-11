from rest_framework import serializers
from .models import Savings, SavingsTransaction, SavingsOTP


# ------------------------------------------------------------
# Transaction Serializer
# ------------------------------------------------------------
class SavingsTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsTransaction
        fields = [
            "id",
            "type",
            "amount",
            "note",
            "created_at",
        ]


# ------------------------------------------------------------
# Savings Serializer
# ------------------------------------------------------------
class SavingsSerializer(serializers.ModelSerializer):
    # List all transaction history
    transactions = SavingsTransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Savings
        fields = [
            "id",
            "amount",
            "locked_until",
            "is_released",
            "created_at",
            "released_at",
            "transactions",
        ]


# ------------------------------------------------------------
# OTP Serializer (Optional)
# ------------------------------------------------------------
class SavingsOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsOTP
        fields = ["id", "code", "created_at", "is_used"]

