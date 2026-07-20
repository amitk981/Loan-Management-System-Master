"""Thin composition entry point for communications-owned job execution."""

from sfpcl_credit.communications.modules.communication_dispatcher import (
    CommunicationDispatcher,
)
from sfpcl_credit.monitoring.modules.reminder_engine import ReminderEngine
from sfpcl_credit.processes.disbursement_advice_delivery import (
    execute_disbursement_advice_job,
)


def execute_communication_job(job_id, *, adapter=None):
    cancelled = ReminderEngine.cancel_unserviceable_delivery(
        communication_job_id=job_id
    )
    if cancelled is not None:
        return cancelled
    return CommunicationDispatcher.execute_job(
        job_id,
        adapter=adapter,
        advice_executor=execute_disbursement_advice_job,
    )


__all__ = ["execute_communication_job"]
