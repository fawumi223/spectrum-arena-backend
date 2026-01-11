from django.conf import settings
from django.db import models
from datetime import date
from django.utils import timezone
from decimal import Decimal


# ============================================================
#                     SAVINGS MODEL
# ============================================================
class Savings(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="savings"
    )

    # Main savings balance
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    # User-selected unlock date
    locked_until = models.DateField()

    is_released = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    released_at = models.DateTimeField(null=True, blank=True)

    # ---------------------------------------------------------
    # INTEREST ENGINE (H22)
    # ---------------------------------------------------------
    interest_rate = models.FloatField(default=0.05)  # 5% yearly interest
    last_interest_applied = models.DateTimeField(auto_now_add=True)
    interest_earned = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )

    # ---------------------------------------------------------
    # SAVINGS GOAL SYSTEM (H23)
    # ---------------------------------------------------------
    target_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    goal_completed = models.BooleanField(default=False)

    # ---------------------------------------------------------
    # METHODS
    # ---------------------------------------------------------
    def can_withdraw(self):
        return date.today() >= self.locked_until or self.is_released

    def __str__(self):
        return f"{self.user} - ₦{self.amount} locked until {self.locked_until}"


# ============================================================
#             TRANSACTIONS MODEL (DEPOSIT / WITHDRAWAL)
# ============================================================
class SavingsTransaction(models.Model):
    savings = models.ForeignKey(
        Savings,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    type = models.CharField(max_length=20)   # deposit / withdrawal / release
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} ₦{self.amount} ({self.created_at.date()})"


# ============================================================
#                OTP MODEL FOR SECURE WITHDRAWALS
# ============================================================
class SavingsOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    savings = models.ForeignKey(Savings, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP {self.code} for {self.user}"

