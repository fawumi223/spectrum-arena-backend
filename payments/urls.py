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


urlpatterns = [
    # --------------------------------------------
    # Saved cards
    # --------------------------------------------
    path("saved-cards/", SavedCardsView.as_view()),

    # --------------------------------------------
    # First-time funding (Paystack hosted page)
    # --------------------------------------------
    path("init-wallet-funding/", InitWalletFundingView.as_view()),
    path("init-savings-funding/", InitSavingsFundingView.as_view()),

    # --------------------------------------------
    # Savings / Thrift
    # --------------------------------------------
    path("savings/create/", CreateSavingsPlanView.as_view()),
    path(
        "savings/<int:savings_id>/withdraw/",
        WithdrawSavingsView.as_view(),
    ),

    # --------------------------------------------
    # Repeat funding (saved card)
    # --------------------------------------------
    path("charge-card/", ChargeSavedCardView.as_view()),

    # --------------------------------------------
    # Webhooks (NO AUTH, PAYSTACK ONLY)
    # --------------------------------------------
    path("webhooks/paystack/", paystack_webhook),
]

