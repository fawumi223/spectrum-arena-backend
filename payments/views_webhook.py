import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .webhooks import handle_successful_payment

@csrf_exempt
def paystack_webhook(request):
    payload = json.loads(request.body.decode("utf-8"))
    event = payload.get("event")
    data = payload.get("data", {})

    if event == "charge.success":
        handle_successful_payment(data)

    return HttpResponse(status=200)

