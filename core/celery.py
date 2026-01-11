import os
from celery import Celery
from django.conf import settings

# ---------------------------------------------------------------------
# Set default Django settings for Celery
# ---------------------------------------------------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# ---------------------------------------------------------------------
# Create Celery app
# ---------------------------------------------------------------------
app = Celery("core")

# Load Celery settings from Django settings.py (only variables starting with CELERY_)
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks.py modules in all installed apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# ---------------------------------------------------------------------
# Optional: Debug helper task
# ---------------------------------------------------------------------
@app.task(bind=True)
def debug_task(self):
    """
    Simple task to test Celery setup.
    Run in terminal: celery -A core call debug_task
    """
    print(f"Request: {self.request!r}")
    return f"Debug task executed successfully at {self.request!r}"


# ---------------------------------------------------------------------
# Optional: Signal to log worker start
# ---------------------------------------------------------------------
from celery.signals import worker_ready

@worker_ready.connect
def at_start(sender, **kwargs):
    print("Celery worker is ready. All tasks can be processed.")

