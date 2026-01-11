from django.core.mail import send_mail
from django.conf import settings

def send_email_otp(user):
    """
    Send OTP email to user.
    Sender name will appear as: Spectrum Arena
    """

    if not user.email:
        return False

    otp = user.otp  # Use the OTP stored on the user

    subject = "Spectrum Arena Verification Code"

    message = (
        f"Hello {user.full_name},\n\n"
        f"Your Spectrum Arena verification code is:\n\n"
        f"{otp}\n\n"
        "This code expires in 10 minutes.\n\n"
        "If you did not request this, please ignore this email.\n\n"
        "— Spectrum Arena"
    )

    from_email = f"Spectrum Arena <{settings.DEFAULT_FROM_EMAIL}>"

    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=[user.email],
        fail_silently=False,
    )

    return True

