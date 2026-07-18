"""Thin composition entry point for communications-owned job execution."""

from sfpcl_credit.communications.modules.communication_dispatcher import (
    CommunicationDispatcher,
)
from sfpcl_credit.processes.disbursement_advice_delivery import (
    execute_disbursement_advice_job,
)


def execute_communication_job(job_id, *, adapter=None):
    return CommunicationDispatcher.execute_job(
        job_id,
        adapter=adapter,
        advice_executor=execute_disbursement_advice_job,
    )


__all__ = ["execute_communication_job"]
