from decimal import Decimal
from django.db import transaction

from .models import Wallet, SavingsPlan, IdempotencyKey


@transaction.atomic
def handle_successful_payment(data):
    """
    This function is called ONLY after Paystack confirms payment success.
    It must be idempotent and atomic.
    """

    reference = data.get("reference")
    metadata = data.get("metadata", {}) or {}

    payment_type = metadata.get("payment_type")
    user_id = metadata.get("user_id")
    savings_id = metadata.get("savings_id")

    # ------------------------------
    # IDEMPOTENCY GUARD (webhook-level)
    # ------------------------------
    if IdempotencyKey.objects.filter(
        key=reference,
        endpoint="paystack-webhook",
    ).exists():
        return  # already processed

    amount = Decimal(data["amount"]) / Decimal("100")

    # ------------------------------
    # CREDIT LOGIC
    # ------------------------------
    wallet = Wallet.objects.select_for_update().get(user_id=user_id)

    if payment_type == "wallet":
        wallet.balance += amount
        wallet.save(update_fields=["balance"])

    elif payment_type == "savings" and savings_id:
        savings = SavingsPlan.objects.select_for_update().get(id=savings_id)

        # savings.amount grows ONLY from confirmed payments
        savings.amount += amount
        savings.save(update_fields=["amount"])

    # ------------------------------
    # SAVE IDEMPOTENCY RECORD
    # ------------------------------
    IdempotencyKey.objects.create(
        user_id=user_id,
        key=reference,
        endpoint="paystack-webhook",
        response={"status": "credited"},
    )

