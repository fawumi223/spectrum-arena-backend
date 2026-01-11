from django.contrib import admin
from .models import Job, JobSyncLog


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "source", "location", "date_posted")
    list_filter = ("source", "company")
    search_fields = ("title", "company", "description", "location")
    ordering = ("-date_posted",)
    readonly_fields = ("date_posted", "url")

    fieldsets = (
        ("Job Info", {
            "fields": ("title", "company", "location", "description", "source", "url")
        }),
        ("Meta Data", {
            "fields": ("date_posted",),
        }),
    )

    def has_add_permission(self, request):
        """Disallow manual creation of external jobs in admin."""
        return False


@admin.register(JobSyncLog)
class JobSyncLogAdmin(admin.ModelAdmin):
    list_display = ("source", "status", "new_jobs", "run_time")
    search_fields = ("source", "status", "message")
    list_filter = ("status", "source")
    ordering = ("-run_time",)

