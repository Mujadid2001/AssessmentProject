"""
Django settings for ELD project
Production-ready configuration with PostgreSQL support
"""

import os
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key generation with fallback
def get_secret_key():
    """Generate or retrieve SECRET_KEY with secure fallback"""
    env_key = os.environ.get("SECRET_KEY")
    if env_key:
        return env_key
    
    # Development fallback
    import hashlib
    dev_key = hashlib.sha256(b"eld-dev-key-2024").hexdigest()
    return f"django-insecure-{dev_key}"

SECRET_KEY = get_secret_key()
DEBUG = os.environ.get("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1,*.vercel.app").split(",")

# Application definition
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "corsheaders",
    "api",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
            ],
        },
    },
]

# Database - PostgreSQL (Neon.tech) with SQLite fallback
def get_database_config():
    """Get database configuration from environment or use SQLite fallback"""
    database_url = os.environ.get("DATABASE_URL")
    
    if database_url:
        # PostgreSQL via Neon.tech
        import dj_database_url
        return dj_database_url.config(
            default=database_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
    else:
        # SQLite for development
        return {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }

DATABASES = get_database_config()

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_FILTER_BACKENDS": ["rest_framework.filters.OrderingFilter"],
    "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
}

# CORS
CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000"
).split(",")

# Security
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
}

# Production: WhiteNoise static files
if not DEBUG:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Production: CORS
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    origin.strip() for origin in os.environ.get(
        "CORS_ALLOWED_ORIGINS", 
        "http://localhost:5173,http://localhost:3000"
    ).split(",")
]

# Production: Database connection pooling
if not DEBUG and "DATABASES" in locals():
    DATABASES["default"]["CONN_MAX_AGE"] = 600
    DATABASES["default"]["OPTIONS"] = {
        "connect_timeout": 10,
        "options": "-c statement_timeout=30000"
    }

# Production: Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
