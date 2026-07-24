import os

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
