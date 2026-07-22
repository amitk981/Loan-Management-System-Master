"""Pinned async-worker entry points; business policy stays in deep modules."""

from celery import shared_task
from django.utils import timezone

from sfpcl_credit.configurations.modules.interest_rate_configuration import (
    run_due_current_rate_projections,
)
from sfpcl_credit.communications.modules.communication_dispatcher import (
    CommunicationDispatcher,
)
from sfpcl_credit.defaults.modules.default_workflow import DefaultWorkflow
from sfpcl_credit.processes.communication_delivery import (
    execute_communication_job,
)


@shared_task(name="communications.execute_job")
def execute_communication_delivery_job(job_id):
    return CommunicationDispatcher.execute_task(
        job_id, executor=execute_communication_job
    )


@shared_task(name="communications.dispatch_due_jobs")
def dispatch_due_communication_jobs():
    return CommunicationDispatcher.run_due_jobs(
        executor=execute_communication_delivery_job
    )


@shared_task(name="configurations.publish_due_current_rates")
def dispatch_due_current_rate_projections():
    projections = run_due_current_rate_projections(limit=100)
    return {
        "processed_count": len(projections),
        "loan_account_ids": [
            str(projection.loan_account_id) for projection in projections
        ],
    }


@shared_task(name="defaults.process_grace_expiries")
def dispatch_default_grace_expiries():
    return DefaultWorkflow.process_grace_expiries(
        as_of_date=timezone.localdate(), actor=None, limit=100
    )


__all__ = [
    "dispatch_due_communication_jobs",
    "dispatch_due_current_rate_projections",
    "dispatch_default_grace_expiries",
    "execute_communication_delivery_job",
]
