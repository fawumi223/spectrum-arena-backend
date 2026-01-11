from django.core.management.base import BaseCommand
from jobs_sync.sync_jobs import run_all_syncs


class Command(BaseCommand):
    help = "Sync jobs from Google, Jobberman, and Indeed."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("🚀 Starting job sync..."))
        run_all_syncs()
        self.stdout.write(self.style.SUCCESS("✅ Job sync completed successfully."))

