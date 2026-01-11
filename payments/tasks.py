from celery import shared_task
from django.utils import timezone
from django.db import transaction

from .models import SavingsPlan


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def unlock_savings_plan(self, savings_id):
    try:
        with transaction.atomic():
            savings = SavingsPlan.objects.select_for_update().get(id=savings_id)

            if savings.status != "locked":
                return "Already unlocked"

            if timezone.now() < savings.locked_until:
                return "Too early to unlock"

            wallet = savings.wallet

            # 🔓 RELEASE FUNDS
            wallet.locked_balance -= savings.amount
            wallet.balance += savings.amount
            wallet.save(update_fields=["balance", "locked_balance"])

            savings.status = "unlocked"
            savings.unlocked_at = timezone.now()
            savings.save(update_fields=["status", "unlocked_at"])

            return "Unlocked successfully"

    except SavingsPlan.DoesNotExist:
        return "Savings plan not found"

