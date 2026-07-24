import os
from urllib.parse import urlsplit

from django.core.exceptions import ImproperlyConfigured

from sfpcl_credit.config.settings import *  # noqa: F403
from sfpcl_credit.shared.key_configuration import (
    FieldKeyConfigurationError,
    validate_field_key_configuration,
)


DEBUG = False
DEPLOYMENT_ENVIRONMENT = "production"
IS_PRODUCTION = True
ENABLE_DEMO_SURFACES = False
INSTALLED_APPS = [  # noqa: F405
    app for app in INSTALLED_APPS if app != "sfpcl_credit.tracer"  # noqa: F405
]

_required_runtime_environment = {
    "SFPCL_SECRET_KEY",
    "SFPCL_JWT_SIGNING_KEY",
    "SFPCL_ALLOWED_HOSTS",
    "SFPCL_CORS_ORIGINS",
    "SFPCL_CSRF_TRUSTED_ORIGINS",
}
_missing_runtime_environment = sorted(
    name for name in _required_runtime_environment if not os.environ.get(name)
)
if _missing_runtime_environment:
    raise ImproperlyConfigured(
        "Production security configuration requires explicit environment values: "
        + ", ".join(_missing_runtime_environment)
    )

if len(SECRET_KEY) < 32:  # noqa: F405
    raise ImproperlyConfigured(
        "SFPCL_SECRET_KEY must contain at least 32 characters in production"
    )
JWT_SIGNING_KEY = os.environ["SFPCL_JWT_SIGNING_KEY"]
if len(JWT_SIGNING_KEY) < 32:
    raise ImproperlyConfigured(
        "SFPCL_JWT_SIGNING_KEY must contain at least 32 characters in production"
    )

ALLOWED_HOSTS = env_csv("SFPCL_ALLOWED_HOSTS", [])  # noqa: F405
if not ALLOWED_HOSTS or any(  # noqa: F405
    host == "*" or host.startswith(".") or host in {"localhost", "127.0.0.1", "::1"}
    for host in ALLOWED_HOSTS  # noqa: F405
):
    raise ImproperlyConfigured(
        "SFPCL_ALLOWED_HOSTS must contain explicit non-local production hosts"
    )

CORS_ALLOWED_ORIGINS = env_csv("SFPCL_CORS_ORIGINS", [])  # noqa: F405
CSRF_TRUSTED_ORIGINS = env_csv("SFPCL_CSRF_TRUSTED_ORIGINS", [])  # noqa: F405
for environment_name, origins in (
    ("SFPCL_CORS_ORIGINS", CORS_ALLOWED_ORIGINS),
    ("SFPCL_CSRF_TRUSTED_ORIGINS", CSRF_TRUSTED_ORIGINS),
):
    if not origins or any(
        urlsplit(origin).scheme != "https"
        or not urlsplit(origin).hostname
        or urlsplit(origin).hostname in {"localhost", "127.0.0.1", "::1"}
        for origin in origins
    ):
        raise ImproperlyConfigured(
            f"{environment_name} must contain explicit HTTPS production origins"
        )

CORS_ALLOW_ALL_ORIGINS = False
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

_REQUIRED_FIELD_KEY_ENVIRONMENT = {
    "SFPCL_FIELD_ENCRYPTION_CURRENT_VERSION",
    "SFPCL_FIELD_ENCRYPTION_KEY_REF",
    "SFPCL_FIELD_ENCRYPTION_KEYS",
    "SFPCL_FIELD_LOOKUP_KEY",
}
_missing_field_key_environment = sorted(
    name for name in _REQUIRED_FIELD_KEY_ENVIRONMENT if not os.environ.get(name)
)
if _missing_field_key_environment:
    raise ImproperlyConfigured(
        "Production field encryption requires explicit environment secrets: "
        + ", ".join(_missing_field_key_environment)
    )

try:
    validate_field_key_configuration(
        current_version=FIELD_ENCRYPTION_CURRENT_VERSION,  # noqa: F405
        previous_versions=FIELD_ENCRYPTION_PREVIOUS_VERSIONS,  # noqa: F405
        keys=FIELD_ENCRYPTION_KEYS,  # noqa: F405
        lookup_key=FIELD_LOOKUP_KEY,  # noqa: F405
        key_reference=FIELD_ENCRYPTION_KEY_REF,  # noqa: F405
    )
except FieldKeyConfigurationError as exc:
    raise ImproperlyConfigured(str(exc)) from exc

_secret_values = {
    os.environ["SFPCL_SECRET_KEY"],
    os.environ["SFPCL_JWT_SIGNING_KEY"],
    os.environ["SFPCL_FIELD_LOOKUP_KEY"],
    *FIELD_ENCRYPTION_KEYS.values(),  # noqa: F405
}
if len(_secret_values) != 3 + len(FIELD_ENCRYPTION_KEYS):  # noqa: F405
    raise ImproperlyConfigured(
        "Django, JWT, and field encryption secrets must be separate"
    )
