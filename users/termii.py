import requests
from django.conf import settings

TERMII_TOKEN_URL = f"{settings.TERMII_BASE_URL}/api/sms/otp/send"

def send_termii_sms(phone, otp):
    payload = {
        "api_key": settings.TERMII_API_KEY,
        "to": phone,
        "from": "N-Alert",
        "channel": "dnd",
        "pin_type": "NUMERIC",
        "pin_length": 6,
        "pin_time_to_live": 10,
        "pin_attempts": 10,
        "pin_placeholder": "<OTP>",
        "message_type": "NUMERIC",
        "message_text": f"Your Spectrum OTP is <OTP>. It expires in 10 minutes.",
    }

    try:
        response = requests.post(TERMII_TOKEN_URL, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "http_error": str(e),
            "response": e.response.text
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

