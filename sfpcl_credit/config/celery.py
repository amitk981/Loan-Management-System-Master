import os

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sfpcl_credit.config.settings")

app = Celery("sfpcl_credit")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.imports = ("sfpcl_credit.processes.tasks",)


__all__ = ["app"]
