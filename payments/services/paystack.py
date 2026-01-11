import requests
from django.conf import settings

PAYSTACK_BASE_URL = "https://api.paystack.co"

def charge_authorization(*, email, amount, authorization_code):
    url = f"{PAYSTACK_BASE_URL}/transaction/charge_authorization"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "email": email,
        "amount": int(amount),  # already in kobo
        "authorization_code": authorization_code,
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    return response.json()

