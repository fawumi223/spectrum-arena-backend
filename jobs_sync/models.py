from django.db import models
from django.utils import timezone


class Job(models.Model):
    """
    External Job Model
    Stores job listings fetched from external sources.
    """
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    source = models.CharField(max_length=50)  # Google, Jobberman, Indeed
    url = models.URLField(unique=True)
    date_posted = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-date_posted"]
        verbose_name = "External Job"
        verbose_name_plural = "External Jobs"

    def __str__(self):
        return f"{self.title} @ {self.company}"


class JobSyncLog(models.Model):
    """
    Logs every job synchronization
    """
    SOURCE_CHOICES = [
        ("Google", "Google"),
        ("Jobberman", "Jobberman"),
        ("Indeed", "Indeed"),
        ("All", "All Sources"),
    ]

    STATUS_CHOICES = [
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default="All")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="SUCCESS")
    new_jobs = models.PositiveIntegerField(default=0)
    message = models.TextField(blank=True, null=True)
    run_time = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-run_time"]
        verbose_name = "Job Sync Log"
        verbose_name_plural = "Job Sync Logs"

    def __str__(self):
        return f"{self.source} - {self.new_jobs} jobs ({self.status})"

