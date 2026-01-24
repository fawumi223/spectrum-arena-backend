from decimal import Decimal
from django.utils import timezone

from .models import PaystackTransaction, Wallet, SavingsPlan


def handle_successful_payment(data):
    """
    Handles Paystack charge.success webhook events.
    Supports:
    - Wallet top-up
    - Savings funding (future use)
    """

    reference = data.get("reference")
    amount_kobo = data.get("amount")
    metadata = data.get("metadata", {})

    user_id = metadata.get("user_id")
    payment_type = metadata.get("payment_type", "wallet")
    savings_id = metadata.get("savings_id")

    # Convert Paystack amount (kobo -> naira)
    amount = Decimal(amount_kobo) / 100

    # Prevent duplicate webhook processing
    trx, created = PaystackTransaction.objects.get_or_create(
        reference=reference,
        defaults={
            "user_id": user_id,
            "payment_type": payment_type,
            "amount": amount,
            "status": "success",
            "raw_payload": data,
        }
    )

    if not created:
        # Already processed
        return

    # -------------------------------------------
    # WALLET FUNDING
    # -------------------------------------------
    if payment_type == "wallet":
        try:
            wallet = Wallet.objects.get(user_id=user_id)
        except Wallet.DoesNotExist:
            return  # user deleted or inconsistency

        wallet.balance += amount
        wallet.save(update_fields=["balance"])

    # -------------------------------------------
    # SAVINGS FUNDING (OPTIONAL FUTURE USE)
    # -------------------------------------------
    elif payment_type == "savings" and savings_id:
        try:
            savings = SavingsPlan.objects.get(id=savings_id, wallet__user_id=user_id)
        except SavingsPlan.DoesNotExist:
            return

        savings.status = "locked"
        savings.locked_at = timezone.now()
        savings.amount = amount
        savings.save(update_fields=["status", "locked_at", "amount"])

    # -------------------------------------------
    # NOTHING ELSE TO HANDLE
    # -------------------------------------------
    return

