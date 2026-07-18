"""Pinned async-worker entry points; business policy stays in deep modules."""

from celery import shared_task

from sfpcl_credit.communications.modules.communication_dispatcher import (
    CommunicationDispatcher,
)
from sfpcl_credit.processes.communication_delivery import (
    execute_communication_job,
)


@shared_task(name="communications.execute_job")
def execute_communication_delivery_job(job_id):
    execute_communication_job(job_id)
    evidence = CommunicationDispatcher.job_evidence(job_id=job_id, limit=1)[0]
    return CommunicationDispatcher._task_evidence(evidence)


@shared_task(name="communications.dispatch_due_jobs")
def dispatch_due_communication_jobs():
    return CommunicationDispatcher._run_due_jobs(
        executor=execute_communication_delivery_job
    )


__all__ = [
    "dispatch_due_communication_jobs",
    "execute_communication_delivery_job",
]
