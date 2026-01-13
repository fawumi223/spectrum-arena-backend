"""
Django settings for Spectrum Arena backend
"""

# =========================================================================
# BASE IMPORTS
# =========================================================================
import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
from celery.schedules import crontab

# =========================================================================
# BASE DIRECTORY
# =========================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# =========================================================================
# SECURITY
# =========================================================================
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-dev-key")
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = os.getenv(
    "DJANGO_ALLOWED_HOSTS",
    "localhost,127.0.0.1"
).split(",")

# =========================================================================
# INSTALLED APPS
# =========================================================================
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework", "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_spectacular",

    # Local apps
    "users",
    "jobs",
    "artisans",
    "jobs_sync.apps.JobsSyncConfig",
    "savings",
    "payments",
]

# =========================================================================
# MIDDLEWARE
# =========================================================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # must be above CommonMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# =========================================================================
# URLS / WSGI
# =========================================================================
ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"

# =========================================================================
# DATABASE (POSTGRES + POSTGIS)
# =========================================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

# =========================================================================
# AUTH
# =========================================================================
AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =========================================================================
# INTERNATIONALIZATION
# =========================================================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Lagos"
USE_I18N = True
USE_TZ = True

# =========================================================================
# STATIC FILES
# =========================================================================
STATIC_URL = "/static/"

# Local dev static directory (keep for React, images, etc.)
STATICFILES_DIRS = [BASE_DIR / "static"]

# Production static collection directory
STATIC_ROOT = BASE_DIR / "staticfiles"

# Whitenoise static file compression & cache versioning
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# =========================================================================
# TEMPLATES
# =========================================================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "core" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# =========================================================================
# DATABASES
# =========================================================================
if os.getenv("DB_NAME"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD"),
            "HOST": os.getenv("DB_HOST"),
            "PORT": os.getenv("DB_PORT", 5432),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# =========================================================================
# DJANGO REST FRAMEWORK
# =========================================================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Spectrum Arena API",
    "DESCRIPTION": "Backend API for Spectrum Arena",
    "VERSION": "1.0.0",
}

# =========================================================================
# JWT
# =========================================================================
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=6),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# =========================================================================
# EMAIL CONFIG (GMAIL SMTP - ACTIVE)
# =========================================================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# =========================================================================
# PAYSTACK
# =========================================================================
PAYSTACK_PUBLIC_KEY = os.getenv("PAYSTACK_PUBLIC_KEY")
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
PAYSTACK_BASE_URL = "https://api.paystack.co"

# =========================================================================
# TERMII SMS (OTP)
# =========================================================================
TERMII_API_KEY = os.getenv("TERMII_API_KEY")
TERMII_BASE_URL = os.getenv("TERMII_BASE_URL", "https://v3.api.termii.com")
TERMII_SENDER_ID = os.getenv("TERMII_SENDER_ID", "SPECTRUMAPP")
TERMII_FROM = os.getenv("TERMII_FROM")
TERMII_CHANNEL = os.getenv("TERMII_CHANNEL", "generic")

# =========================================================================
# CORS / CSRF (DEV MODE)
# =========================================================================
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True  # REMOVE IN PRODUCTION
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "https://spectrumarena.com",
]

CORS_EXPOSE_HEADERS = ["Content-Type", "Authorization"]

CORS_ALLOW_HEADERS = [
    "accept", "authorization", "content-type", "origin",
    "user-agent", "x-csrftoken", "x-requested-with",
]

CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

# =========================================================================
# CELERY / REDIS
# =========================================================================
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Africa/Lagos"
CELERY_ENABLE_UTC = False

CELERY_BEAT_SCHEDULE = {
    "daily-job-sync": {
        "task": "jobs_sync.tasks.auto_sync_jobs",
        "schedule": crontab(hour=0, minute=0),
    },
    "unlock-savings": {
        "task": "savings.tasks.unlock_matured_savings",
        "schedule": crontab(hour=0, minute=0),
    },
}

# =========================================================================
# DEFAULT PRIMARY KEY
# =========================================================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

