"""PostgreSQL-only settings for authoritative transaction/concurrency tests."""

import os

from sfpcl_credit.config.settings import *  # noqa: F403


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("SFPCL_POSTGRES_DB", "sfpcl_credit"),
        "USER": os.environ.get("SFPCL_POSTGRES_USER", os.environ.get("USER", "postgres")),
        "PASSWORD": os.environ.get("SFPCL_POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("SFPCL_POSTGRES_HOST", ""),
        "PORT": os.environ.get("SFPCL_POSTGRES_PORT", "5432"),
        "TEST": {
            "NAME": os.environ.get("SFPCL_POSTGRES_TEST_DB", "test_sfpcl_credit"),
        },
    }
}
