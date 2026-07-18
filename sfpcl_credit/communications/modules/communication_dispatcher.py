from dataclasses import dataclass
from datetime import date, datetime, timedelta
import hashlib
import json
import re
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import connection, transaction
from django.db.models import Q
from django.utils import timezone

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.communications.adapters import (
    EmailDeliveryPayload,
    EmailDeliveryResult,
    ManualEmailDeliveryAdapter,
    delivery_payload_digest,
    validate_delivery_result,
)
from sfpcl_credit.communications.models import (
    Communication,
    CommunicationDeliveryJob,
    CommunicationDeliveryOutbox,
    CommunicationProviderAttempt,
    ContentTemplate,
    DisbursementAdviceDeliveryReceipt,
    Notification,
)
from sfpcl_credit.communications.runtime import enqueue_after_commit
from sfpcl_credit.identity.models import AuditLog, User
from sfpcl_credit.workflows.events import record_workflow_event
from sfpcl_credit.workflows.models import WorkflowEvent


_TOKEN_RE = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")
_MASKED_REFERENCE_RE = re.compile(r"^\*{4,}[A-Za-z0-9]{4}$")
_SENSITIVE_VARIABLE_PARTS = (
    "aadhaar",
    "pan",
    "bank_account",
    "cheque",
    "ifsc",
    "ciphertext",
)
_ADVICE_ACTION = "disbursement.advice_sent"
_ADVICE_WORKFLOW = "DisbursementAdviceSent"
_GENERIC_ACTION = "communications.communication.created"
_USER_RECIPIENT_TYPES = {"user", "staff_user", "internal_user"}
_ROLE_RECIPIENT_TYPES = {"role", "role_code"}
_TEAM_RECIPIENT_TYPES = {"team", "team_code"}
_LEGACY_PROVENANCE_ADAPTER_KINDS = {
    "legacy:pre-outbox",
    "legacy:retained-outbox",
}


class CommunicationDispatchConflict(Exception):
    pass


class CommunicationDeliveryFailed(CommunicationDispatchConflict):
    def __init__(self, message, *, failure_code="provider_rejected"):
        super().__init__(message)
        self.failure_code = failure_code


@dataclass(frozen=True)
class AdviceDeliveryDecision:
    outbox_id: uuid.UUID
    advice_intent_id: uuid.UUID
    communication_id: uuid.UUID
    idempotency_key: str
    recipient_address: str
    recipient_digest: str
    template_id: uuid.UUID
    template_provenance_status: str
    template_code: str
    template_name: str
    template_type: str
    template_language_code: str | None
    template_audience: str
    template_version: str
    template_approval_status: str
    template_effective_from: date
    template_effective_to: date | None
    template_variables: tuple[str, ...]
    subject_template: str
    body_template: str
    template_checksum: str
    subject: str
    body: str
    payload_digest: str
    related_entity_type: str
    related_entity_id: uuid.UUID
    external_message_id: str
    delivery_status: str
    accepted_at: datetime


@dataclass(frozen=True)
class AdviceFinalizationRequest:
    request_id: str
    ip_address: str
    user_agent: str


@dataclass(frozen=True)
class AdviceFinalizationDecision:
    communication_id: uuid.UUID
    receipt_id: uuid.UUID
    action_id: uuid.UUID
    audit_id: uuid.UUID
    workflow_id: uuid.UUID
    delivery_evidence_digest: str
    delivery_status: str
    sent_at: datetime


@dataclass(frozen=True)
class FinalizedAdviceArtifact:
    outbox_id: uuid.UUID
    communication_id: uuid.UUID
    checksum_sha256: str
    body: bytes
    sent_at: datetime
    action_id: uuid.UUID
    audit_id: uuid.UUID
    workflow_id: uuid.UUID
    delivery_evidence_digest: str


def resolve_finalized_advice_artifact(*, context):
    """Resolve exact communications-owned terminal advice without dispatching."""
    outboxes = list(
        CommunicationDeliveryOutbox.objects.select_related(
            "accepted_provider_attempt", "delivery_receipt", "final_communication"
        )
        .filter(
            advice_intent=context.advice_intent_id,
            communication_id=context.communication_id,
        )
        .order_by("outbox_id")[:2]
    )
    if len(outboxes) != 1:
        return None
    outbox = outboxes[0]
    receipt = outbox.delivery_receipt
    communication = outbox.final_communication
    if receipt is None or communication is None:
        return None
    try:
        decision = CommunicationDispatcher._decision(outbox)
    except CommunicationDispatchConflict:
        return None
    if not (
        _receipt_matches(receipt, decision)
        and communication.pk == decision.communication_id
        and communication.related_entity_type == decision.related_entity_type
        and communication.related_entity_id == decision.related_entity_id
        and communication.recipient_party_type == "borrower"
        and communication.channel == "email"
        and communication.content_template_id == decision.template_id
        and communication.subject_snapshot == decision.subject
        and communication.body_snapshot == decision.body
        and communication.sent_at == decision.accepted_at
        and communication.delivery_status == "sent"
        and communication.external_message_id == decision.external_message_id
    ):
        return None
    try:
        finalization = _reconcile_finalization(
            context, receipt, decision, communication
        )
    except CommunicationDispatchConflict:
        return None
    body = f"{decision.subject}\n\n{decision.body}\n".encode("utf-8")
    return FinalizedAdviceArtifact(
        outbox_id=outbox.pk,
        communication_id=communication.pk,
        checksum_sha256=hashlib.sha256(body).hexdigest(),
        body=body,
        sent_at=communication.sent_at,
        action_id=finalization.action_id,
        audit_id=finalization.audit_id,
        workflow_id=finalization.workflow_id,
        delivery_evidence_digest=finalization.delivery_evidence_digest,
    )


@dataclass(frozen=True)
class DeliveryJobExecution:
    job_id: uuid.UUID
    job_kind: str
    communication_id: uuid.UUID
    actor_id: uuid.UUID
    related_entity_id: uuid.UUID
    recipient_address: str
    request_id: str
    ip_address: str
    user_agent: str
    attempts: int
    status: str
    claim_token: uuid.UUID | None


@dataclass(frozen=True)
class _PreparedAdvice:
    proposed: dict
    delivery_payload: EmailDeliveryPayload
    template: ContentTemplate


class CommunicationDispatcher:
    """Own template, render, durable outbox, and provider dispatch policy."""

    @classmethod
    def create_from_template(
        cls,
        *,
        actor,
        request,
        content_template_id,
        merge_data,
        related_entity_type,
        related_entity_id,
        recipient_party_type,
        recipient_party_id,
        recipient_address,
        channel,
        idempotency_key=None,
    ):
        with transaction.atomic():
            key = cls._validated_idempotency_key(idempotency_key)
            cls._lock_idempotency_key(key)
            template = cls._approved_effective_template(content_template_id)
            subject = cls._render_generic(
                template.subject_template, template.variables_json or [], merge_data
            )
            body = cls._render_generic(
                template.body_template, template.variables_json or [], merge_data
            )
            proposed_digest = cls._generic_payload_digest(
                communication_id=None,
                related_entity_type=related_entity_type,
                related_entity_id=related_entity_id,
                recipient_party_type=recipient_party_type,
                recipient_party_id=recipient_party_id,
                recipient_address=recipient_address,
                channel=channel,
                content_template_id=template.pk,
                subject=subject,
                body=body,
            )
            retained = (
                CommunicationDeliveryJob.objects.select_for_update(of=("self",))
                .filter(idempotency_key=key)
                .first()
            )
            if retained is not None:
                if not (
                    retained.job_kind == CommunicationDeliveryJob.KIND_GENERIC
                    and retained.actor_id == actor.pk
                    and retained.request_payload_digest == proposed_digest
                ):
                    raise CommunicationDispatchConflict(
                        "The idempotency key is already bound to another communication request."
                    )
                try:
                    return Communication.objects.get(pk=retained.communication_id)
                except Communication.DoesNotExist as exc:
                    raise CommunicationDispatchConflict(
                        "The retained communication job has no communication snapshot."
                    ) from exc
            row = Communication.objects.create(
                related_entity_type=related_entity_type,
                related_entity_id=related_entity_id,
                recipient_party_type=recipient_party_type,
                recipient_party_id=recipient_party_id,
                recipient_address=recipient_address,
                channel=channel,
                content_template=template,
                subject_snapshot=subject,
                body_snapshot=body,
                sent_by_user=actor,
                delivery_status=Communication.DELIVERY_PENDING,
            )
            cls._create_notification(row)
            cls._record_generic_audit(actor, request, row)
            return row

    @classmethod
    def send(
        cls,
        *,
        communication_id,
        idempotency_key,
        actor=None,
        request=None,
        _advice_context=None,
        _outbox=None,
    ):
        """Queue an existing communication through the canonical delivery seam."""
        key = cls._validated_idempotency_key(idempotency_key)
        if _advice_context is not None:
            return cls._send_advice_job(
                communication_id=communication_id,
                idempotency_key=key,
                context=_advice_context,
                outbox=_outbox,
                request=request,
            )
        with transaction.atomic():
            cls._lock_idempotency_key(key)
            try:
                row = Communication.objects.select_for_update(of=("self",)).select_related(
                    "sent_by_user__primary_role"
                ).get(pk=communication_id)
            except (Communication.DoesNotExist, ValueError, TypeError) as exc:
                raise CommunicationDispatchConflict(
                    "The communication was not found or conflicts with retained delivery truth."
                ) from exc
            operator = actor or row.sent_by_user
            if operator is None or row.sent_by_user_id != operator.pk:
                raise CommunicationDispatchConflict(
                    "The communication actor conflicts with retained delivery truth."
                )
            payload_digest = cls._generic_payload_digest_from_row(row)
            retained = (
                CommunicationDeliveryJob.objects.select_for_update(of=("self",))
                .filter(Q(idempotency_key=key) | Q(communication_id=row.pk))
                .first()
            )
            if retained is not None:
                cls._require_generic_job_match(
                    retained, row, operator, key, payload_digest
                )
                return row
            role = getattr(operator, "primary_role", None)
            request_id = ""
            if request is not None:
                request_id = request.headers.get("X-Request-ID", "").strip()
            job = CommunicationDeliveryJob.objects.create(
                communication_id=row.pk,
                job_kind=CommunicationDeliveryJob.KIND_GENERIC,
                idempotency_key=key,
                actor_id=operator.pk,
                actor_role_code=getattr(role, "role_code", None) or "unassigned",
                actor_team_codes=sorted(operator.team_codes()),
                request_id=request_id or f"req_communication_{uuid.uuid4().hex}",
                ip_address=request_ip(request) if request else "",
                user_agent=request_user_agent(request) if request else "",
                request_payload_digest=payload_digest,
            )
            enqueue_after_commit(job.pk)
            return row

    @classmethod
    def _send_advice_job(
        cls, *, communication_id, idempotency_key, context, outbox, request
    ):
        if not (
            outbox is not None
            and outbox.communication_id == communication_id
            and outbox.advice_intent == context.advice_intent_id
            and outbox.template_provenance_status
            == CommunicationDeliveryOutbox.PROVENANCE_VERIFIED
            and outbox.template_provenance_origin
            == CommunicationDeliveryOutbox.PROVENANCE_ORIGIN_FROZEN
        ):
            raise CommunicationDispatchConflict(
                "Legacy-partial or mismatched advice cannot be attached to a delivery job."
            )
        retained = (
            CommunicationDeliveryJob.objects.select_for_update()
            .filter(
                Q(idempotency_key=idempotency_key)
                | Q(communication_id=communication_id)
                | Q(advice_intent_id=context.advice_intent_id)
            )
            .first()
        )
        if retained is not None:
            cls._require_job_match(retained, context, outbox, idempotency_key)
            return retained
        job = CommunicationDeliveryJob.objects.create(
            outbox=outbox,
            communication_id=communication_id,
            advice_intent_id=context.advice_intent_id,
            job_kind=CommunicationDeliveryJob.KIND_ADVICE,
            idempotency_key=idempotency_key,
            actor_id=context.actor_id,
            actor_role_code=context.actor_role_code,
            actor_team_codes=list(context.actor_team_codes),
            request_id=request.request_id,
            ip_address=request.ip_address,
            user_agent=request.user_agent,
            request_payload_digest=outbox.payload_digest,
        )
        enqueue_after_commit(job.pk)
        return job

    @staticmethod
    def _validated_idempotency_key(value):
        key = value.strip() if isinstance(value, str) else ""
        if not key:
            raise ValidationError(
                {"idempotency_key": "Idempotency-Key header is required."}
            )
        if len(key) > 255:
            raise ValidationError(
                {"idempotency_key": "Idempotency-Key must be at most 255 characters."}
            )
        return key

    @staticmethod
    def _lock_idempotency_key(key):
        if connection.vendor != "postgresql":
            return
        digest = hashlib.sha256(key.encode()).digest()[:8]
        lock_id = int.from_bytes(digest, byteorder="big", signed=True)
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_xact_lock(%s)", [lock_id])

    @classmethod
    def _generic_payload_digest_from_row(cls, row):
        return cls._generic_payload_digest(
            communication_id=None,
            related_entity_type=row.related_entity_type,
            related_entity_id=row.related_entity_id,
            recipient_party_type=row.recipient_party_type,
            recipient_party_id=row.recipient_party_id,
            recipient_address=row.recipient_address,
            channel=row.channel,
            content_template_id=row.content_template_id,
            subject=row.subject_snapshot,
            body=row.body_snapshot,
        )

    @staticmethod
    def _generic_payload_digest(**facts):
        canonical = {
            key: str(value) if isinstance(value, uuid.UUID) else value
            for key, value in facts.items()
            if key != "communication_id"
        }
        return hashlib.sha256(
            json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

    @staticmethod
    def _require_generic_job_match(job, row, actor, key, payload_digest):
        if not (
            job.job_kind == CommunicationDeliveryJob.KIND_GENERIC
            and job.outbox_id is None
            and job.advice_intent_id is None
            and job.communication_id == row.pk
            and job.idempotency_key == key
            and job.actor_id == actor.pk
            and job.request_payload_digest == payload_digest
        ):
            raise CommunicationDispatchConflict(
                "The idempotency key is already bound to another communication request."
            )

    @staticmethod
    def _approved_effective_template(content_template_id):
        try:
            template = ContentTemplate.objects.select_for_update().get(
                content_template_id=content_template_id
            )
        except ContentTemplate.DoesNotExist as exc:
            raise ValidationError(
                {"content_template_id": "Content template was not found."}
            ) from exc
        today = timezone.localdate()
        if template.approval_status != ContentTemplate.STATUS_APPROVED:
            raise ValidationError(
                {"content_template_id": "Content template must be approved."}
            )
        if template.effective_from > today:
            raise ValidationError(
                {"content_template_id": "Content template is not effective yet."}
            )
        if template.effective_to and template.effective_to < today:
            raise ValidationError(
                {"content_template_id": "Content template is no longer effective."}
            )
        return template

    @staticmethod
    def _render_generic(source, declared_variables, merge_data):
        if source is None:
            return None
        declared = set(declared_variables)
        provided = set(merge_data)
        if declared - provided:
            missing = ", ".join(sorted(declared - provided))
            raise ValidationError({"merge_data": f"Missing template variables: {missing}."})
        if provided - declared:
            extra = ", ".join(sorted(provided - declared))
            raise ValidationError({"merge_data": f"Unknown template variables: {extra}."})
        return _TOKEN_RE.sub(lambda match: str(merge_data[match.group(1)]), source)

    @staticmethod
    def _create_notification(row):
        party_type = row.recipient_party_type.strip().lower()
        recipient = None
        if party_type in _USER_RECIPIENT_TYPES and row.recipient_party_id:
            user = User.objects.filter(pk=row.recipient_party_id).first()
            recipient = {"recipient_user": user} if user else None
        elif party_type in _ROLE_RECIPIENT_TYPES and row.recipient_address:
            recipient = {"recipient_role_code": row.recipient_address.strip()}
        elif party_type in _TEAM_RECIPIENT_TYPES and row.recipient_address:
            recipient = {"recipient_team_code": row.recipient_address.strip()}
        if recipient is None:
            return
        categories = {
            "loan_application": "Application",
            "loan_account": "Repayment",
            "document": "Documents",
            "compliance_task": "Compliance",
        }
        urls = {
            "loan_application": "/applications/detail",
            "loan_account": "/loan-accounts/detail",
            "document": "/documentation",
            "compliance_task": "/compliance",
        }
        Notification.objects.create(
            communication=row,
            notification_type=(
                "application"
                if row.related_entity_type == "loan_application"
                else row.related_entity_type or "system"
            ),
            category=categories.get(row.related_entity_type, "System"),
            severity=Notification.SEVERITY_INFO,
            title=row.subject_snapshot or "Communication notification",
            message=row.body_snapshot,
            related_entity_type=row.related_entity_type,
            related_entity_id=row.related_entity_id,
            action_label="Open related record",
            action_url=urls.get(row.related_entity_type, "/notifications"),
            sender_user=row.sent_by_user,
            **recipient,
        )

    @staticmethod
    def _record_generic_audit(actor, request, row):
        AuditLog.objects.create(
            actor_user=actor,
            actor_type="user",
            action=_GENERIC_ACTION,
            entity_type="communication",
            entity_id=row.pk,
            old_value_json=None,
            new_value_json={
                "communication_id": str(row.pk),
                "related_entity_type": row.related_entity_type,
                "related_entity_id": str(row.related_entity_id),
                "recipient_party_type": row.recipient_party_type,
                "recipient_party_id": str(row.recipient_party_id) if row.recipient_party_id else None,
                "recipient_address": row.recipient_address,
                "channel": row.channel,
                "content_template_id": str(row.content_template_id),
                "sent_by_user_id": str(row.sent_by_user_id),
                "delivery_status": row.delivery_status,
            },
            ip_address=request_ip(request),
            user_agent=request_user_agent(request),
        )

    @classmethod
    def queue_advice(cls, *, context, request, idempotency_key):
        """Freeze one advice outbox and durable worker job without provider I/O."""
        key = cls._validated_idempotency_key(idempotency_key)
        with transaction.atomic():
            cls._lock_idempotency_key(key)
            job = (
                CommunicationDeliveryJob.objects.select_for_update(of=("self",))
                .select_related("outbox")
                .filter(advice_intent_id=context.advice_intent_id)
                .first()
            )
            if job is not None and job.status == CommunicationDeliveryJob.STATUS_SENT:
                if not (
                    job.outbox.delivery_status
                    == CommunicationDeliveryOutbox.DELIVERY_SENT
                    and job.outbox.delivery_receipt_id
                    and job.outbox.final_communication_id
                ):
                    raise CommunicationDispatchConflict(
                        "The terminal communication job lacks final delivery evidence."
                    )
                cls._require_context_identity(job.outbox, context)
                cls._require_job_match(job, context, job.outbox, key)
                return job
            prepared = cls._prepare(context, key)
            outbox = cls._freeze_or_reconcile(context, prepared)
            expected = {
                "outbox_id": outbox.pk,
                "actor_id": context.actor_id,
                "actor_role_code": context.actor_role_code,
                "actor_team_codes": list(context.actor_team_codes),
                "request_payload_digest": outbox.payload_digest,
            }
            if job is None:
                return cls.send(
                    communication_id=context.communication_id,
                    idempotency_key=key,
                    request=request,
                    _advice_context=context,
                    _outbox=outbox,
                )
            if any(getattr(job, field) != value for field, value in expected.items()):
                raise CommunicationDispatchConflict(
                    "The retained communication job conflicts with current advice facts."
                )
            cls._require_job_match(job, context, outbox, key)
            return job

    @staticmethod
    def _require_job_match(job, context, outbox, idempotency_key=None):
        if not (
            job.outbox_id == outbox.pk
            and job.communication_id == context.communication_id
            and job.actor_id == context.actor_id
            and job.actor_role_code == context.actor_role_code
            and job.actor_team_codes == list(context.actor_team_codes)
            and job.request_payload_digest == outbox.payload_digest
            and job.job_kind == CommunicationDeliveryJob.KIND_ADVICE
            and (
                idempotency_key is None or job.idempotency_key == idempotency_key
            )
        ):
            raise CommunicationDispatchConflict(
                "The retained communication job conflicts with current advice facts."
            )

    @staticmethod
    def advice_is_queued(advice_intent_id):
        return CommunicationDeliveryJob.objects.filter(
            advice_intent_id=advice_intent_id
        ).exists()

    @classmethod
    def start_job(cls, job_id):
        with transaction.atomic():
            job = (
                CommunicationDeliveryJob.objects.select_for_update(of=("self",))
                .select_related("outbox")
                .get(pk=job_id)
            )
            if job.status == CommunicationDeliveryJob.STATUS_SENT:
                return cls._job_execution(job)
            if job.status not in {
                CommunicationDeliveryJob.STATUS_QUEUED,
                CommunicationDeliveryJob.STATUS_RETRYING,
            } or job.next_attempt_at > timezone.now():
                raise CommunicationDispatchConflict(
                    "The communication job is not ready for execution."
                )
            job.status = CommunicationDeliveryJob.STATUS_RUNNING
            job.attempts += 1
            started_at = timezone.now()
            job.started_at = started_at
            job.claim_token = uuid.uuid4()
            job.lease_expires_at = started_at + timedelta(
                seconds=settings.COMMUNICATION_JOB_LEASE_SECONDS
            )
            job.last_failure_code = ""
            job.save(
                update_fields=[
                    "status",
                    "attempts",
                    "started_at",
                    "claim_token",
                    "lease_expires_at",
                    "last_failure_code",
                ]
            )
            return cls._job_execution(job)

    @staticmethod
    def retry_failed(*, actor=None, limit=100):
        del actor
        bounded_limit = max(1, min(int(limit), settings.COMMUNICATION_JOB_BATCH_LIMIT))
        now = timezone.now()
        eligible = Q(job_kind=CommunicationDeliveryJob.KIND_GENERIC) | Q(
            job_kind=CommunicationDeliveryJob.KIND_ADVICE,
            outbox__template_provenance_status=(
                CommunicationDeliveryOutbox.PROVENANCE_VERIFIED
            ),
            outbox__template_provenance_origin=(
                CommunicationDeliveryOutbox.PROVENANCE_ORIGIN_FROZEN
            ),
        )
        with transaction.atomic():
            stale = list(
                CommunicationDeliveryJob.objects.select_for_update(of=("self",))
                .filter(
                    eligible,
                    status=CommunicationDeliveryJob.STATUS_RUNNING,
                    lease_expires_at__lte=now,
                )
                .order_by("lease_expires_at", "communication_job_id")[:bounded_limit]
            )
            for job in stale:
                job.status = CommunicationDeliveryJob.STATUS_RETRYING
                job.next_attempt_at = now
                job.last_failure_code = "worker_crash"
                job.claim_token = None
                job.lease_expires_at = None
                job.recovery_count += 1
                job.last_recovered_at = now
                job.save(
                    update_fields=[
                        "status",
                        "next_attempt_at",
                        "last_failure_code",
                        "claim_token",
                        "lease_expires_at",
                        "recovery_count",
                        "last_recovered_at",
                    ]
                )
            return list(
                CommunicationDeliveryJob.objects.filter(
                    eligible,
                    status__in=(
                        CommunicationDeliveryJob.STATUS_QUEUED,
                        CommunicationDeliveryJob.STATUS_RETRYING,
                    ),
                    next_attempt_at__lte=now,
                )
                .order_by("next_attempt_at", "communication_job_id")
                .values_list("communication_job_id", flat=True)[:bounded_limit]
            )

    @staticmethod
    def job_evidence(*, job_id=None, limit=100):
        bounded_limit = max(1, min(int(limit), settings.COMMUNICATION_JOB_BATCH_LIMIT))
        rows = CommunicationDeliveryJob.objects.select_related("outbox")
        if job_id is not None:
            rows = rows.filter(pk=job_id)
        rows = rows.order_by("next_attempt_at", "communication_job_id")[:bounded_limit]
        evidence = []
        for job in rows:
            legacy_blocked = bool(
                job.job_kind == CommunicationDeliveryJob.KIND_ADVICE
                and (
                    job.outbox is None
                    or job.outbox.template_provenance_status
                    != CommunicationDeliveryOutbox.PROVENANCE_VERIFIED
                    or job.outbox.template_provenance_origin
                    != CommunicationDeliveryOutbox.PROVENANCE_ORIGIN_FROZEN
                )
            )
            evidence.append(
                {
                    "communication_job_id": str(job.pk),
                    "job_kind": job.job_kind,
                    "status": "operator_blocked" if legacy_blocked else job.status,
                    "attempts": job.attempts,
                    "max_attempts": job.max_attempts,
                    "next_attempt_at": _iso_or_none(job.next_attempt_at),
                    "started_at": _iso_or_none(job.started_at),
                    "completed_at": _iso_or_none(job.completed_at),
                    "lease_expires_at": _iso_or_none(job.lease_expires_at),
                    "recovery_count": job.recovery_count,
                    "last_recovered_at": _iso_or_none(job.last_recovered_at),
                    "last_failure_code": (
                        "legacy_provenance_blocked"
                        if legacy_blocked
                        else job.last_failure_code
                    ),
                    "recovered": job.recovery_count > 0,
                    "operator_attention_required": (
                        legacy_blocked
                        or job.status == CommunicationDeliveryJob.STATUS_FAILED
                    ),
                }
            )
        return evidence

    @classmethod
    def complete_job(cls, job_id, *, claim_token):
        with transaction.atomic():
            job = (
                CommunicationDeliveryJob.objects.select_for_update(of=("self",))
                .select_related("outbox")
                .get(pk=job_id)
            )
            outbox = job.outbox
            advice_complete = bool(
                outbox
                and outbox.delivery_status == CommunicationDeliveryOutbox.DELIVERY_SENT
                and outbox.delivery_receipt_id
                and outbox.final_communication_id
            )
            generic_complete = bool(
                job.job_kind == CommunicationDeliveryJob.KIND_GENERIC
                and Communication.objects.filter(
                    pk=job.communication_id, delivery_status="sent", sent_at__isnull=False
                ).exists()
            )
            if not (
                job.status == CommunicationDeliveryJob.STATUS_RUNNING
                and job.claim_token == claim_token
                and (advice_complete or generic_complete)
            ):
                raise CommunicationDispatchConflict(
                    "The communication job cannot complete without final delivery evidence."
                )
            job.status = CommunicationDeliveryJob.STATUS_SENT
            job.completed_at = timezone.now()
            job.last_failure_code = ""
            job.claim_token = None
            job.lease_expires_at = None
            job.save(
                update_fields=[
                    "status",
                    "completed_at",
                    "last_failure_code",
                    "claim_token",
                    "lease_expires_at",
                ]
            )
            return job

    @classmethod
    def defer_job(cls, job_id, failure_code, *, claim_token):
        safe_codes = {"provider_timeout", "provider_rejected", "provider_malformed", "worker_crash"}
        if failure_code not in safe_codes:
            failure_code = "worker_crash"
        with transaction.atomic():
            job = CommunicationDeliveryJob.objects.select_for_update().get(pk=job_id)
            if not (
                job.status == CommunicationDeliveryJob.STATUS_RUNNING
                and job.claim_token == claim_token
            ):
                raise CommunicationDispatchConflict(
                    "The communication worker no longer owns this job claim."
                )
            exhausted = job.attempts >= job.max_attempts
            job.status = (
                CommunicationDeliveryJob.STATUS_FAILED
                if exhausted
                else CommunicationDeliveryJob.STATUS_RETRYING
            )
            job.last_failure_code = failure_code
            job.completed_at = timezone.now() if exhausted else None
            job.claim_token = None
            job.lease_expires_at = None
            if not exhausted:
                seconds = min(900, 60 * (2 ** (job.attempts - 1)))
                job.next_attempt_at = timezone.now() + timedelta(seconds=seconds)
            job.save(
                update_fields=[
                    "status",
                    "last_failure_code",
                    "completed_at",
                    "next_attempt_at",
                    "claim_token",
                    "lease_expires_at",
                ]
            )
            if exhausted:
                Notification.objects.get_or_create(
                    notification_type="communication_job_failed",
                    related_entity_type="communication_job",
                    related_entity_id=job.pk,
                    defaults={
                        "category": "Operations",
                        "severity": Notification.SEVERITY_URGENT,
                        "title": "Communication delivery needs attention",
                        "message": "A communication job exhausted its safe retry limit.",
                        "action_label": "Review communication job",
                        "action_url": "/notifications",
                        "recipient_user_id": job.actor_id,
                    },
                )
            return job

    @staticmethod
    def _job_execution(job):
        if job.outbox_id:
            related_entity_id = job.outbox.related_entity_id
            recipient_address = job.outbox.recipient_address
        else:
            communication = Communication.objects.get(pk=job.communication_id)
            related_entity_id = communication.related_entity_id
            recipient_address = communication.recipient_address or ""
        return DeliveryJobExecution(
            job_id=job.pk,
            job_kind=job.job_kind,
            communication_id=job.communication_id,
            actor_id=job.actor_id,
            related_entity_id=related_entity_id,
            recipient_address=recipient_address,
            request_id=job.request_id,
            ip_address=job.ip_address,
            user_agent=job.user_agent,
            attempts=job.attempts,
            status=job.status,
            claim_token=job.claim_token,
        )

    @classmethod
    def execute_generic_job(cls, job_id, *, adapter=None):
        execution = cls.start_job(job_id)
        if execution.job_kind != CommunicationDeliveryJob.KIND_GENERIC:
            raise CommunicationDispatchConflict(
                "The communication job requires its business process coordinator."
            )
        if execution.status == CommunicationDeliveryJob.STATUS_SENT:
            return CommunicationDeliveryJob.objects.get(pk=job_id)
        row = Communication.objects.get(pk=execution.communication_id)
        payload = EmailDeliveryPayload(
            communication_id=row.pk,
            recipient_email=row.recipient_address or "",
            subject=row.subject_snapshot or "",
            body_text=row.body_snapshot,
            related_entity_type=row.related_entity_type,
            related_entity_id=row.related_entity_id,
        )
        job = CommunicationDeliveryJob.objects.get(pk=job_id)
        if job.provider_external_message_id:
            result = EmailDeliveryResult(
                external_message_id=job.provider_external_message_id,
                delivery_status=job.provider_delivery_status,
                accepted_at=job.provider_accepted_at,
            )
            validate_delivery_result(result)
        else:
            delivery_adapter = adapter or ManualEmailDeliveryAdapter()
            try:
                result = delivery_adapter.send_email(payload, job.idempotency_key)
            except TimeoutError:
                return cls.defer_job(
                    job_id, "provider_timeout", claim_token=execution.claim_token
                )
            except (TypeError, ValueError):
                return cls.defer_job(
                    job_id, "provider_rejected", claim_token=execution.claim_token
                )
            try:
                validate_delivery_result(result)
            except (TypeError, ValueError):
                return cls.defer_job(
                    job_id, "provider_malformed", claim_token=execution.claim_token
                )
            with transaction.atomic():
                job = CommunicationDeliveryJob.objects.select_for_update().get(pk=job_id)
                if not (
                    job.status == CommunicationDeliveryJob.STATUS_RUNNING
                    and job.claim_token == execution.claim_token
                ):
                    raise CommunicationDispatchConflict(
                        "The generic communication job lost execution authority."
                    )
                if job.provider_external_message_id:
                    if not (
                        job.provider_external_message_id == result.external_message_id
                        and job.provider_delivery_status == result.delivery_status
                        and job.provider_accepted_at == result.accepted_at
                    ):
                        raise CommunicationDispatchConflict(
                            "The retained generic provider acceptance conflicts."
                        )
                else:
                    job.provider_external_message_id = result.external_message_id
                    job.provider_delivery_status = result.delivery_status
                    job.provider_accepted_at = result.accepted_at
                    job.save(
                        update_fields=[
                            "provider_external_message_id",
                            "provider_delivery_status",
                            "provider_accepted_at",
                        ]
                    )
        with transaction.atomic():
            job = CommunicationDeliveryJob.objects.select_for_update().get(pk=job_id)
            row = Communication.objects.select_for_update().get(pk=job.communication_id)
            if not (
                job.status == CommunicationDeliveryJob.STATUS_RUNNING
                and job.claim_token == execution.claim_token
                and job.request_payload_digest == cls._generic_payload_digest_from_row(row)
            ):
                raise CommunicationDispatchConflict(
                    "The generic communication changed during provider delivery."
                )
            row.delivery_status = "sent"
            row.external_message_id = result.external_message_id
            row.sent_at = result.accepted_at
            row.save(update_fields=["delivery_status", "external_message_id", "sent_at"])
        return cls.complete_job(job_id, claim_token=execution.claim_token)

    @classmethod
    def dispatch(
        cls, *, context, adapter=None, _job_id=None, _claim_token=None
    ):
        with transaction.atomic():
            cls._require_active_advice_claim(
                job_id=_job_id,
                claim_token=_claim_token,
                communication_id=context.communication_id,
            )
            retained = (
                CommunicationDeliveryOutbox.objects.select_for_update()
                .filter(advice_intent=context.advice_intent_id)
                .first()
            )
            if (
                retained is not None
                and retained.delivery_status == "sent"
                and retained.delivery_receipt_id is not None
                and retained.final_communication_id is not None
            ):
                cls._require_context_identity(retained, context)
                return cls._decision(retained)
            prepared = cls._prepare(context, retained.idempotency_key if retained else None)
            outbox = cls._freeze_or_reconcile(context, prepared)
            if outbox.delivery_status == CommunicationDeliveryOutbox.DELIVERY_SENT:
                return cls._decision(outbox)

        delivery_adapter = adapter or ManualEmailDeliveryAdapter()
        adapter_kind = cls._adapter_kind(delivery_adapter)
        try:
            result = delivery_adapter.send_email(
                prepared.delivery_payload,
                prepared.proposed["idempotency_key"],
            )
        except (TypeError, ValueError) as exc:
            with transaction.atomic():
                cls._require_active_advice_claim(
                    job_id=_job_id,
                    claim_token=_claim_token,
                    communication_id=context.communication_id,
                )
                cls._record_rejected_attempt(outbox.pk, prepared, adapter_kind)
            raise CommunicationDeliveryFailed(
                "The disbursement advice was not accepted for delivery.",
                failure_code="provider_rejected",
            ) from exc
        try:
            validate_delivery_result(result)
        except (TypeError, ValueError) as exc:
            with transaction.atomic():
                cls._require_active_advice_claim(
                    job_id=_job_id,
                    claim_token=_claim_token,
                    communication_id=context.communication_id,
                )
                cls._record_rejected_attempt(outbox.pk, prepared, adapter_kind)
            raise CommunicationDeliveryFailed(
                "The disbursement advice provider result was malformed.",
                failure_code="provider_malformed",
            ) from exc

        with transaction.atomic():
            cls._require_active_advice_claim(
                job_id=_job_id,
                claim_token=_claim_token,
                communication_id=context.communication_id,
            )
            outbox = CommunicationDeliveryOutbox.objects.select_for_update().get(
                advice_intent=context.advice_intent_id
            )
            cls._require_match(outbox, prepared.proposed)
            if outbox.delivery_status == CommunicationDeliveryOutbox.DELIVERY_PENDING:
                accepted_attempt = cls._record_accepted_attempt(
                    outbox, prepared, result, adapter_kind
                )
                outbox.delivery_status = CommunicationDeliveryOutbox.DELIVERY_SENT
                outbox.provider_external_message_id = result.external_message_id
                outbox.provider_delivery_status = result.delivery_status
                outbox.provider_accepted_at = result.accepted_at
                outbox.accepted_provider_attempt = accepted_attempt
                outbox.save(
                    update_fields=[
                        "delivery_status",
                        "provider_external_message_id",
                        "provider_delivery_status",
                        "provider_accepted_at",
                        "accepted_provider_attempt",
                    ]
                )
            elif not cls._provider_matches(outbox, result):
                raise CommunicationDispatchConflict(
                    "The retained provider acceptance is stale or incoherent."
                )
            return cls._decision(outbox)

    @staticmethod
    def _require_active_advice_claim(*, job_id, claim_token, communication_id):
        if job_id is None and claim_token is None:
            return
        if job_id is None or claim_token is None:
            raise CommunicationDispatchConflict(
                "The communication worker claim is incomplete."
            )
        job = (
            CommunicationDeliveryJob.objects.select_for_update(of=("self",))
            .filter(pk=job_id)
            .first()
        )
        if not (
            job is not None
            and job.job_kind == CommunicationDeliveryJob.KIND_ADVICE
            and job.communication_id == communication_id
            and job.status == CommunicationDeliveryJob.STATUS_RUNNING
            and job.claim_token == claim_token
            and job.lease_expires_at is not None
            and job.lease_expires_at > timezone.now()
        ):
            raise CommunicationDispatchConflict(
                "The communication worker no longer owns this advice claim."
            )

    @classmethod
    def finalize(cls, *, context, decision, request=None):
        """Finalize protected delivery evidence inside the context owner's transaction."""

        if not transaction.get_connection().in_atomic_block:
            raise CommunicationDispatchConflict(
                "Advice finalization requires the context owner's transaction."
            )
        receipt = _retained_receipt(decision)
        existing = Communication.objects.select_for_update().filter(
            pk=decision.communication_id
        ).first()
        if existing is not None:
            return _reconcile_finalization(context, receipt, decision, existing)
        if request is None:
            raise CommunicationDispatchConflict(
                "New advice finalization requires safe request evidence."
            )
        return _create_finalization(context, receipt, decision, request)

    @classmethod
    def _prepare(cls, context, idempotency_key):
        cls._validate_context(context)
        key = cls._validated_idempotency_key(idempotency_key)
        template = cls._current_template(context)
        merge_values = dict(context.merge_values)
        subject = cls._render(template.subject_template or "", merge_values)
        body = cls._render(template.body_template, merge_values)
        if any(
            sensitive and (sensitive in subject or sensitive in body)
            for sensitive in context.sensitive_values
        ):
            raise CommunicationDispatchConflict(
                "The rendered disbursement advice contains a sensitive value."
            )
        delivery_payload = EmailDeliveryPayload(
            communication_id=context.communication_id,
            recipient_email=context.recipient_address,
            subject=subject,
            body_text=body,
            related_entity_type=context.related_entity_type,
            related_entity_id=context.related_entity_id,
        )
        template_checksum = cls._template_checksum(template)
        proposed = {
            "advice_intent": context.advice_intent_id,
            "communication_id": context.communication_id,
            "idempotency_key": key,
            "channel": "email",
            "recipient_address": context.recipient_address,
            "recipient_digest": hashlib.sha256(
                context.recipient_address.encode()
            ).hexdigest(),
            "content_template_id": template.pk,
            "template_code_snapshot": template.template_code,
            "template_provenance_status": "verified",
            "template_provenance_origin": "frozen_before_dispatch",
            "template_name_snapshot": template.template_name,
            "template_type_snapshot": template.template_type,
            "template_language_code_snapshot": template.language_code,
            "template_audience_snapshot": template.audience,
            "template_version_snapshot": template.template_version,
            "template_approval_status_snapshot": template.approval_status,
            "template_effective_from_snapshot": template.effective_from,
            "template_effective_to_snapshot": template.effective_to,
            "template_variables_snapshot": sorted(template.variables_json or []),
            "subject_template_snapshot": template.subject_template or "",
            "body_template_snapshot": template.body_template,
            "template_checksum_sha256": template_checksum,
            "subject_snapshot": subject,
            "body_snapshot": body,
            "payload_digest": delivery_payload_digest(delivery_payload),
            "related_entity_type": context.related_entity_type,
            "related_entity_id": context.related_entity_id,
        }
        return _PreparedAdvice(
            proposed=proposed,
            delivery_payload=delivery_payload,
            template=template,
        )

    @classmethod
    def _freeze_or_reconcile(cls, context, prepared):
        outbox = (
            CommunicationDeliveryOutbox.objects.select_for_update()
            .filter(advice_intent=context.advice_intent_id)
            .first()
        )
        if outbox is None:
            if Communication.objects.select_for_update().filter(
                pk=context.communication_id
            ).exists():
                raise CommunicationDispatchConflict(
                    "A terminal communication cannot replace missing outbox evidence."
                )
            return CommunicationDeliveryOutbox.objects.create(**prepared.proposed)
        cls._require_match(outbox, prepared.proposed)
        return outbox

    @staticmethod
    def _require_match(outbox, proposed):
        if any(
            getattr(outbox, field) != value
            for field, value in proposed.items()
        ):
            raise CommunicationDispatchConflict(
                "The frozen communication outbox conflicts with current advice facts."
            )

    @staticmethod
    def _require_context_identity(outbox, context):
        if not (
            outbox.advice_intent == context.advice_intent_id
            and outbox.communication_id == context.communication_id
            and outbox.recipient_address == context.recipient_address
            and outbox.related_entity_type == context.related_entity_type
            and outbox.related_entity_id == context.related_entity_id
        ):
            raise CommunicationDispatchConflict(
                "The retained communication outbox conflicts with current advice facts."
            )

    @staticmethod
    def _provider_matches(outbox, result):
        return bool(
            outbox.provider_external_message_id == result.external_message_id
            and outbox.provider_delivery_status == result.delivery_status == "sent"
            and outbox.provider_accepted_at == result.accepted_at
        )

    @classmethod
    def _current_template(cls, context):
        today = timezone.localdate()
        rows = list(
            ContentTemplate.objects.select_for_update()
            .filter(
                template_code__startswith=context.template_code_prefix,
                template_type=context.template_type,
                audience=context.template_audience,
                approval_status=ContentTemplate.STATUS_APPROVED,
                effective_from__lte=today,
            )
            .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=today))
            .order_by("content_template_id")[:2]
        )
        required = set(context.required_variables)
        if len(rows) != 1 or set(rows[0].variables_json or []) != required:
            raise CommunicationDispatchConflict(
                "Exactly one approved effective disbursement advice template is required."
            )
        template = rows[0]
        declared = set(_TOKEN_RE.findall(template.subject_template or "")) | set(
            _TOKEN_RE.findall(template.body_template)
        )
        if declared != required:
            raise CommunicationDispatchConflict(
                "The disbursement advice template variables are incomplete or unexpected."
            )
        return template

    @staticmethod
    def _validate_context(context):
        required = set(context.required_variables)
        values = dict(context.merge_values)
        if (
            len(values) != len(context.merge_values)
            or set(values) != required
            or any(not isinstance(value, str) or not value for value in values.values())
            or any(
                part in variable.lower()
                for variable in required
                for part in _SENSITIVE_VARIABLE_PARTS
            )
            or any(
                sensitive and sensitive in value
                for sensitive in context.sensitive_values
                for value in values.values()
            )
            or not _MASKED_REFERENCE_RE.fullmatch(
                values.get("bank_reference_number", "")
            )
        ):
            raise CommunicationDispatchConflict(
                "The disbursement advice context is incomplete or contains sensitive values."
            )

    @staticmethod
    def _render(source, merge_values):
        rendered = source
        for key, value in merge_values.items():
            rendered = re.sub(
                rf"{{{{\s*{re.escape(key)}\s*}}}}", value, rendered
            )
        if not rendered or _TOKEN_RE.search(rendered):
            raise CommunicationDispatchConflict(
                "The disbursement advice template could not be rendered."
            )
        return rendered

    @staticmethod
    def _template_checksum(template):
        facts = {
            "content_template_id": str(template.pk),
            "template_code": template.template_code,
            "template_name": template.template_name,
            "template_type": template.template_type,
            "language_code": template.language_code,
            "audience": template.audience,
            "template_version": template.template_version,
            "approval_status": template.approval_status,
            "effective_from": template.effective_from.isoformat(),
            "effective_to": (
                template.effective_to.isoformat() if template.effective_to else None
            ),
            "variables": sorted(template.variables_json or []),
            "subject_template": template.subject_template,
            "body_template": template.body_template,
        }
        return hashlib.sha256(
            json.dumps(facts, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

    @staticmethod
    def _decision(outbox):
        CommunicationDispatcher._validate_outbox_evidence(outbox)
        attempt = CommunicationDispatcher._accepted_attempt(outbox)
        if (
            outbox.delivery_status != CommunicationDeliveryOutbox.DELIVERY_SENT
            or not outbox.provider_external_message_id
            or outbox.provider_delivery_status != "sent"
            or outbox.provider_accepted_at is None
        ):
            raise CommunicationDispatchConflict(
                "The retained provider acceptance is stale or incoherent."
            )
        try:
            validate_delivery_result(
                EmailDeliveryResult(
                    external_message_id=attempt.provider_external_message_id,
                    delivery_status=attempt.provider_delivery_status,
                    accepted_at=attempt.provider_accepted_at,
                )
            )
        except ValueError as exc:
            raise CommunicationDispatchConflict(
                "The retained provider acceptance is stale or incoherent."
            ) from exc
        return AdviceDeliveryDecision(
            outbox_id=outbox.pk,
            advice_intent_id=outbox.advice_intent,
            communication_id=outbox.communication_id,
            idempotency_key=outbox.idempotency_key,
            recipient_address=outbox.recipient_address,
            recipient_digest=outbox.recipient_digest,
            template_id=outbox.content_template_id,
            template_provenance_status=outbox.template_provenance_status,
            template_code=outbox.template_code_snapshot,
            template_name=outbox.template_name_snapshot,
            template_type=outbox.template_type_snapshot,
            template_language_code=outbox.template_language_code_snapshot,
            template_audience=outbox.template_audience_snapshot,
            template_version=outbox.template_version_snapshot,
            template_approval_status=outbox.template_approval_status_snapshot,
            template_effective_from=outbox.template_effective_from_snapshot,
            template_effective_to=outbox.template_effective_to_snapshot,
            template_variables=tuple(outbox.template_variables_snapshot or ()),
            subject_template=outbox.subject_template_snapshot,
            body_template=outbox.body_template_snapshot,
            template_checksum=outbox.template_checksum_sha256,
            subject=outbox.subject_snapshot,
            body=outbox.body_snapshot,
            payload_digest=outbox.payload_digest,
            related_entity_type=outbox.related_entity_type,
            related_entity_id=outbox.related_entity_id,
            external_message_id=attempt.provider_external_message_id,
            delivery_status=attempt.provider_delivery_status,
            accepted_at=attempt.provider_accepted_at,
        )

    @staticmethod
    def _validate_outbox_evidence(outbox):
        if not (
            outbox.template_provenance_status == "verified"
            and outbox.template_provenance_origin == "frozen_before_dispatch"
            and outbox.content_template_id is not None
            and outbox.template_code_snapshot is not None
            and outbox.template_name_snapshot is not None
            and outbox.template_type_snapshot is not None
            and outbox.template_audience_snapshot is not None
            and outbox.template_version_snapshot is not None
            and outbox.template_approval_status_snapshot is not None
            and outbox.template_effective_from_snapshot is not None
            and outbox.template_variables_snapshot is not None
            and outbox.subject_template_snapshot is not None
            and outbox.body_template_snapshot is not None
            and outbox.template_checksum_sha256 is not None
        ):
            raise CommunicationDispatchConflict(
                "The frozen communication outbox conflicts with retained evidence."
            )
        template_facts = {
            "content_template_id": str(outbox.content_template_id),
            "template_code": outbox.template_code_snapshot,
            "template_name": outbox.template_name_snapshot,
            "template_type": outbox.template_type_snapshot,
            "language_code": outbox.template_language_code_snapshot,
            "audience": outbox.template_audience_snapshot,
            "template_version": outbox.template_version_snapshot,
            "approval_status": outbox.template_approval_status_snapshot,
            "effective_from": outbox.template_effective_from_snapshot.isoformat(),
            "effective_to": (
                outbox.template_effective_to_snapshot.isoformat()
                if outbox.template_effective_to_snapshot else None
            ),
            "variables": sorted(outbox.template_variables_snapshot or []),
            "subject_template": outbox.subject_template_snapshot,
            "body_template": outbox.body_template_snapshot,
        }
        payload = EmailDeliveryPayload(
            communication_id=outbox.communication_id,
            recipient_email=outbox.recipient_address,
            subject=outbox.subject_snapshot,
            body_text=outbox.body_snapshot,
            related_entity_type=outbox.related_entity_type,
            related_entity_id=outbox.related_entity_id,
        )
        checksum = hashlib.sha256(
            json.dumps(template_facts, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        if not (
            checksum == outbox.template_checksum_sha256
            and delivery_payload_digest(payload) == outbox.payload_digest
            and hashlib.sha256(outbox.recipient_address.encode()).hexdigest()
            == outbox.recipient_digest
        ):
            raise CommunicationDispatchConflict(
                "The frozen communication outbox conflicts with retained evidence."
            )

    @staticmethod
    def _adapter_kind(adapter):
        cls = type(adapter)
        return f"{cls.__module__}.{cls.__qualname__}"

    @classmethod
    def _record_accepted_attempt(cls, outbox, prepared, result, adapter_kind):
        if CommunicationProviderAttempt.objects.select_for_update().filter(
            outbox=outbox, outcome=CommunicationProviderAttempt.OUTCOME_ACCEPTED
        ).exists():
            raise CommunicationDispatchConflict(
                "The retained provider acceptance is stale or incoherent."
            )
        attempted_at = timezone.now()
        proposed = {
            "outbox": outbox,
            "advice_intent_id": outbox.advice_intent,
            "communication_id": outbox.communication_id,
            "idempotency_key": outbox.idempotency_key,
            "payload_digest": prepared.proposed["payload_digest"],
            "adapter_kind": adapter_kind,
            "outcome": CommunicationProviderAttempt.OUTCOME_ACCEPTED,
            "provider_external_message_id": result.external_message_id,
            "provider_delivery_status": result.delivery_status,
            "provider_accepted_at": result.accepted_at,
            "attempted_at": attempted_at,
        }
        siblings = list(
            CommunicationProviderAttempt.objects.select_for_update()
            .filter(outbox=outbox)
            .order_by("attempted_at", "provider_attempt_id")
        )
        cls._require_rejected_attempts(outbox, siblings)
        proposed["evidence_digest"] = cls._attempt_digest(
            proposed, prior_attempt_digests=[row.evidence_digest for row in siblings]
        )
        return CommunicationProviderAttempt.objects.create(**proposed)

    @classmethod
    def _record_rejected_attempt(cls, outbox_id, prepared, adapter_kind):
        with transaction.atomic():
            outbox = CommunicationDeliveryOutbox.objects.select_for_update().get(
                pk=outbox_id
            )
            if CommunicationProviderAttempt.objects.filter(
                outbox=outbox,
                outcome=CommunicationProviderAttempt.OUTCOME_ACCEPTED,
            ).exists():
                raise CommunicationDispatchConflict(
                    "An accepted provider result cannot receive a sibling attempt."
                )
            attempted_at = timezone.now()
            proposed = {
                "outbox": outbox,
                "advice_intent_id": outbox.advice_intent,
                "communication_id": outbox.communication_id,
                "idempotency_key": outbox.idempotency_key,
                "payload_digest": prepared.proposed["payload_digest"],
                "adapter_kind": adapter_kind,
                "outcome": CommunicationProviderAttempt.OUTCOME_REJECTED,
                "provider_external_message_id": None,
                "provider_delivery_status": None,
                "provider_accepted_at": None,
                "attempted_at": attempted_at,
            }
            proposed["evidence_digest"] = cls._attempt_digest(proposed)
            CommunicationProviderAttempt.objects.create(**proposed)

    @classmethod
    def _accepted_attempt(cls, outbox):
        attempts = list(
            CommunicationProviderAttempt.objects.select_for_update()
            .filter(outbox=outbox)
            .order_by("attempted_at", "provider_attempt_id")
        )
        accepted = [
            row
            for row in attempts
            if row.outcome == CommunicationProviderAttempt.OUTCOME_ACCEPTED
        ]
        rejected = [row for row in attempts if row.outcome == "rejected"]
        cls._require_rejected_attempts(outbox, rejected)
        if (
            len(accepted) != 1
            or attempts[-1].pk != accepted[0].pk
            or accepted[0].adapter_kind in _LEGACY_PROVENANCE_ADAPTER_KINDS
            or outbox.accepted_provider_attempt_id != accepted[0].pk
            or accepted[0].advice_intent_id != outbox.advice_intent
            or accepted[0].communication_id != outbox.communication_id
            or accepted[0].idempotency_key != outbox.idempotency_key
            or accepted[0].payload_digest != outbox.payload_digest
            or accepted[0].provider_external_message_id
            != outbox.provider_external_message_id
            or accepted[0].provider_delivery_status
            != outbox.provider_delivery_status
            or accepted[0].provider_accepted_at != outbox.provider_accepted_at
            or accepted[0].evidence_digest
            != cls._attempt_digest(
                {
                    "outbox": outbox,
                    "advice_intent_id": accepted[0].advice_intent_id,
                    "communication_id": accepted[0].communication_id,
                    "idempotency_key": accepted[0].idempotency_key,
                    "payload_digest": accepted[0].payload_digest,
                    "adapter_kind": accepted[0].adapter_kind,
                    "outcome": accepted[0].outcome,
                    "provider_external_message_id": accepted[0].provider_external_message_id,
                    "provider_delivery_status": accepted[0].provider_delivery_status,
                    "provider_accepted_at": accepted[0].provider_accepted_at,
                    "attempted_at": accepted[0].attempted_at,
                },
                prior_attempt_digests=[row.evidence_digest for row in rejected],
            )
        ):
            raise CommunicationDispatchConflict(
                "The retained provider acceptance is stale or incoherent."
            )
        return accepted[0]

    @classmethod
    def _require_rejected_attempts(cls, outbox, attempts):
        for row in attempts:
            facts = {
                "outbox": outbox,
                "advice_intent_id": row.advice_intent_id,
                "communication_id": row.communication_id,
                "idempotency_key": row.idempotency_key,
                "payload_digest": row.payload_digest,
                "adapter_kind": row.adapter_kind,
                "outcome": row.outcome,
                "provider_external_message_id": row.provider_external_message_id,
                "provider_delivery_status": row.provider_delivery_status,
                "provider_accepted_at": row.provider_accepted_at,
                "attempted_at": row.attempted_at,
            }
            if not (
                row.outcome == CommunicationProviderAttempt.OUTCOME_REJECTED
                and row.advice_intent_id == outbox.advice_intent
                and row.communication_id == outbox.communication_id
                and row.idempotency_key == outbox.idempotency_key
                and row.payload_digest == outbox.payload_digest
                and row.evidence_digest == cls._attempt_digest(facts)
            ):
                raise CommunicationDispatchConflict(
                    "The retained provider acceptance is stale or incoherent."
                )

    @staticmethod
    def _attempt_digest(facts, *, prior_attempt_digests=()):
        stable = {
            "outbox_id": str(facts["outbox"].pk),
            "advice_intent_id": str(facts["advice_intent_id"]),
            "communication_id": str(facts["communication_id"]),
            "idempotency_key": facts["idempotency_key"],
            "payload_digest": facts["payload_digest"],
            "adapter_kind": facts["adapter_kind"],
            "outcome": facts["outcome"],
            "provider_external_message_id": facts["provider_external_message_id"],
            "provider_delivery_status": facts["provider_delivery_status"],
            "provider_accepted_at": (
                _iso(facts["provider_accepted_at"])
                if facts["provider_accepted_at"]
                else None
            ),
            "attempted_at": _iso(facts["attempted_at"]),
            "prior_attempt_digests": list(prior_attempt_digests),
        }
        return hashlib.sha256(
            json.dumps(stable, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


def _retained_receipt(decision):
    with transaction.atomic():
        receipt, _created = (
            DisbursementAdviceDeliveryReceipt.objects.select_for_update().get_or_create(
                advice_intent=decision.advice_intent_id,
                defaults={
                    "idempotency_key": decision.idempotency_key,
                    "payload_digest": decision.payload_digest,
                    "external_message_id": decision.external_message_id,
                    "delivery_status": decision.delivery_status,
                    "accepted_at": decision.accepted_at,
                },
            )
        )
    if not _receipt_matches(receipt, decision):
        raise CommunicationDispatchConflict(
            "The retained provider acceptance is stale or incoherent."
        )
    return receipt


def _receipt_matches(receipt, decision):
    return bool(
        receipt.advice_intent == decision.advice_intent_id
        and receipt.idempotency_key == decision.idempotency_key
        and receipt.payload_digest == decision.payload_digest
        and receipt.delivery_status == decision.delivery_status == "sent"
        and receipt.external_message_id == decision.external_message_id
        and receipt.accepted_at == decision.accepted_at
    )


def _create_finalization(context, receipt, decision, request):
    communication = _create_protected_communication(context, decision)
    action_id = uuid.uuid4()
    evidence = _safe_delivery_evidence(
        context,
        receipt,
        decision,
        action_id=action_id,
        request=request,
    )
    actor = User.objects.get(pk=context.actor_id)
    audit = AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action=_ADVICE_ACTION,
        entity_type=decision.related_entity_type,
        entity_id=decision.related_entity_id,
        old_value_json={"disbursement_advice_communication_id": None},
        new_value_json=evidence,
        ip_address=request.ip_address,
        user_agent=request.user_agent,
    )
    workflow = record_workflow_event(
        actor=actor,
        workflow_name=_ADVICE_WORKFLOW,
        entity_type=decision.related_entity_type,
        entity_id=decision.related_entity_id,
        from_state="transfer_successful",
        to_state="advice_sent",
        trigger_reason=_workflow_trigger(action_id, communication.pk, request.request_id),
        action_code=_ADVICE_ACTION,
        metadata=evidence,
    )
    evidence_digest = _delivery_evidence_digest(
        context,
        receipt,
        decision,
        evidence=evidence,
        audit=audit,
        workflow=workflow,
    )
    _protect_final_chain(decision, receipt, communication)
    return AdviceFinalizationDecision(
        communication_id=communication.pk,
        receipt_id=receipt.pk,
        action_id=action_id,
        audit_id=audit.pk,
        workflow_id=workflow.pk,
        delivery_evidence_digest=evidence_digest,
        delivery_status=communication.delivery_status,
        sent_at=communication.sent_at,
    )


def _create_protected_communication(context, decision):
    return Communication.objects.create(
        communication_id=decision.communication_id,
        related_entity_type=decision.related_entity_type,
        related_entity_id=decision.related_entity_id,
        recipient_party_type="borrower",
        recipient_party_id=context.recipient_party_id,
        recipient_address=decision.recipient_address,
        channel="email",
        content_template_id=decision.template_id,
        subject_snapshot=decision.subject,
        body_snapshot=decision.body,
        sent_by_user_id=context.actor_id,
        sent_at=decision.accepted_at,
        delivery_status=decision.delivery_status,
        external_message_id=decision.external_message_id,
    )


def _reconcile_finalization(context, receipt, decision, communication):
    audits = list(
        AuditLog.objects.select_for_update()
        .filter(
            action=_ADVICE_ACTION,
            entity_type=decision.related_entity_type,
            entity_id=decision.related_entity_id,
        )
        .order_by("audit_log_id")[:2]
    )
    workflows = list(
        WorkflowEvent.objects.select_for_update()
        .filter(
            workflow_name=_ADVICE_WORKFLOW,
            entity_type=decision.related_entity_type,
            entity_id=decision.related_entity_id,
        )
        .order_by("workflow_event_id")[:2]
    )
    if len(audits) != 1 or len(workflows) != 1:
        raise CommunicationDispatchConflict(
            "The retained communication finalization is stale or incoherent."
        )
    audit = audits[0]
    workflow = workflows[0]
    evidence = audit.new_value_json
    if not isinstance(evidence, dict):
        raise CommunicationDispatchConflict(
            "The retained communication finalization is stale or incoherent."
        )
    try:
        action_id = uuid.UUID(evidence.get("action_id", ""))
        request = AdviceFinalizationRequest(
            request_id=evidence["request_id"],
            ip_address=evidence["ip_address"],
            user_agent=evidence["user_agent"],
        )
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        raise CommunicationDispatchConflict(
            "The retained communication finalization is stale or incoherent."
        ) from exc
    expected_evidence = _safe_delivery_evidence(
        context,
        receipt,
        decision,
        action_id=action_id,
        request=request,
    )
    expected_digest = _delivery_evidence_digest(
        context,
        receipt,
        decision,
        evidence=evidence,
        audit=audit,
        workflow=workflow,
    )
    outbox = CommunicationDeliveryOutbox.objects.select_for_update().get(
        pk=decision.outbox_id
    )
    if not (
        communication.pk == decision.communication_id == context.communication_id
        and communication.related_entity_type == decision.related_entity_type
        and communication.related_entity_id == decision.related_entity_id
        and communication.recipient_party_type == "borrower"
        and communication.recipient_party_id == context.recipient_party_id
        and communication.recipient_address == decision.recipient_address
        and communication.channel == "email"
        and communication.content_template_id == decision.template_id
        and communication.subject_snapshot == decision.subject
        and communication.body_snapshot == decision.body
        and communication.sent_by_user_id == context.actor_id
        and communication.sent_at == decision.accepted_at
        and communication.delivery_status == decision.delivery_status == "sent"
        and communication.external_message_id == decision.external_message_id
        and audit.actor_user_id == context.actor_id
        and audit.actor_type == "user"
        and audit.old_value_json == {"disbursement_advice_communication_id": None}
        and evidence == expected_evidence
        and audit.ip_address == request.ip_address
        and audit.user_agent == request.user_agent
        and workflow.workflow_name == _ADVICE_WORKFLOW
        and workflow.entity_type == decision.related_entity_type
        and workflow.entity_id == decision.related_entity_id
        and workflow.from_state == "transfer_successful"
        and workflow.to_state == "advice_sent"
        and workflow.triggered_by_user_id == context.actor_id
        and workflow.trigger_reason
        == _workflow_trigger(action_id, communication.pk, request.request_id)
        and outbox.delivery_receipt_id == receipt.pk
        and outbox.final_communication_id == communication.pk
    ):
        raise CommunicationDispatchConflict(
            "The retained communication finalization is stale or incoherent."
        )
    return AdviceFinalizationDecision(
        communication_id=communication.pk,
        receipt_id=receipt.pk,
        action_id=action_id,
        audit_id=audit.pk,
        workflow_id=workflow.pk,
        delivery_evidence_digest=expected_digest,
        delivery_status=communication.delivery_status,
        sent_at=communication.sent_at,
    )


def _protect_final_chain(decision, receipt, communication):
    outbox = CommunicationDeliveryOutbox.objects.select_for_update().get(
        pk=decision.outbox_id
    )
    if outbox.delivery_receipt_id or outbox.final_communication_id:
        raise CommunicationDispatchConflict(
            "The retained communication finalization is stale or incoherent."
        )
    outbox.delivery_receipt = receipt
    outbox.final_communication = communication
    outbox.save(update_fields=["delivery_receipt", "final_communication"])


def _safe_delivery_evidence(context, receipt, decision, *, action_id, request):
    return {
        "action_id": str(action_id),
        "disbursement_id": str(decision.related_entity_id),
        "communication_id": str(decision.communication_id),
        "loan_account_id": str(context.loan_account_id),
        "loan_application_id": str(context.loan_application_id),
        "member_id": str(context.member_id),
        "template_id": str(decision.template_id),
        "template_code": decision.template_code,
        "template_version": decision.template_version,
        "recipient_masked": _masked_email(decision.recipient_address),
        "recipient_digest": decision.recipient_digest,
        "channel": "email",
        "delivery_status": receipt.delivery_status,
        "provider_message_digest": _digest(receipt.external_message_id),
        "subject_digest": _digest(decision.subject),
        "body_digest": _digest(decision.body),
        "sent_at": _iso(receipt.accepted_at),
        "disbursement_amount_digest": _digest(f"{context.disbursement_amount:.2f}"),
        "bank_reference_masked": context.masked_bank_reference,
        "transfer_success_action_id": str(context.transfer_success_action_id),
        "transfer_success_evidence_digest": context.transfer_success_evidence_digest,
        "actor_user_id": str(context.actor_id),
        "actor_role_code": context.actor_role_code,
        "actor_team_codes": list(context.actor_team_codes),
        "request_id": request.request_id,
        "ip_address": request.ip_address,
        "user_agent": request.user_agent,
        "outcome": "sent",
    }


def _delivery_evidence_digest(context, receipt, decision, *, evidence, audit, workflow):
    facts = {
        "advice_intent_id": str(context.advice_intent_id),
        "intent_created_at": _iso(context.intent_created_at),
        "audit_evidence": evidence,
        "audit_id": str(audit.pk),
        "audit_created_at": _iso(audit.created_at),
        "workflow_id": str(workflow.pk),
        "workflow_created_at": _iso(workflow.created_at),
        "workflow_trigger_reason": workflow.trigger_reason,
        "receipt_id": str(receipt.pk),
        "receipt_payload_digest": receipt.payload_digest,
        "template_approval_status": decision.template_approval_status,
        "template_effective_from": decision.template_effective_from.isoformat(),
        "template_effective_to": (
            decision.template_effective_to.isoformat()
            if decision.template_effective_to
            else None
        ),
        "template_variables": list(decision.template_variables),
    }
    return _digest(json.dumps(facts, sort_keys=True, separators=(",", ":")))


def _workflow_trigger(action_id, communication_id, request_id):
    return (
        f"action_id={action_id};communication_id={communication_id};"
        f"request_id={request_id}"
    )


def _masked_email(email):
    local, domain = email.split("@", 1)
    return f"{local[:1]}***@{domain}"


def _digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def _iso(value):
    return value.isoformat().replace("+00:00", "Z")


def _iso_or_none(value):
    return _iso(value) if value is not None else None


__all__ = [
    "AdviceDeliveryDecision",
    "AdviceFinalizationDecision",
    "AdviceFinalizationRequest",
    "CommunicationDeliveryFailed",
    "CommunicationDispatchConflict",
    "CommunicationDispatcher",
    "FinalizedAdviceArtifact",
    "resolve_finalized_advice_artifact",
]
