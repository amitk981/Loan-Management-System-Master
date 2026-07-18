"""Top-level process composition for communications-owned advice jobs."""

from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import transaction

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.communications.modules.communication_dispatcher import (
    AdviceFinalizationRequest,
    CommunicationDeliveryFailed,
    CommunicationDispatcher,
    CommunicationDispatchConflict,
)
from sfpcl_credit.disbursements.modules import disbursement_advice as advice_owner
from sfpcl_credit.disbursements.modules.disbursement_advice import (
    DisbursementAdviceConflict,
    DisbursementAdviceDeliveryFailed,
)
from sfpcl_credit.identity.models import User


@dataclass(frozen=True)
class _WorkerRequest:
    request_id: str
    ip_address: str
    user_agent: str

    @property
    def headers(self):
        return {"X-Request-ID": self.request_id, "User-Agent": self.user_agent}

    @property
    def META(self):
        return {"REMOTE_ADDR": self.ip_address}


def execute_disbursement_advice_job(job_id, *, adapter=None):
    execution = CommunicationDispatcher.start_job(job_id)
    if execution.status == "sent":
        return _serialize(execution.job_id, "sent", execution.attempts)
    actor = User.objects.get(pk=execution.actor_id)
    request = _WorkerRequest(
        request_id=execution.request_id,
        ip_address=execution.ip_address,
        user_agent=execution.user_agent,
    )
    try:
        result = send_disbursement_advice_now(
            actor=actor,
            disbursement_id=execution.related_entity_id,
            payload={
                "channel": "email",
                "recipient_email": execution.recipient_address,
            },
            request=request,
            adapter=adapter,
        )
    except DisbursementAdviceDeliveryFailed as exc:
        job = CommunicationDispatcher.defer_job(
            execution.job_id, exc.failure_code
        )
        return _serialize(job.pk, job.status, job.attempts)
    except TimeoutError:
        job = CommunicationDispatcher.defer_job(
            execution.job_id, "provider_timeout"
        )
        return _serialize(job.pk, job.status, job.attempts)
    except Exception:
        CommunicationDispatcher.defer_job(execution.job_id, "worker_crash")
        raise
    job = CommunicationDispatcher.complete_job(execution.job_id)
    return {
        **_serialize(job.pk, job.status, job.attempts),
        "disbursement_advice_communication_id": result[
            "disbursement_advice_communication_id"
        ],
    }


def queue_disbursement_advice(
    *, actor, disbursement_id, payload, idempotency_key=None, request=None
):
    key = CommunicationDispatcher._validated_idempotency_key(idempotency_key)
    cleaned = advice_owner._validate_payload(payload)
    with transaction.atomic():
        context = advice_owner._locked_advice_context(actor, disbursement_id)
        try:
            advice_owner._validate_request_context(context, cleaned)
        except ValidationError as exc:
            if CommunicationDispatcher.advice_is_queued(context.intent.pk):
                raise DisbursementAdviceConflict(
                    "The retained communication job conflicts with changed request facts."
                ) from exc
            raise
        if context.row.disbursement_advice_communication_id is None:
            advice_owner._require_pending_delivery(context)
        try:
            job = CommunicationDispatcher.queue_advice(
                context=context.dispatch_context,
                request=_finalization_request(request),
                idempotency_key=key,
            )
        except CommunicationDispatchConflict as exc:
            raise DisbursementAdviceConflict(str(exc)) from exc
        if job.status == "sent":
            return {
                **send_disbursement_advice_now(
                    actor=actor,
                    disbursement_id=disbursement_id,
                    payload=cleaned,
                    request=request,
                ),
                "communication_job_id": str(job.pk),
            }
        return {
            "disbursement_id": str(context.row.pk),
            "communication_job_id": str(job.pk),
            "delivery_status": job.status,
            "queued_at": advice_owner._iso(job.created_at),
        }


def send_disbursement_advice_now(
    *, actor, disbursement_id, payload, request=None, adapter=None
):
    cleaned = advice_owner._validate_payload(payload)
    with transaction.atomic():
        context = advice_owner._locked_advice_context(actor, disbursement_id)
        started_without_finalization = (
            context.row.disbursement_advice_communication_id is None
        )
        if started_without_finalization:
            advice_owner._validate_request_context(context, cleaned)
            advice_owner._require_pending_delivery(context)
    try:
        decision = CommunicationDispatcher.dispatch(
            context=context.dispatch_context,
            adapter=adapter,
        )
    except CommunicationDeliveryFailed as exc:
        raise DisbursementAdviceDeliveryFailed(
            str(exc), failure_code=exc.failure_code
        ) from exc
    except CommunicationDispatchConflict as exc:
        raise DisbursementAdviceConflict(str(exc)) from exc
    with transaction.atomic():
        context = advice_owner._locked_advice_context(actor, disbursement_id)
        try:
            decision = CommunicationDispatcher.dispatch(
                context=context.dispatch_context,
            )
        except CommunicationDispatchConflict as exc:
            raise DisbursementAdviceConflict(str(exc)) from exc
        is_replay = context.row.disbursement_advice_communication_id is not None
        if is_replay and started_without_finalization:
            raise DisbursementAdviceConflict(
                "Another caller finalized the accepted disbursement advice."
            )
        if not is_replay:
            advice_owner._validate_request_context(context, cleaned)
            advice_owner._require_pending_delivery(context)
        try:
            finalization = CommunicationDispatcher.finalize(
                context=context.dispatch_context,
                decision=decision,
                request=None if is_replay else _finalization_request(request),
            )
        except CommunicationDispatchConflict as exc:
            raise DisbursementAdviceConflict(str(exc)) from exc
        if is_replay:
            return advice_owner._current_replay(context, cleaned, finalization)
        return advice_owner._consume_finalization(context, finalization)


def _finalization_request(request):
    return AdviceFinalizationRequest(
        request_id=advice_owner._request_id(request),
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )


def _serialize(job_id, status, attempts):
    return {
        "communication_job_id": str(job_id),
        "delivery_status": status,
        "attempts": attempts,
    }


__all__ = [
    "execute_disbursement_advice_job",
    "queue_disbursement_advice",
    "send_disbursement_advice_now",
]
