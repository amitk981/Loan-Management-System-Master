"""Pinned async-worker entry points; business policy stays in deep modules."""

try:
    from celery import shared_task
except ImportError:  # The orchestrator installs the newly pinned dependency.
    def shared_task(*decorator_args, **decorator_kwargs):
        del decorator_args, decorator_kwargs

        def decorate(function):
            return function

        return decorate

from sfpcl_credit.communications.modules.communication_dispatcher import (
    CommunicationDispatcher,
)
from sfpcl_credit.processes.disbursement_advice_delivery import (
    execute_disbursement_advice_job,
)


@shared_task(name="communications.dispatch_due_jobs")
def dispatch_due_communication_jobs():
    results = []
    for job_id in CommunicationDispatcher.retry_failed():
        results.append(execute_disbursement_advice_job(job_id))
    return results


__all__ = ["dispatch_due_communication_jobs"]
