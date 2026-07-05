import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


def env_bool(name, default):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_csv(name, default):
    value = os.environ.get(name)
    if value is None:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


SECRET_KEY = os.environ.get("SFPCL_SECRET_KEY", "local-dev-only-sfpcl-credit")
DEBUG = env_bool("SFPCL_DEBUG", True)
ALLOWED_HOSTS = env_csv("SFPCL_ALLOWED_HOSTS", ["localhost", "127.0.0.1", "testserver"])
CORS_ALLOWED_ORIGINS = env_csv("SFPCL_CORS_ORIGINS", ["http://localhost:5173"])

ROOT_URLCONF = "sfpcl_credit.config.urls"
WSGI_APPLICATION = "sfpcl_credit.config.wsgi.application"
ASGI_APPLICATION = "sfpcl_credit.config.asgi.application"

INSTALLED_APPS = [
    "corsheaders",
    "django.contrib.contenttypes",
    "sfpcl_credit.identity",
    "sfpcl_credit.tracer",
    "sfpcl_credit.workflows",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

# SFPCL_DB_PATH lets a dev/E2E web server point at an isolated sqlite file
# (e.g. the Playwright harness) without touching the default local dev DB.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("SFPCL_DB_PATH") or (BASE_DIR / "db.sqlite3"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
TIME_ZONE = "UTC"

AUTH_ACCESS_TOKEN_MINUTES = 15
AUTH_REFRESH_TOKEN_HOURS = 24
