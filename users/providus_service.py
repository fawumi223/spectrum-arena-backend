import requests
from django.conf import settings

def create_providus_payment_reference(amount, customer_name, customer_email):
    """
    Simulate creating a payment reference with Providus.
    Replace with real API later.
    """
    # ---- SIMULATION MODE ----
    print("⚙️ Simulating Providus payment initialization...")
    fake_response = {
        "status": "success",
        "data": {
            "reference": "TXN123456789",
            "payment_link": f"https://sandbox.providusbank.com/pay/TXN123456789",
            "amount": amount,
            "customer": {
                "name": customer_name,
                "email": customer_email
            }
        }
    }
    return fake_response["data"]

    # ---- REAL PROVIDUS REQUEST (for later use) ----
    # url = f"{settings.PROVIDUS_BASE_URL}/v1/payments/initiate"
    # headers = {
    #     "Authorization": f"Bearer {settings.PROVIDUS_API_KEY}",
    #     "Content-Type": "application/json"
    # }
    # payload = {
    #     "amount": str(amount),
    #     "currency": "NGN",
    #     "customer": {
    #         "name": customer_name,
    #         "email": customer_email
    #     },
    #     "callback_url": "https://yourdomain.com/api/users/providus-webhook/"
    # }
    # response = requests.post(url, json=payload, headers=headers)
    # if response.status_code == 200:
    #     return response.json().get("data", {})
    # else:
    #     print("Providus error:", response.text)
    #     return None

