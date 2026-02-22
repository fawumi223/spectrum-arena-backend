"""
Django settings for Spectrum Arena backend
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# =========================================================================
# BASE
# =========================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# =========================================================================
# SECURITY
# =========================================================================
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "unsafe-dev-key")
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".railway.app",
    ".up.railway.app",
]

# =========================================================================
# INSTALLED APPS
# =========================================================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_spectacular",

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
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"

# =========================================================================
# DATABASE
# =========================================================================
if os.getenv("DATABASE_URL"):
    import dj_database_url
    DATABASES = {
        "default": dj_database_url.parse(os.getenv("DATABASE_URL"))
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# =========================================================================
# AUTH
# =========================================================================
AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

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
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

if DEBUG:
    STATICFILES_DIRS = [BASE_DIR / "static"]

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
# REST FRAMEWORK / OPENAPI
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
    "VERSION": "1.0.0",
    "SERVERS": [
        {"url": "https://web-production-c2159.up.railway.app", "description": "Production"},
        {"url": "http://127.0.0.1:8000", "description": "Local"},
    ],
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
# EMAIL
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
PAYSTACK_PUBLIC_KEY_TEST = os.getenv("PAYSTACK_PUBLIC_KEY_TEST")
PAYSTACK_SECRET_KEY_TEST = os.getenv("PAYSTACK_SECRET_KEY_TEST")
PAYSTACK_PUBLIC_KEY_LIVE = os.getenv("PAYSTACK_PUBLIC_KEY_LIVE")
PAYSTACK_SECRET_KEY_LIVE = os.getenv("PAYSTACK_SECRET_KEY_LIVE")

if DEBUG:
    PAYSTACK_PUBLIC_KEY = PAYSTACK_PUBLIC_KEY_TEST
    PAYSTACK_SECRET_KEY = PAYSTACK_SECRET_KEY_TEST
else:
    PAYSTACK_PUBLIC_KEY = PAYSTACK_PUBLIC_KEY_LIVE
    PAYSTACK_SECRET_KEY = PAYSTACK_SECRET_KEY_LIVE

PAYSTACK_BASE_URL = "https://api.paystack.co"

# =========================================================================
# TERMII
# =========================================================================
TERMII_API_KEY = os.getenv("TERMII_API_KEY")
TERMII_BASE_URL = os.getenv("TERMII_BASE_URL", "https://v3.api.termii.com")
TERMII_SENDER_ID = os.getenv("TERMII_SENDER_ID", "SPECTRUMAPP")
TERMII_FROM = os.getenv("TERMII_FROM")
TERMII_CHANNEL = os.getenv("TERMII_CHANNEL", "generic")

# =========================================================================
# CORS / CSRF
# =========================================================================
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = [
    "https://spectrum-arena-frontend.vercel.app",
]

CSRF_TRUSTED_ORIGINS = [
    "https://spectrum-arena-frontend.vercel.app",
    "https://web-production-c2159.up.railway.app",
]

# =========================================================================
# DEFAULT
# =========================================================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
