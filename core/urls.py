"""
URL configuration for Spectrum Arena backend.
"""

from django.shortcuts import redirect
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# DRF Spectacular (Swagger / OpenAPI)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from users.views_paystack import paystack_webhook


# ---------------------------------------------------------
# Redirect root → Swagger UI
# ---------------------------------------------------------
def root_redirect(request):
    return redirect("/api/docs/")


urlpatterns = [
    # Redirect base URL
    path("", root_redirect),

    # Admin
    path("admin/", admin.site.urls),

    # API routes
    path("api/users/", include("users.urls")),
    path("api/jobs/", include("jobs.urls")),
    path("api/jobs-sync/", include("jobs_sync.urls")),
    path("api/artisans/", include("artisans.urls")),
    path("api/savings/", include("savings.urls")),
    path("api/payments/", include("payments.urls")),

    # JWT endpoints
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Paystack webhook
    path("api/webhooks/paystack/", paystack_webhook, name="paystack-webhook"),

    # OpenAPI/Swagger schema
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),

    # Swagger UI (with cache disabled for Chrome/mobile correctness)
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema", cache_timeout=0),
        name="swagger-ui"
    ),

    # ReDoc UI
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]


# ---------------------------------------------------------
# Static files (only served when DEBUG=True)
# ---------------------------------------------------------
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

