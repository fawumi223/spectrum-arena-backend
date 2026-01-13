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
    # Root redirect
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

    # JWT
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Paystack webhook
    path("api/webhooks/paystack/", paystack_webhook, name="paystack-webhook"),

    # Schema / Swagger / Redoc
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]


# DEV static
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

