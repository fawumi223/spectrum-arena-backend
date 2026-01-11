from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db import connection
from jobs.models import JobPost


@receiver(post_migrate)
def create_default_job(sender, **kwargs):
    """
    Automatically create a default job post for Sugar Bakes & Creams.
    Safe against missing table errors during initial migrations.
    """
    if sender.name != 'jobs':
        return  # Only run when the jobs app finishes migrating

    # ✅ Ensure the JobPost table exists before inserting
    if 'jobs_jobpost' not in connection.introspection.table_names():
        print("⚠️ Skipping job seeding — 'jobs_jobpost' table not yet created.")
        return

    User = get_user_model()

    # ✅ Create or get a verified user for the default post
    user, _ = User.objects.get_or_create(
        full_name="Sugar Bakes And Creams",
        phone_number="+2347016564381",
        defaults={
            "email": "omobolaislamiat02@gmail.com",
            "is_verified": True,
            "plan_type": "premium",
        },
    )

    # ✅ Create or get the default JobPost (new schema)
    JobPost.objects.get_or_create(
        user=user,
        company_name="Sugar Bakes And Creams",
        company_address="Lagos, Nigeria",
        category="Catering",
        role="Pastry and Cake Marketer",
        job_type="Full-Time",
        job_mode="ONSITE",
        description="We’re hiring a skilled marketer for cakes, pastries, and confectioneries.",
        salary_range="₦50,000 - ₦120,000 monthly (Negotiable)",
        plan_type="premium",
        source="INTERNAL",
    )

    print("✅ Default job created successfully.")

