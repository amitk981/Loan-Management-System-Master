"""Django and asynchronous-worker configuration for the SFPCL backend."""

from sfpcl_credit.config.celery import app as celery_app


__all__ = ["celery_app"]
