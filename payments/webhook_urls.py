from django.urls import path
from .views_webhook import paystack_webhook, simulate_webhook

urlpatterns = [
    path("paystack/", paystack_webhook, name="paystack-webhook"),
    path("paystack/simulate/", simulate_webhook, name="paystack-webhook-simulate"),
]

