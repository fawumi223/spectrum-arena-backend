import hashlib
import hmac
import json
from decimal import Decimal

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from users.models import User, PaystackTransaction
from savings.models import Savings
from payments.models import SavedCard


@csrf_exempt
def paystack_webhook(request):
    # --------------------------------------------------
    # 1. VERIFY PAYSTACK SIGNATURE
    # --------------------------------------------------
    signature = request.headers.get("X-Paystack-Signature")
    body = request.body

    computed_signature = hmac.new(
        key=settings.PAYSTACK_SECRET_KEY.encode(),
        msg=body,
        digestmod=hashlib.sha512,
    ).hexdigest()

    if signature != computed_signature:
        return HttpResponse(status=401)

    payload = json.loads(body)
    event = payload.get("event")
    data = payload.get("data", {})

    # --------------------------------------------------
    # 2. PROCESS ONLY SUCCESSFUL CHARGES
    # --------------------------------------------------
    if event != "charge.success":
        return HttpResponse(status=200)

    reference = data.get("reference")
    amount = Decimal(data.get("amount", 0)) / 100  # kobo → naira

    customer = data.get("customer", {})
    email = customer.get("email")

    metadata = data.get("metadata", {})
    payment_type = metadata.get("payment_type")
    savings_id = metadata.get("savings_id")

    authorization = data.get("authorization")

    # --------------------------------------------------
    # 3. RESOLVE USER
    # --------------------------------------------------
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Never fail webhook retries
        return HttpResponse(status=200)

    # --------------------------------------------------
    # 4. IDEMPOTENCY CHECK (CRITICAL)
    # --------------------------------------------------
    if PaystackTransaction.objects.filter(reference=reference).exists():
        return HttpResponse(status=200)

    # --------------------------------------------------
    # 5. ATOMIC TRANSACTION (ALL OR NOTHING)
    # --------------------------------------------------
    with transaction.atomic():

        # ----------------------------------------------
        # RECORD PAYSTACK TRANSACTION
        # ----------------------------------------------
        PaystackTransaction.objects.create(
            user=user,
            reference=reference,
            amount=amount,
            payment_type=payment_type,
            status="success",
            raw_payload=payload,
        )

        # ----------------------------------------------
        # SAVE CARD (REUSABLE AUTHORIZATION)
        # ----------------------------------------------
        if authorization and authorization.get("reusable"):
            SavedCard.objects.get_or_create(
                authorization_code=authorization.get("authorization_code"),
                defaults={
                    "user": user,
                    "card_type": authorization.get("card_type"),
                    "last4": authorization.get("last4"),
                    "exp_month": authorization.get("exp_month"),
                    "exp_year": authorization.get("exp_year"),
                    "bank": authorization.get("bank"),
                    "reusable": True,
                    "is_active": True,
                },
            )

        # ----------------------------------------------
        # SAVINGS FUNDING
        # ----------------------------------------------
        if payment_type == "savings" and savings_id:
            try:
                savings = Savings.objects.select_for_update().get(
                    id=savings_id,
                    user=user,
                )
                savings.balance += amount
                savings.save(update_fields=["balance"])
            except Savings.DoesNotExist:
                # Never break webhook
                pass

        # ----------------------------------------------
        # WALLET FUNDING
        # ----------------------------------------------
        elif payment_type == "wallet":
            user.wallet_balance += amount
            user.save(update_fields=["wallet_balance"])

    # --------------------------------------------------
    # 6. ACKNOWLEDGE WEBHOOK
    # --------------------------------------------------
    return HttpResponse(status=200)

