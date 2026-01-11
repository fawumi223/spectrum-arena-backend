import random
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import SavingsOTP


# ============================================================
#                     OTP GENERATION
# ============================================================
def generate_otp(user, savings):
    """Generate a 6-digit OTP for savings withdrawal."""
    code = f"{random.randint(100000, 999999)}"

    otp = SavingsOTP.objects.create(
        user=user,
        savings=savings,
        code=code,
    )

    # Send email
    send_mail(
        subject="Spectrum Arena Savings OTP",
        message=f"Your OTP for withdrawing ₦{savings.amount} is: {code}\n\n"
                f"This OTP expires in 5 minutes.",
        from_email="no-reply@spectrumarena.com",
        recipient_list=[user.email],
        fail_silently=True,
    )

    return otp


# ============================================================
#                     OTP VERIFICATION
# ============================================================
def verify_otp(user, savings, code):
    """Check if OTP exists, matches, unused, and not expired."""
    try:
        otp = SavingsOTP.objects.get(
            user=user,
            savings=savings,
            code=code,
            is_used=False,
        )
    except SavingsOTP.DoesNotExist:
        return False, "Invalid OTP"

    # Expiration — 5 minutes validity
    if otp.created_at < timezone.now() - timedelta(minutes=5):
        return False, "OTP expired"

    # Mark as used
    otp.is_used = True
    otp.save()

    return True, "OTP verified successfully"


# ============================================================
#                     INTEREST ENGINE (H22)
# ============================================================
def apply_interest(savings):
    """
    Apply interest to a savings account based on the number
    of days since last interest calculation.
    """

    now = timezone.now()
    last = savings.last_interest_applied

    # Days passed
    days_passed = (now.date() - last.date()).days

    if days_passed <= 0:
        return savings  # No interest to apply today

    yearly_rate = Decimal(savings.interest_rate)
    daily_rate = yearly_rate / Decimal(365)

    # Interest = principal * rate * days
    interest = Decimal(savings.amount) * daily_rate * Decimal(days_passed)

    # Update savings
    savings.amount = Decimal(savings.amount) + interest
    savings.interest_earned = Decimal(savings.interest_earned) + interest
    savings.last_interest_applied = now
    savings.save()

    return savings


# ============================================================
#                     GOAL SYSTEM (H23)
# ============================================================
def update_goal_status(savings):
    """
    Check if savings amount has reached or passed target amount.
    """
    if savings.target_amount:
        if Decimal(savings.amount) >= Decimal(savings.target_amount):
            savings.goal_completed = True
        else:
            savings.goal_completed = False

        savings.save()

    return savings

