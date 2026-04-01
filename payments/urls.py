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

# Utility APIs
from .views_utilities import (
    DataBundleListView,
    PurchaseDataView,
    PurchaseAirtimeView,
)


urlpatterns = [
    # --------------------------------------------------
    # CARDS
    # --------------------------------------------------
    path("saved-cards/", SavedCardsView.as_view(), name="saved-cards"),

    # --------------------------------------------------
    # WALLET / FUNDING
    # --------------------------------------------------
    path(
        "init-wallet-funding/",
        InitWalletFundingView.as_view(),
        name="init-wallet-funding",
    ),

    path(
        "wallet/init-nuban/",
        InitNUBANView.as_view(),
        name="init-nuban",
    ),

    path(
        "wallet/me/",
        wallet_me,
        name="wallet-me",
    ),

    # --------------------------------------------------
    # SAVINGS
    # --------------------------------------------------
    path(
        "savings/create/",
        CreateSavingsPlanView.as_view(),
        name="savings-create",
    ),

    path(
        "savings/<int:savings_id>/withdraw/",
        WithdrawSavingsView.as_view(),
        name="savings-withdraw",
    ),

    # --------------------------------------------------
    # DATA / UTILITIES
    # --------------------------------------------------
    path(
        "data/bundles/",
        DataBundleListView.as_view(),
        name="data-bundles",
    ),

    path(
        "data/purchase/",
        PurchaseDataView.as_view(),
        name="data-purchase",
    ),

    path(
        "airtime/purchase/",
        PurchaseAirtimeView.as_view(),
        name="airtime-purchase",
    ),

    # --------------------------------------------------
    # WEBHOOKS
    # --------------------------------------------------
    path(
        "webhooks/paystack/",
        paystack_webhook,
        name="paystack-webhook",
    ),

    path(
        "webhooks/simulate/",
        simulate_webhook,
        name="simulate-webhook",
    ),
]
