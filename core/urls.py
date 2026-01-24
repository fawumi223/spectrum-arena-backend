"""
URL configuration for Spectrum Arena backend.
"""

from django.shortcuts import redirect
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import TokenRefreshView

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from users.views_paystack import paystack_webhook
from users.views import PhoneTokenObtainPairView


def root_redirect(request):
    return redirect("/api/docs/")


urlpatterns = [
    # Root redirect → Swagger UI
    path("", root_redirect),

    # Admin Dashboard
    path("admin/", admin.site.urls),

    # ---- API ROUTES ----
    path("api/users/", include("users.urls")),
    path("api/jobs/", include("jobs.urls")),
    path("api/jobs-sync/", include("jobs_sync.urls")),
    path("api/artisans/", include("artisans.urls")),
    path("api/savings/", include("savings.urls")),
    path("api/payments/", include("payments.urls")),

    # ---- JWT AUTH ----
    path("api/token/", PhoneTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # ---- WEBHOOKS (NO AUTH) ----
    path("api/webhooks/paystack/", paystack_webhook, name="paystack-webhook"),

    # ---- OPENAPI SCHEMA ----
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),

    # ---- SWAGGER ----
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui"
    ),

    # ---- REDOC ----
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc"
    ),
]


# ---- STATIC IN DEV MODE ----
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

