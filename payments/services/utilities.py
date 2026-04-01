import uuid
from decimal import Decimal

from django.db import transaction

from payments.models import Wallet, UtilityTransaction
from payments.vtpass_service import purchase_data


def purchase_data_bundle(user, bundle, phone):
    """
    Handles wallet deduction + VTpass data purchase.
    """

    wallet = Wallet.objects.select_for_update().get(user=user)

    amount = Decimal(bundle.selling_price)

    if wallet.balance < amount:
        raise Exception("Insufficient wallet balance")

    # Deduct wallet
    wallet.balance -= amount
    wallet.save(update_fields=["balance"])

    # Call VTpass
    response, reference = purchase_data(
        phone=phone,
        service_id=bundle.network,
        billers_code=phone,
        variation_code=bundle.vtpass_code,
        amount=float(amount),
    )

    # Save transaction
    UtilityTransaction.objects.create(
        user=user,
        wallet=wallet,
        transaction_type="data",
        network=bundle.network,
        phone_number=phone,
        amount=amount,
        reference=reference,
        status="success",
        provider_response=response,
    )

    return {
        "reference": reference,
        "amount": float(amount),
        "wallet_balance": float(wallet.balance),
    }
