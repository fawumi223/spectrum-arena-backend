from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from twilio.rest import Client


# --------------------------------------------------------
# SMS ALERTS SETUP
# --------------------------------------------------------
TWILIO_SID = settings.TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
TWILIO_PHONE = settings.TWILIO_PHONE_NUMBER

twilio_client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)


def send_sms_alert(to_number, message):
    """
    Sends an SMS alert to the user
    """
    twilio_client.messages.create(
        body=message,
        from_=TWILIO_PHONE,
        to=to_number
    )


# --------------------------------------------------------
# EMAIL ALERTS
# --------------------------------------------------------
def send_email_alert_html(subject, html_content, recipient_email, text_content=None):
    """
    Sends an HTML email with optional plain-text fallback.
    """
    text_content = text_content or "Please view this email in an HTML-compatible client."
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)


def html_template(title, body_html):
    """
    Wraps content in a branded SPECTRUM ARENA HTML template
    """
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f5f6fa; margin: 0; padding: 0;">
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td align="center">
              <table width="600" cellpadding="20" cellspacing="0" style="background-color: #111827; color: #fff; border-radius: 8px;">
                <tr>
                  <td align="center" style="font-size: 24px; font-weight: bold; color: #ff7f00;">
                    SPECTRUM ARENA
                  </td>
                </tr>
                <tr>
                  <td>
                    <h2 style="color: #ff7f00;">{title}</h2>
                    <div style="font-size: 16px; line-height: 1.5; color: #fff;">
                      {body_html}
                    </div>
                  </td>
                </tr>
                <tr>
                  <td style="font-size: 12px; color: #aaa; text-align: center;">
                    &copy; 2025 SPECTRUM ARENA. All rights reserved.
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """


# --------------------------------------------------------
# EMAIL ALERTS FUNCTIONS
# --------------------------------------------------------

def send_withdrawal_alert(user, amount):
    subject = "Withdrawal Successful – Spectrum Arena"
    body_html = f"""
    <p>Hello {user.first_name},</p>
    <p>Your withdrawal of <strong>₦{amount:,.2f}</strong> was successful.</p>
    <p>If you did not authorize this transaction, please contact support immediately.</p>
    """
    html_content = html_template("Withdrawal Successful", body_html)
    send_email_alert_html(subject, html_content, user.email)


def send_deposit_alert(user, amount):
    subject = "Deposit Received – Spectrum Arena"
    body_html = f"""
    <p>Hello {user.first_name},</p>
    <p>We’ve received your deposit of <strong>₦{amount:,.2f}</strong>.</p>
    <p>Thank you for saving with Spectrum Arena.</p>
    """
    html_content = html_template("Deposit Received", body_html)
    send_email_alert_html(subject, html_content, user.email)


def send_otp_email(user, otp_code):
    subject = "Your Spectrum Arena OTP"
    body_html = f"""
    <p>Hello {user.first_name},</p>
    <p>Your One-Time Password (OTP) is:</p>
    <h2 style="color: #ff7f00;">{otp_code}</h2>
    <p>This code expires in 5 minutes.</p>
    <p>Do NOT share this code with anyone.</p>
    """
    html_content = html_template("Your OTP Code", body_html)
    send_email_alert_html(subject, html_content, user.email)


# --------------------------------------------------------
# FAILED WITHDRAWAL ALERT
# --------------------------------------------------------
def send_failed_withdrawal_alert(user, amount, reason):
    subject = "Withdrawal Attempt Failed – Spectrum Arena"
    body_html = f"""
    <p>Hello {user.first_name},</p>
    <p>Your withdrawal attempt of <strong>₦{amount:,.2f}</strong> failed.</p>
    <p>Reason: <strong>{reason}</strong></p>
    <p>If you did not attempt this transaction, please contact support immediately.</p>
    """
    html_content = html_template("Withdrawal Failed", body_html)
    send_email_alert_html(subject, html_content, user.email)


# --------------------------------------------------------
# DAILY SAVINGS ACTIVITY SUMMARY
# --------------------------------------------------------
def send_daily_savings_summary(user, transactions, total_balance):
    """
    Send a daily summary email to the user.
    transactions: list of dicts [{'type': 'deposit', 'amount': 5000, 'timestamp': datetime}, ...]
    """
    subject = "Your Daily Savings Summary – Spectrum Arena"

    tx_html = ""
    for tx in transactions:
        tx_type = "Deposit" if tx['type'] == 'deposit' else "Withdrawal"
        color = "#4ade80" if tx['type'] == 'deposit' else "#f87171"  # green/red
        tx_html += f"""
        <tr>
            <td>{tx['timestamp'].strftime('%d %b %Y %H:%M')}</td>
            <td style="color:{color}; font-weight:bold;">{tx_type}</td>
            <td>₦{tx['amount']:,.2f}</td>
        </tr>
        """

    body_html = f"""
    <p>Hello {user.first_name},</p>
    <p>Here’s a summary of your savings activity today:</p>
    <table width="100%" cellpadding="5" cellspacing="0" style="background-color:#1f2937; color:#fff; border-radius:6px;">
        <thead>
            <tr>
                <th>Date & Time</th>
                <th>Type</th>
                <th>Amount</th>
            </tr>
        </thead>
        <tbody>
            {tx_html}
        </tbody>
    </table>
    <p>Total Balance: <strong>₦{total_balance:,.2f}</strong></p>
    """
    html_content = html_template("Daily Savings Summary", body_html)
    send_email_alert_html(subject, html_content, user.email)

