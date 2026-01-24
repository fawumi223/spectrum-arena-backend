from django.urls import path

from .views import (
    SavedCardsView,
    InitWalletFundingView,
    InitSavingsFundingView,
    ChargeSavedCardView,
    CreateSavingsPlanView,
    WithdrawSavingsView,
)

from .views_webhook import paystack_webhook
from .views_wallet import InitNUBANView   # ⭐ NEW IMPORT


urlpatterns = [
    # --------------------------------------------
    # Saved cards
    # --------------------------------------------
    path("saved-cards/", SavedCardsView.as_view(), name="saved-cards"),

    # --------------------------------------------
    # First-time funding (Paystack hosted page)
    # --------------------------------------------
    path("init-wallet-funding/", InitWalletFundingView.as_view(), name="init-wallet-funding"),
    path("init-savings-funding/", InitSavingsFundingView.as_view(), name="init-savings-funding"),

    # --------------------------------------------
    # Savings / Thrift
    # --------------------------------------------
    path("savings/create/", CreateSavingsPlanView.as_view(), name="savings-create"),
    path("savings/<int:savings_id>/withdraw/", WithdrawSavingsView.as_view(), name="savings-withdraw"),

    # --------------------------------------------
    # Repeat funding (saved card)
    # --------------------------------------------
    path("charge-card/", ChargeSavedCardView.as_view(), name="charge-card"),

    # --------------------------------------------
    # Wallet → Generate Providus NUBAN (virtual account)
    # --------------------------------------------
    path("wallet/init-nuban/", InitNUBANView.as_view(), name="init-nuban"),  # ⭐ NEW ROUTE

    # --------------------------------------------
    # Webhooks (NO AUTH, PAYSTACK ONLY)
    # --------------------------------------------
    path("webhooks/paystack/", paystack_webhook, name="paystack-webhook"),
]

