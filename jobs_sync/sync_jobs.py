import requests
from jobs_sync.models import Job


def sync_google_jobs():
    """
    Fetch and store jobs from Google Jobs.
    (This is currently a mock example; we'll integrate live APIs or scraping next.)
    """
    print("🔄 Syncing from Google Jobs...")

    # Example pseudo-fetch data
    jobs = [
        {
            "title": "Backend Developer",
            "company": "Google",
            "location": "Lagos",
            "description": "Django API role",
            "source": "Google",
            "url": "https://google.com/jobs/backend",
        },
    ]

    for job in jobs:
        Job.objects.get_or_create(url=job["url"], defaults=job)

    print("✅ Google Jobs synced successfully.")


def sync_jobberman():
    """
    Fetch and store jobs from Jobberman (RSS / JSON feed).
    """
    print("🔄 Syncing from Jobberman...")
    # TODO: Implement Jobberman API or RSS parser
    pass


def sync_indeed():
    """
    Fetch and store jobs from Indeed.
    """
    print("🔄 Syncing from Indeed...")
    # TODO: Implement Indeed public search / feed
    pass


def run_all_syncs():
    """
    Run all job synchronization sources sequentially.
    """
    sync_google_jobs()
    sync_jobberman()
    sync_indeed()
    print("✅ All job sources synced successfully.")

