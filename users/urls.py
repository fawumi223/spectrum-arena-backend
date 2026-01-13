from django.urls import path

# Existing Paystack webhook
from users.views_paystack import paystack_webhook

# Auth / onboarding views (temporary no-OTP mode)
from .views import (
    SignupView,
    VerifyView,
    LoginView,
)

urlpatterns = [
    # ---------------------------------------------------------------------
    # AUTH / ONBOARDING (OTP BYPASSED FOR DEMO)
    # ---------------------------------------------------------------------
    path("signup/", SignupView.as_view(), name="signup"),
    path("verify/", VerifyView.as_view(), name="verify"),
    path("login/", LoginView.as_view(), name="login"),

    # ---------------------------------------------------------------------
    # PAYSTACK WEBHOOK (wallet, savings, utilities)
    # ---------------------------------------------------------------------
    path("webhooks/paystack/", paystack_webhook, name="paystack-webhook"),
]

