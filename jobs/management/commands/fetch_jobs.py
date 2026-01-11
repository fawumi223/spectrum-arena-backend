from django.core.management.base import BaseCommand
from jobs.utils_fetch import (
    fetch_indeed_jobs, fetch_jobberman_jobs, fetch_google_jobs, save_external_jobs
)

class Command(BaseCommand):
    help = "Fetch jobs from external sources (Indeed, Jobberman, Google Jobs)"

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Starting external job fetch...")

        all_jobs = []
        all_jobs += fetch_indeed_jobs()
        all_jobs += fetch_jobberman_jobs()
        all_jobs += fetch_google_jobs()

        save_external_jobs(all_jobs)

        self.stdout.write(self.style.SUCCESS("✅ External job fetch completed successfully!"))

