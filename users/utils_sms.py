import requests
import os

TERMII_API_KEY = os.getenv("TERMII_API_KEY")
TERMII_BASE_URL = os.getenv("TERMII_BASE_URL", "https://api.ng.termii.com")
TERMII_SENDER_ID = os.getenv("TERMII_SENDER_ID", "Spectrum")


def format_phone(phone):
    """Convert 07012345678 -> +2347012345678"""
    phone = phone.strip()
    if phone.startswith("+"):
        return phone
    if phone.startswith("0"):
        return "+234" + phone[1:]
    return phone


def send_sms_otp(phone_number, otp):
    if not TERMII_API_KEY:
        print("⚠️ TERMII_API_KEY not configured")
        return False

    phone = format_phone(phone_number)

    url = f"{TERMII_BASE_URL}/api/sms/send"

    payload = {
        "api_key": TERMII_API_KEY,
        "to": phone,
        "from": TERMII_SENDER_ID,
        "sms": f"Your Spectrum Arena OTP is {otp}. It expires in 10 minutes.",
        "type": "plain",
        "channel": "generic"
    }

    try:
        resp = requests.post(url, json=payload)
        data = resp.json()
        print("TERMII RESPONSE:", data)

        # Termii success check
        if resp.status_code == 200 and data.get("message", "").lower() == "message sent":
            return True

        return False

    except Exception as e:
        print("❌ Termii SMS Error:", e)
        return False

