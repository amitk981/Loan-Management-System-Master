import os
import sys
import base64
import json
from pathlib import Path

from corsheaders.defaults import default_headers


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
# Development-only field keys are intentionally independent from SECRET_KEY. Production secret
# provisioning/boot enforcement and repository-wide rotation remain owned by 012E3.
_LOCAL_FIELD_KEY = base64.urlsafe_b64encode(
    b"local-only-field-encryption-key!"
).decode("ascii")
_LOCAL_LOOKUP_KEY = base64.urlsafe_b64encode(
    b"local-only-field-lookup-hmac-key"
).decode("ascii")
FIELD_ENCRYPTION_CURRENT_VERSION = os.environ.get(
    "SFPCL_FIELD_ENCRYPTION_CURRENT_VERSION", "local-v1"
)
FIELD_ENCRYPTION_KEY_REF = os.environ.get(
    "SFPCL_FIELD_ENCRYPTION_KEY_REF", "local-development-only"
)
FIELD_ENCRYPTION_PREVIOUS_VERSIONS = env_csv(
    "SFPCL_FIELD_ENCRYPTION_PREVIOUS_VERSIONS", []
)
FIELD_ENCRYPTION_KEYS = json.loads(
    os.environ.get(
        "SFPCL_FIELD_ENCRYPTION_KEYS",
        json.dumps({"local-v1": _LOCAL_FIELD_KEY}),
    )
)
FIELD_LOOKUP_KEY = os.environ.get("SFPCL_FIELD_LOOKUP_KEY", _LOCAL_LOOKUP_KEY)
DEBUG = env_bool("SFPCL_DEBUG", True)
ALLOWED_HOSTS = env_csv("SFPCL_ALLOWED_HOSTS", ["localhost", "127.0.0.1", "testserver"])
CORS_ALLOWED_ORIGINS = env_csv("SFPCL_CORS_ORIGINS", ["http://localhost:5173"])
CORS_ALLOW_HEADERS = (*default_headers, "x-request-id", "idempotency-key")

ROOT_URLCONF = "sfpcl_credit.config.urls"
WSGI_APPLICATION = "sfpcl_credit.config.wsgi.application"
ASGI_APPLICATION = "sfpcl_credit.config.asgi.application"

INSTALLED_APPS = [
    "corsheaders",
    "django.contrib.contenttypes",
    "sfpcl_credit.approvals",
    "sfpcl_credit.applications",
    "sfpcl_credit.communications",
    "sfpcl_credit.configurations",
    "sfpcl_credit.credit",
    "sfpcl_credit.documents",
    "sfpcl_credit.defaults",
    "sfpcl_credit.disbursements",
    "sfpcl_credit.finance",
    "sfpcl_credit.interest",
    "sfpcl_credit.sap_workflow",
    "sfpcl_credit.legal_documents",
    "sfpcl_credit.loans",
    "sfpcl_credit.security_instruments",
    "sfpcl_credit.identity",
    "sfpcl_credit.members",
    "sfpcl_credit.monitoring",
    "sfpcl_credit.recovery.apps.RecoveryConfig",
    "sfpcl_credit.scheduler",
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

CELERY_BROKER_URL = os.environ.get("SFPCL_CELERY_BROKER_URL", "memory://")
CELERY_RESULT_BACKEND = os.environ.get(
    "SFPCL_CELERY_RESULT_BACKEND", "cache+memory://"
)
CELERY_TASK_ALWAYS_EAGER = env_bool(
    "SFPCL_CELERY_TASK_ALWAYS_EAGER", False
)
CELERY_TASK_EAGER_PROPAGATES = env_bool(
    "SFPCL_CELERY_TASK_EAGER_PROPAGATES", False
)
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
COMMUNICATION_JOB_LEASE_SECONDS = int(
    os.environ.get("SFPCL_COMMUNICATION_JOB_LEASE_SECONDS", "300")
)
COMMUNICATION_JOB_BATCH_LIMIT = int(
    os.environ.get("SFPCL_COMMUNICATION_JOB_BATCH_LIMIT", "100")
)
COMMUNICATION_EMAIL_ADAPTER = os.environ.get(
    "SFPCL_COMMUNICATION_EMAIL_ADAPTER",
    "sfpcl_credit.communications.adapters.ManualEmailDeliveryAdapter",
)
COMMUNICATION_SMS_ADAPTER = os.environ.get(
    "SFPCL_COMMUNICATION_SMS_ADAPTER",
    "sfpcl_credit.communications.adapters.ManualSmsDeliveryAdapter",
)
CELERY_BEAT_SCHEDULE = {
    "communications-dispatch-due-jobs": {
        "task": "communications.dispatch_due_jobs",
        "schedule": float(
            os.environ.get("SFPCL_COMMUNICATION_DISPATCH_INTERVAL_SECONDS", "60")
        ),
    }
}

AUTH_ACCESS_TOKEN_MINUTES = 15
AUTH_REFRESH_TOKEN_HOURS = 24

# Under `manage.py test` only: Django's documented test-speed optimization.
# Most test setUps create users and log in through the API; PBKDF2's 720k
# iterations per hash dominated suite time (~2s/test). Runtime behavior
# (runserver, e2e servers, seed commands) keeps the default PBKDF2 hasher.
if "test" in sys.argv:
    PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

DOCUMENT_STORAGE_ROOT = os.environ.get("SFPCL_DOCUMENT_STORAGE_ROOT") or (
    BASE_DIR / "local-document-storage"
)
