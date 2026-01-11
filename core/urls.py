"""
URL configuration for Spectrum Arena backend.
"""

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

# -------------------------------------------------------------------------
# URL patterns
# -------------------------------------------------------------------------
urlpatterns = [
    # ---------------------------------------------------------------------
    # Admin
    # ---------------------------------------------------------------------
    path("admin/", admin.site.urls),

    # ---------------------------------------------------------------------
    # API routes (App includes)
    # ---------------------------------------------------------------------
    path("api/users/", include("users.urls")),
    path("api/jobs/", include("jobs.urls")),
    path("api/jobs-sync/", include("jobs_sync.urls")),
    path("api/artisans/", include("artisans.urls")),
    path("api/savings/", include("savings.urls")),
    path("api/payments/", include("payments.urls")),

    # ---------------------------------------------------------------------
    # Authentication (JWT)
    # ---------------------------------------------------------------------
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # ---------------------------------------------------------------------
    # Paystack Webhook (NO auth, NO csrf)
    # ---------------------------------------------------------------------
    path("webhooks/paystack/", paystack_webhook, name="paystack-webhook"),

    # ---------------------------------------------------------------------
    # OpenAPI / Swagger / ReDoc
    # ---------------------------------------------------------------------
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

# -------------------------------------------------------------------------
# Static files serving (DEV ONLY)
# -------------------------------------------------------------------------
if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    )

