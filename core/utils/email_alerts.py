from django.core.mail import EmailMultiAlternatives
from django.conf import settings


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


# --------------------------------------------------------
# Helper to wrap content in a branded HTML template
# --------------------------------------------------------
def html_template(title, body_html):
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
# Withdrawal Alert
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


# --------------------------------------------------------
# Deposit Alert
# --------------------------------------------------------
def send_deposit_alert(user, amount):
    subject = "Deposit Received – Spectrum Arena"
    body_html = f"""
    <p>Hello {user.first_name},</p>
    <p>We’ve received your deposit of <strong>₦{amount:,.2f}</strong>.</p>
    <p>Thank you for saving with Spectrum Arena.</p>
    """
    html_content = html_template("Deposit Received", body_html)
    send_email_alert_html(subject, html_content, user.email)


# --------------------------------------------------------
# OTP Email Alert
# --------------------------------------------------------
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

