import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .webhooks import handle_successful_payment


@csrf_exempt
def paystack_webhook(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponse(status=400)

    event = payload.get("event")
    data = payload.get("data", {})

    if event == "charge.success":
        handle_successful_payment(data)

    return HttpResponse(status=200)


# --------------------------------------------------
# SIMULATE PAYSTACK SUCCESS (CTO TEST BUTTON)
# --------------------------------------------------
@csrf_exempt
def simulate_webhook(request):
    """
    TEST ONLY — simulate Paystack webhook.
    """
    fake_data = {
        "reference": "TEST-SIMULATED-REF",
        "amount": 5000 * 100,  # kobo
        "customer": {
            "email": "demo@spectrum.ng"
        },
    }
    handle_successful_payment(fake_data)
    return HttpResponse("Simulated webhook event processed.", status=200)

