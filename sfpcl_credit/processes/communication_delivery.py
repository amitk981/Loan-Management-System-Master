"""Top-level execution coordinator for generic communications-owned jobs."""

from sfpcl_credit.communications.models import CommunicationDeliveryJob
from sfpcl_credit.communications.modules.communication_dispatcher import (
    CommunicationDispatcher,
)
from sfpcl_credit.processes.disbursement_advice_delivery import (
    execute_disbursement_advice_job,
)


def execute_communication_job(job_id, *, adapter=None):
    job = CommunicationDeliveryJob.objects.only("job_kind").get(pk=job_id)
    if job.job_kind == CommunicationDeliveryJob.KIND_ADVICE:
        return execute_disbursement_advice_job(job_id, adapter=adapter)
    result = CommunicationDispatcher.execute_generic_job(job_id, adapter=adapter)
    return {
        "communication_job_id": str(result.pk),
        "communication_id": str(result.communication_id),
        "delivery_status": result.status,
        "attempts": result.attempts,
    }


__all__ = ["execute_communication_job"]
