import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

SECRET_KEY = os.environ.get("SFPCL_SECRET_KEY", "local-dev-only-sfpcl-credit")
DEBUG = True
ALLOWED_HOSTS = ["*"]

ROOT_URLCONF = "sfpcl_credit.config.urls"
WSGI_APPLICATION = "sfpcl_credit.config.wsgi.application"
ASGI_APPLICATION = "sfpcl_credit.config.asgi.application"

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "sfpcl_credit.identity",
]

MIDDLEWARE = []

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
TIME_ZONE = "UTC"

AUTH_ACCESS_TOKEN_MINUTES = 15
AUTH_REFRESH_TOKEN_HOURS = 24
