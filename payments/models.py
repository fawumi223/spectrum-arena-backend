from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


# --------------------------------------------------
# WALLET (AUTO-CREATED AFTER OTP VERIFICATION)
# --------------------------------------------------
class Wallet(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="wallet",
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    locked_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wallet({self.user})"


# --------------------------------------------------
# SAVED CARD (WITH FAILURE TRACKING)
# --------------------------------------------------
class SavedCard(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_cards",
    )

    authorization_code = models.CharField(max_length=255, unique=True)

    card_type = models.CharField(max_length=50)
    last4 = models.CharField(max_length=4)
    exp_month = models.CharField(max_length=2)
    exp_year = models.CharField(max_length=4)
    bank = models.CharField(max_length=100)

    reusable = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    failed_attempts = models.PositiveSmallIntegerField(default=0)
    last_failed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} • ****{self.last4}"


# --------------------------------------------------
# IDEMPOTENCY KEYS
# --------------------------------------------------
class IdempotencyKey(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="idempotency_keys",
    )
    key = models.CharField(max_length=100)
    endpoint = models.CharField(max_length=100)
    response = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "key", "endpoint")

    def __str__(self):
        return f"{self.user} • {self.endpoint} • {self.key}"


# --------------------------------------------------
# SAVINGS / THRIFT PLAN (LEDGER-LOCKED)
# --------------------------------------------------
class SavingsPlan(models.Model):
    PLAN_TYPES = (
        ("SAVINGS", "Savings"),
        ("THRIFT", "Thrift"),
    )

    STATUS_CHOICES = (
        ("locked", "Locked"),
        ("unlocked", "Unlocked"),
        ("broken", "Broken Early"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="savings_plans",
    )

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="savings_plans",
    )

    plan_type = models.CharField(
        max_length=20,
        choices=PLAN_TYPES,
        default="SAVINGS",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="locked",
    )

    locked_at = models.DateTimeField(auto_now_add=True)
    locked_until = models.DateTimeField()

    unlocked_at = models.DateTimeField(null=True, blank=True)
    broken_at = models.DateTimeField(null=True, blank=True)

    penalty_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plan_type} • {self.amount} • {self.user}"

