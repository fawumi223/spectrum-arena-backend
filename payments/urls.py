from django.urls import path

from .views import (
    SavedCardsView,
    InitWalletFundingView,
    CreateSavingsPlanView,
    WithdrawSavingsView,
    wallet_me,
)
from .views_wallet import InitNUBANView
from .views_webhook import paystack_webhook, simulate_webhook


urlpatterns = [
    # Cards
    path("saved-cards/", SavedCardsView.as_view(), name="saved-cards"),

    # Wallet / Funding
    path("init-wallet-funding/", InitWalletFundingView.as_view(), name="init-wallet-funding"),
    path("wallet/init-nuban/", InitNUBANView.as_view(), name="init-nuban"),
    path("wallet/me/", wallet_me, name="wallet-me"),

    # Savings
    path("savings/create/", CreateSavingsPlanView.as_view(), name="savings-create"),
    path("savings/<int:savings_id>/withdraw/", WithdrawSavingsView.as_view(), name="savings-withdraw"),

    # Webhooks
    path("webhooks/paystack/", paystack_webhook, name="paystack-webhook"),
    path("webhooks/simulate/", simulate_webhook, name="simulate-webhook"),
]

