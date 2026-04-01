import requests
import uuid
from django.conf import settings


# --------------------------------------------------
# VTPASS BASE URL
# --------------------------------------------------
VTPASS_BASE_URL = "https://api-service.vtpass.com/api/pay"


# --------------------------------------------------
# PURCHASE DATA BUNDLE
# --------------------------------------------------
def purchase_data(phone, service_id, billers_code, variation_code, amount):

    reference = str(uuid.uuid4())

    payload = {
        "request_id": reference,
        "serviceID": service_id,
        "billersCode": billers_code,
        "variation_code": variation_code,
        "amount": amount,
        "phone": phone,
    }

    response = requests.post(
        VTPASS_BASE_URL,
        json=payload,
        auth=(settings.VTPASS_EMAIL, settings.VTPASS_API_KEY),
    )

    return response.json(), reference


# --------------------------------------------------
# PURCHASE AIRTIME
# --------------------------------------------------
def purchase_airtime(phone, network, amount):

    reference = str(uuid.uuid4())

    payload = {
        "request_id": reference,
        "serviceID": network,
        "billersCode": phone,
        "amount": amount,
        "phone": phone,
    }

    response = requests.post(
        VTPASS_BASE_URL,
        json=payload,
        auth=(settings.VTPASS_EMAIL, settings.VTPASS_API_KEY),
    )

    return response.json(), reference
