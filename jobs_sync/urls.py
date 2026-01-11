from django.urls import path
from .views import JobSyncListView, JobSyncStatsView

urlpatterns = [
    path("", JobSyncListView.as_view(), name="job-sync-list"),
    path("stats/", JobSyncStatsView.as_view(), name="job-sync-stats"),
]

