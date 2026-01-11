from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class NotificationLog(models.Model):
    NOTIF_TYPE_CHOICES = [
        ("email", "Email"),
        ("sms", "SMS"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=NOTIF_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=10, default="pending")  # pending, sent, failed
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} | {self.type} | {self.title}"

