"""
URL configuration for Spectrum Arena backend.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


def root_redirect(request):
    return JsonResponse({"message": "Spectrum Arena API is running"})


urlpatterns = [
    path("", root_redirect),

    # Admin
    path("admin/", admin.site.urls),

    # ---- CORE ACTIVE APPS ----
    path("api/users/", include("users.urls")),
    path("api/payments/", include("payments.urls")),
    path("api/savings/", include("savings.urls")),  # ✅ SAVINGS ENABLED

    # ---- STILL DISABLED ----
    # path("api/jobs/", include("jobs.urls")),
    # path("api/jobs-sync/", include("jobs_sync.urls")),
    # path("api/artisans/", include("artisans.urls")),

    # ---- JWT AUTH ----
    path("api/token/", include("users.jwt_urls")),

    # ---- OPENAPI ----
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

