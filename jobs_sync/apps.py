from django.apps import AppConfig

class JobsSyncConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "jobs_sync"

    def ready(self):
        # Import tasks only when Django apps are fully loaded
        import jobs_sync.tasks

