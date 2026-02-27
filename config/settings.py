from datetime import timedelta

import os
from pathlib import Path

from dotenv import load_dotenv

# ──────────────────────────────────────────────
# Base & Environment
# ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-only-fallback-key",
)
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() in ("true", "1", "yes")
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost").split(",")

# ──────────────────────────────────────────────
# Installed Apps
# ──────────────────────────────────────────────
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "drf_spectacular",
    # Project apps
    "accounts",
    "trains",
    "bookings",
    "analytics",
]

# ──────────────────────────────────────────────
# Middleware
# ──────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Custom
    "analytics.middleware.SearchAnalyticsMiddleware",
]

# ──────────────────────────────────────────────
# URL / WSGI / ASGI
# ──────────────────────────────────────────────
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ──────────────────────────────────────────────
# Templates
# ──────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ──────────────────────────────────────────────
# Databases
# ──────────────────────────────────────────────
DATABASES = {
    # PRIMARY — MySQL for transactional data
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("MYSQL_DATABASE", "irtc_db"),
        "USER": os.getenv("MYSQL_USER", "irtc_user"),
        "PASSWORD": os.getenv("MYSQL_PASSWORD", "irtc_pass_123"),
        "HOST": os.getenv("MYSQL_HOST", "db"),
        "PORT": os.getenv("MYSQL_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },
    # SECONDARY — MongoDB for API analytics & logs
    "mongo": {
        "ENGINE": "django_mongodb_backend",
        "NAME": os.getenv("MONGO_DB_NAME", "irtc_logs"),
        "HOST": f"mongodb://{os.getenv('MONGO_HOST', 'mongo')}:{os.getenv('MONGO_PORT', '27017')}/{os.getenv('MONGO_DB_NAME', 'irtc_logs')}",
    },
}

# Direct pymongo URI (used by analytics middleware & views)
MONGO_URI = (
    f"mongodb://{os.getenv('MONGO_HOST', 'mongo')}:{os.getenv('MONGO_PORT', '27017')}"
)

DATABASE_ROUTERS = ["config.db_router.DatabaseRouter"]

# ──────────────────────────────────────────────
# Custom Auth Model
# ──────────────────────────────────────────────
AUTH_USER_MODEL = "accounts.User"

# Uses email to authenticate by default
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# ──────────────────────────────────────────────
# Password Validation
# ──────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ──────────────────────────────────────────────
# Internationalization
# ──────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# ──────────────────────────────────────────────
# Static Files
# ──────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# ──────────────────────────────────────────────
# Default Primary Key
# ──────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ──────────────────────────────────────────────
# Django REST Framework
# ──────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "30/minute",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# ──────────────────────────────────────────────
# drf-spectacular (OpenAPI / Swagger)
# ──────────────────────────────────────────────
SPECTACULAR_SETTINGS = {
    "TITLE": "IRTC Train Booking API",
    "DESCRIPTION": (
        "REST API for the IRTC train booking system.\n\n"
        "• **Accounts** — registration & JWT login\n"
        "• **Trains** — CRUD (admin) & public search\n"
        "• **Bookings** — seat booking with concurrency control\n"
        "• **Analytics** — top searched routes (MongoDB)"
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SECURITY": [{"BearerAuth": []}],
    "COMPONENTS": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    },
    "TAGS": [
        {"name": "Accounts", "description": "User registration & authentication"},
        {"name": "Trains", "description": "Train management & search"},
        {"name": "Bookings", "description": "Seat booking & booking history"},
        {"name": "Analytics", "description": "Search analytics from MongoDB"},
    ],
}

# ──────────────────────────────────────────────
# Simple JWT
# ──────────────────────────────────────────────
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}
