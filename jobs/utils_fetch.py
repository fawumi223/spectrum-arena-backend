import requests
from bs4 import BeautifulSoup
from django.conf import settings
from .models import JobPost

def fetch_indeed_jobs():
    """
    Simulated Indeed job fetcher.
    Later: integrate with Indeed API or RSS.
    """
    print("🔹 Fetching jobs from Indeed...")
    jobs = [
        {
            "company_name": "Indeed Corp",
            "position_title": "Customer Support Specialist",
            "description": "Join our remote support team.",
            "address": "Remote, Nigeria",
            "job_type": "REMOTE",
            "source": "EXTERNAL",
        }
    ]
    return jobs


def fetch_jobberman_jobs():
    """
    Simulated Jobberman job fetcher.
    """
    print("🔹 Fetching jobs from Jobberman...")
    jobs = [
        {
            "company_name": "Jobberman Africa",
            "position_title": "Marketing Lead",
            "description": "We are hiring a marketing lead.",
            "address": "Lagos, Nigeria",
            "job_type": "ONSITE",
            "source": "EXTERNAL",
        }
    ]
    return jobs


def fetch_google_jobs():
    """
    Simulated Google Jobs fetcher.
    """
    print("🔹 Fetching jobs from Google Jobs...")
    jobs = [
        {
            "company_name": "Google Nigeria",
            "position_title": "Software Engineer",
            "description": "Join our engineering team in Lagos.",
            "address": "Lagos, Nigeria",
            "job_type": "HYBRID",
            "source": "EXTERNAL",
        }
    ]
    return jobs


def save_external_jobs(job_list):
    """Store fetched jobs in DB if not already existing."""
    for job in job_list:
        obj, created = JobPost.objects.get_or_create(
            company_name=job["company_name"],
            position_title=job["position_title"],
            defaults={
                "description": job.get("description", ""),
                "address": job.get("address", ""),
                "job_type": job.get("job_type", "ONSITE"),
                "source": job.get("source", "EXTERNAL"),
            },
        )
        if created:
            print(f"✅ New job added: {obj.company_name} — {obj.position_title}")
        else:
            print(f"⚠️ Job already exists: {obj.company_name} — {obj.position_title}")

