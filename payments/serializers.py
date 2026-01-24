from rest_framework import serializers
from django.utils import timezone
from .models import SavedCard, Wallet, SavingsPlan


# --------------------------------------------------
# SAVED CARD
# --------------------------------------------------
class SavedCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedCard
        fields = [
            "id",
            "card_type",
            "last4",
            "exp_month",
            "exp_year",
            "bank",
            "reusable",
            "created_at",
        ]


# --------------------------------------------------
# SAVINGS / THRIFT CREATION (USER INPUT)
# --------------------------------------------------
class SavingsPlanCreateSerializer(serializers.Serializer):
    PLAN_CHOICES = ["SAVINGS", "THRIFT"]

    plan_type = serializers.ChoiceField(choices=PLAN_CHOICES)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    duration_days = serializers.IntegerField(min_value=1)

    def validate_amount(self, value):
        wallet = self.context["wallet"]

        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")

        if wallet.balance < value:
            raise serializers.ValidationError("Insufficient wallet balance.")

        return value

    def create(self, validated_data):
        wallet = self.context["wallet"]
        amount = validated_data["amount"]
        duration_days = validated_data["duration_days"]
        plan_type = validated_data["plan_type"]

        locked_until = timezone.now() + timezone.timedelta(days=duration_days)

        # 🔒 LOCK FUNDS
        wallet.balance -= amount
        wallet.locked_balance += amount
        wallet.save(update_fields=["balance", "locked_balance"])

        savings = SavingsPlan.objects.create(
            user=wallet.user,
            wallet=wallet,
            plan_type=plan_type,
            amount=amount,
            locked_until=locked_until,
            status="locked",
        )

        return savings


# --------------------------------------------------
# SAVINGS WITHDRAWAL (RULES + EARLY BREAK)
# --------------------------------------------------
class SavingsWithdrawSerializer(serializers.Serializer):
    early_break = serializers.BooleanField(default=False)

    def validate(self, data):
        savings = self.context["savings"]

        if savings.status not in ["locked", "unlocked"]:
            raise serializers.ValidationError("Savings not withdrawable.")

        if savings.status == "locked" and not data.get("early_break"):
            raise serializers.ValidationError(
                "Savings is locked. Enable early_break to withdraw."
            )

        return data

