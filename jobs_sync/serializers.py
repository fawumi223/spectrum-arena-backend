from rest_framework import serializers
from .models import Job, JobSyncLog


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"


class JobSyncLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSyncLog
        fields = "__all__"

