from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone

from .models import Job, JobSyncLog
from .serializers import JobSerializer, JobSyncLogSerializer


# -------------------------------------------------------
# LIST ALL FETCHED EXTERNAL JOBS
# -------------------------------------------------------
class JobSyncListView(generics.ListAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer


# -------------------------------------------------------
# JOB SYNC STATISTICS
# -------------------------------------------------------
class JobSyncStatsView(generics.ListAPIView):
    queryset = JobSyncLog.objects.all()
    serializer_class = JobSyncLogSerializer

