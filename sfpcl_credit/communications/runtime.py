from django.db import transaction

from sfpcl_credit.config.celery import app


def enqueue_after_commit(job_id):
    frozen_job_id = str(job_id)

    def publish_communication_job():
        _publish_job(frozen_job_id)

    transaction.on_commit(publish_communication_job, robust=True)


def _publish_job(job_id):
    app.loader.import_default_modules()
    task = app.tasks["communications.execute_job"]
    task.signature(args=[job_id]).apply_async()


__all__ = ["enqueue_after_commit"]
