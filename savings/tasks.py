from celery import shared_task
from django.utils import timezone
from decimal import Decimal

@shared_task
def check_and_unlock_thrifts():
    """
    Run daily: unlock thrifts where:
    - withdraw_date <= today OR
    - target_amount set and current_amount >= target_amount
    When unlocking, mark is_unlocked True and create release transaction.
    """
    today = timezone.now().date()
    thrifts = Thrift.objects.filter(is_unlocked=False).filter(
        models.Q(withdraw_date__lte=today) |
        models.Q(target_amount__isnull=False, target_amount__lte=models.F('current_amount'))
    )

    unlocked_count = 0
    for t in thrifts:
        t.is_unlocked = True
        t.save()
        ThriftTransaction.objects.create(
            thrift=t,
            type="release",
            amount=t.current_amount,
            note="Auto-release by scheduler"
        )
        unlocked_count += 1

    return {"unlocked": unlocked_count}

