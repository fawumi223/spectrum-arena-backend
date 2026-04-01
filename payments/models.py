from django.db import models
from django.conf import settings
from django.utils import timezone

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

    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    locked_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # PROVIDUS VIRTUAL ACCOUNT FIELDS
    nuban_account_number = models.CharField(max_length=20, blank=True, null=True)
    nuban_account_name = models.CharField(max_length=100, blank=True, null=True)
    providus_customer_id = models.CharField(max_length=100, blank=True, null=True)
    providus_ref = models.CharField(max_length=100, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wallet({self.user})"


# --------------------------------------------------
# SAVED CARD
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
# SAVINGS / THRIFT PLAN
# --------------------------------------------------
class SavingsPlan(models.Model):
    PLAN_TYPES = (("SAVINGS", "Savings"), ("THRIFT", "Thrift"))
    STATUS_CHOICES = (
        ("locked", "Locked"),
        ("unlocked", "Unlocked"),
        ("broken", "Broken Early"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="savings_plans")
    wallet = models.ForeignKey("Wallet", on_delete=models.CASCADE, related_name="savings_plans")

    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, default="SAVINGS")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="locked")

    locked_at = models.DateTimeField(auto_now_add=True)
    locked_until = models.DateTimeField()
    unlocked_at = models.DateTimeField(null=True, blank=True)
    broken_at = models.DateTimeField(null=True, blank=True)
    penalty_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plan_type} • {self.amount} • {self.user}"


# --------------------------------------------------
# PAYSTACK TRANSACTIONS (WEBHOOK LEDGER)
# --------------------------------------------------
class PaystackTransaction(models.Model):
    STATUS_CHOICES = (
        ("success", "Success"),
        ("failed", "Failed"),
        ("pending", "Pending"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="paystack_txns",
        null=True,
        blank=True
    )
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_type = models.CharField(max_length=50, default="wallet")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="success")
    raw_payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} • {self.status}"

# --------------------------------------------------
# DATA BUNDLES (VTU PRODUCTS)
# --------------------------------------------------
class DataBundle(models.Model):
    NETWORK_CHOICES = (
        ("mtn", "MTN"),
        ("airtel", "Airtel"),
        ("glo", "Glo"),
        ("9mobile", "9Mobile"),
    )

    CATEGORY_CHOICES = (
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("social", "Social"),
        ("broadband", "Broadband"),
    )

    network = models.CharField(max_length=20, choices=NETWORK_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    name = models.CharField(max_length=100)
    volume = models.CharField(max_length=50)
    validity = models.CharField(max_length=50)

    provider_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    vtpass_code = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def display_price(self):
        return self.selling_price

    def __str__(self):
        return f"{self.network} • {self.volume} • ₦{self.selling_price}"


# --------------------------------------------------
# UTILITY TRANSACTIONS (AIRTIME / DATA / BILLS)
# --------------------------------------------------
class UtilityTransaction(models.Model):
    TYPE_CHOICES = (
        ("airtime", "Airtime"),
        ("data", "Data"),
        ("electricity", "Electricity"),
    )

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="utility_transactions"
    )

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="utility_transactions"
    )

    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    network = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20)

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    reference = models.CharField(max_length=120, unique=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    provider_response = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} • ₦{self.amount} • {self.status}"
