"""
Django settings for recruitment project.

Secrets and environment-specific values are read from environment variables
(loaded from a local .env via python-dotenv). See .env.example.
"""

from pathlib import Path

import dj_database_url
from dotenv import load_dotenv
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from a local .env file (no-op if it doesn't exist).
load_dotenv(BASE_DIR / ".env")


# SECURITY WARNING: keep the secret key used in production secret!
# Read from the environment; fall back to an insecure default for local dev only.
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "django-insecure-local-dev-key-change-me"
)

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG defaults to True locally; set DEBUG=False in production.
DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Hosts Django will accept POST/CSRF from over HTTPS (the deployed domain).
# e.g. CSRF_TRUSTED_ORIGINS=https://myapp.onrender.com
CSRF_TRUSTED_ORIGINS = [
    origin
    for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin
]

# Render injects the service's public hostname automatically. Trust it so the
# deploy serves correctly without manually setting ALLOWED_HOSTS for the domain.
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    # Local apps
    "accounts",
    "jobs",
    "api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise serves static files in production (right after SecurityMiddleware).
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "recruitment.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Shared project-level templates (base.html etc.) live here.
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "recruitment.wsgi.application"


# Database
# Local dev defaults to SQLite; production sets DATABASE_URL to cloud Postgres.
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}


# Custom user model (must be set before the first migration). See SPEC §5.1.
AUTH_USER_MODEL = "accounts.User"

# Authentication redirects (SPEC §8).
LOGIN_URL = "login"                 # where @login_required sends anonymous users
LOGIN_REDIRECT_URL = "dashboard"    # after login → role-aware dashboard redirect
LOGOUT_REDIRECT_URL = "job_list"    # after logout → public job list


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"        # collectstatic target for deployment
STATICFILES_DIRS = [BASE_DIR / "static"]      # project-level static assets

# WhiteNoise: compressed, hashed static files in production.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Production-only security settings (applied when DEBUG=False). The host
# (Render/PythonAnywhere) terminates HTTPS, so we trust its forwarded header
# and redirect any plain HTTP to HTTPS. (SPEC §11, §12.)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
