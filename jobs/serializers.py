from rest_framework import serializers
from .models import JobPost


class JobPostSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = JobPost
        fields = [
            "id",
            "user_full_name",
            "company_name",
            "company_address",
            "category",
            "role",
            "job_type",
            "job_mode",
            "source",
            "salary_range",
            "description",
            "plan_type",
            "is_premium",
            "created_at",
            "expiry_date",
            "is_active",
            "latitude",
            "longitude",
        ]
        read_only_fields = ["id", "is_premium", "created_at", "expiry_date", "is_active"]

