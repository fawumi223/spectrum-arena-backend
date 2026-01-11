from celery import shared_task
from django.utils import timezone
from core.utils.notifications import (
    send_email_alert_html,
    send_sms_alert
)
from .models import NotificationLog


@shared_task(bind=True, max_retries=3)
def send_email_task(self, log_id, subject, html_content, recipient_email, text_content=None):
    try:
        send_email_alert_html(subject, html_content, recipient_email, text_content)
        log = NotificationLog.objects.get(id=log_id)
        log.status = "sent"
        log.sent_at = timezone.now()
        log.save()
    except Exception as exc:
        log = NotificationLog.objects.get(id=log_id)
        log.status = "failed"
        log.error = str(exc)
        log.save()
        raise self.retry(exc=exc, countdown=60)  # retry in 1 min


@shared_task(bind=True, max_retries=3)
def send_sms_task(self, log_id, to_number, message):
    try:
        send_sms_alert(to_number, message)
        log = NotificationLog.objects.get(id=log_id)
        log.status = "sent"
        log.sent_at = timezone.now()
        log.save()
    except Exception as exc:
        log = NotificationLog.objects.get(id=log_id)
        log.status = "failed"
        log.error = str(exc)
        log.save()
        raise self.retry(exc=exc, countdown=60)

