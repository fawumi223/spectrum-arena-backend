from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from .managers import UserManager
import random
from datetime import timedelta


# -------------------------------------------------------------------------
# Custom User Model
# -------------------------------------------------------------------------
class User(AbstractUser):
    username = None  # Disable username
    full_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True)

    # ---------------------------------------------------------------------
    # ROLE SYSTEM (UPPERCASE)
    # ---------------------------------------------------------------------
    ROLE_CHOICES = [
        ("CLIENT", "Client"),
        ("ARTISAN", "Artisan"),
        ("COMPANY", "Company"),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="CLIENT"
    )

    # OTP & Verification
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    OTP_CHANNEL_CHOICES = [
        ("EMAIL", "Email"),
        ("PHONE", "Phone"),
    ]
    otp_channel = models.CharField(
        max_length=10,
        choices=OTP_CHANNEL_CHOICES,
        blank=True,
        null=True,
    )

    is_verified = models.BooleanField(default=False)

    # Plans
    PLAN_CHOICES = [
        ("BASIC", "Basic"),
        ("STANDARD", "Standard"),
        ("PREMIUM", "Premium"),
    ]
    plan_type = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default="BASIC",
    )
    job_post_limit = models.PositiveIntegerField(default=3)

    date_joined = models.DateTimeField(default=timezone.now)
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"

    # OTP Logic
    def generate_otp(self, channel="PHONE"):
        otp = str(random.randint(100000, 999999)).zfill(6)
        self.otp = otp
        self.otp_created_at = timezone.now()
        self.otp_channel = channel
        self.save(update_fields=["otp", "otp_created_at", "otp_channel"])
        return otp

    def otp_is_expired(self, expiry_minutes=10):
        if not self.otp_created_at:
            return True
        return timezone.now() > self.otp_created_at + timedelta(minutes=expiry_minutes)

    # Plan upgrade
    def update_plan(self, new_plan):
        plan_map = {
            "BASIC": 3,
            "STANDARD": 10,
            "PREMIUM": 25,
        }
        new_plan = new_plan.upper()
        if new_plan not in plan_map:
            raise ValueError("Invalid plan type.")
        self.plan_type = new_plan
        self.job_post_limit = plan_map[new_plan]
        self.save(update_fields=["plan_type", "job_post_limit"])


# -------------------------------------------------------------------------
# Transaction Model (Providus / Plan Payments)
# -------------------------------------------------------------------------
class Transaction(models.Model):
    PLAN_CHOICES = [
        ("STANDARD", "Standard"),
        ("PREMIUM", "Premium"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"{self.user} - {self.plan_type} - {self.status}"


# -------------------------------------------------------------------------
# Paystack Transaction Model (Wallet / Savings / Utilities)
# -------------------------------------------------------------------------
class PaystackTransaction(models.Model):
    STATUS_CHOICES = [
        ("success", "Success"),
        ("failed", "Failed"),
        ("pending", "Pending"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="paystack_transactions",
    )
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_type = models.CharField(max_length=50)  # wallet | savings | utility
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    raw_payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Paystack Transaction"
        verbose_name_plural = "Paystack Transactions"

    def __str__(self):
        return f"{self.reference} ({self.status})"

