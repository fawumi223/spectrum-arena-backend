from django.urls import path, include
from rest_framework.routers import DefaultRouter
from jobs.views import JobViewSet, NearbyJobsView
from jobs.views_sync import JobSyncView  # Custom sync API

# Router for CRUD job operations
router = DefaultRouter()
router.register(r'posts', JobViewSet, basename='jobs')

urlpatterns = [
    path('', include(router.urls)),                  # CRUD: /api/jobs/posts/
    path('sync/', JobSyncView.as_view(), name='job-sync'),  # Custom: /api/jobs/sync/
    path('nearby/', NearbyJobsView.as_view(), name='jobs-nearby'),  # NEW: /api/jobs/nearby/
]

