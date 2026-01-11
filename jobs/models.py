from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

USER = settings.AUTH_USER_MODEL


class JobPost(models.Model):
    # Source of job (where it originated)
    SOURCE_CHOICES = [
        ("INTERNAL", "Internal"),
        ("EXTERNAL", "External"),
    ]

    # Mode of the job (on-site / remote / hybrid)
    JOB_MODE_CHOICES = [
        ("ONSITE", "On-site"),
        ("REMOTE", "Remote"),
        ("HYBRID", "Hybrid"),
    ]

    PLAN_BASIC = "basic"
    PLAN_PREMIUM = "premium"
    PLAN_CHOICES = [
        (PLAN_BASIC, "Basic"),
        (PLAN_PREMIUM, "Premium"),
    ]

    JOB_FULLTIME = "Full-Time"
    JOB_PARTTIME = "Part-Time"
    JOB_CONTRACT = "Contract"
    JOB_TYPE_CHOICES = [
        (JOB_FULLTIME, "Full-Time"),
        (JOB_PARTTIME, "Part-Time"),
        (JOB_CONTRACT, "Contract"),
    ]

    # Core fields
    user = models.ForeignKey(
        USER,
        on_delete=models.CASCADE,
        related_name="job_posts",
        null=True,  # temporarily allow NULL for migration safety
        blank=True
    )
    company_name = models.CharField(max_length=255)
    company_address = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, default="General")  # e.g., Autos, Finance, Farming
    role = models.CharField(max_length=200, default="General")
    job_type = models.CharField(max_length=32, choices=JOB_TYPE_CHOICES, default=JOB_FULLTIME)
    job_mode = models.CharField(max_length=16, choices=JOB_MODE_CHOICES, default="ONSITE")
    source = models.CharField(max_length=16, choices=SOURCE_CHOICES, default="INTERNAL")
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # Plan + visibility
    plan_type = models.CharField(max_length=16, choices=PLAN_CHOICES, default=PLAN_BASIC)
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    # Optional geo (for later proximity search)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Job Post"
        verbose_name_plural = "Job Posts"

    def __str__(self):
        return f"{self.company_name} — {self.role} ({self.category})"

    def save(self, *args, **kwargs):
        # Set premium flag and expiry based on plan_type if not already set
        if self.plan_type == self.PLAN_PREMIUM:
            self.is_premium = True
            self.expiry_date = timezone.now() + timedelta(days=7)
        else:
            self.is_premium = False
            self.expiry_date = timezone.now() + timedelta(days=1)

        super().save(*args, **kwargs)

