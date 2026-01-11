from django.urls import path

# Existing Paystack webhook
from users.views_paystack import paystack_webhook

# Auth / onboarding views
from .views import (
    SignupView,
    VerifyOTPView,
    ResendOTPView,
    LoginView,
)

urlpatterns = [
    # ---------------------------------------------------------------------
    # AUTH / ONBOARDING
    # ---------------------------------------------------------------------
    path("signup/", SignupView.as_view(), name="signup"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("resend-otp/", ResendOTPView.as_view(), name="resend-otp"),
    path("login/", LoginView.as_view(), name="login"),

    # ---------------------------------------------------------------------
    # PAYSTACK WEBHOOK (wallet, savings, utilities)
    # ---------------------------------------------------------------------
    path("webhooks/paystack/", paystack_webhook, name="paystack-webhook"),
]

