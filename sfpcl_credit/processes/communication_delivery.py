"""Top-level execution coordinator for generic communications-owned jobs."""

from sfpcl_credit.communications.adapters import (
    configured_email_delivery_adapter,
    configured_sms_delivery_adapter,
)
from sfpcl_credit.communications.models import Communication, CommunicationDeliveryJob
from sfpcl_credit.communications.modules.communication_dispatcher import (
    CommunicationDispatcher,
)
from sfpcl_credit.processes.disbursement_advice_delivery import (
    execute_disbursement_advice_job,
)


def execute_communication_job(job_id, *, adapter=None):
    job = CommunicationDeliveryJob.objects.only("job_kind").get(pk=job_id)
    if job.job_kind == CommunicationDeliveryJob.KIND_ADVICE:
        adapter = adapter or configured_email_delivery_adapter()
        return execute_disbursement_advice_job(job_id, adapter=adapter)
    if adapter is None:
        channel = Communication.objects.only("channel").get(
            pk=job.communication_id
        ).channel
        adapter = (
            configured_sms_delivery_adapter()
            if channel == Communication.CHANNEL_SMS
            else configured_email_delivery_adapter()
        )
    result = CommunicationDispatcher.execute_generic_job(job_id, adapter=adapter)
    return {
        "communication_job_id": str(result.pk),
        "communication_id": str(result.communication_id),
        "delivery_status": result.status,
        "attempts": result.attempts,
    }


__all__ = ["execute_communication_job"]
