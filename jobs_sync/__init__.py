from django.apps import AppConfig

default_app_config = "jobs_sync.apps.JobsSyncConfig"

def ready():
    # Import tasks *after* Django app registry is fully ready
    import jobs_sync.tasks

