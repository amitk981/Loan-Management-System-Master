from dataclasses import dataclass
from datetime import date, datetime
import hashlib
import json
import re
import uuid

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from sfpcl_credit.communications.adapters import (
    EmailDeliveryPayload,
    EmailDeliveryResult,
    ManualEmailDeliveryAdapter,
    delivery_payload_digest,
    validate_delivery_result,
)
from sfpcl_credit.communications.models import (
    CommunicationDeliveryOutbox,
    ContentTemplate,
)


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


class CommunicationDispatchConflict(Exception):
    pass


class CommunicationDeliveryFailed(CommunicationDispatchConflict):
    pass


@dataclass(frozen=True)
class AdviceDeliveryDecision:
    outbox_id: uuid.UUID
    advice_intent_id: uuid.UUID
    communication_id: uuid.UUID
    idempotency_key: str
    recipient_address: str
    recipient_digest: str
    template_id: uuid.UUID
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
class _PreparedAdvice:
    proposed: dict
    delivery_payload: EmailDeliveryPayload
    template: ContentTemplate


class CommunicationDispatcher:
    """Own template, render, durable outbox, and provider dispatch policy."""

    @classmethod
    def dispatch(cls, *, context, adapter=None):
        with transaction.atomic():
            prepared = cls._prepare(context)
            outbox = cls._freeze_or_reconcile(context, prepared)
            if outbox.delivery_status == CommunicationDeliveryOutbox.DELIVERY_SENT:
                return cls._decision(outbox, prepared.template)

        try:
            result = (adapter or ManualEmailDeliveryAdapter()).send_email(
                prepared.delivery_payload,
                prepared.proposed["idempotency_key"],
            )
            validate_delivery_result(result)
        except (TypeError, ValueError) as exc:
            raise CommunicationDeliveryFailed(
                "The disbursement advice was not accepted for delivery."
            ) from exc

        with transaction.atomic():
            outbox = CommunicationDeliveryOutbox.objects.select_for_update().get(
                advice_intent_id=context.advice_intent_id
            )
            cls._require_match(outbox, prepared.proposed)
            if outbox.delivery_status == CommunicationDeliveryOutbox.DELIVERY_PENDING:
                outbox.delivery_status = CommunicationDeliveryOutbox.DELIVERY_SENT
                outbox.provider_external_message_id = result.external_message_id
                outbox.provider_delivery_status = result.delivery_status
                outbox.provider_accepted_at = result.accepted_at
                outbox.save(
                    update_fields=[
                        "delivery_status",
                        "provider_external_message_id",
                        "provider_delivery_status",
                        "provider_accepted_at",
                    ]
                )
            elif not cls._provider_matches(outbox, result):
                raise CommunicationDispatchConflict(
                    "The retained provider acceptance is stale or incoherent."
                )
            return cls._decision(outbox, prepared.template)

    @classmethod
    def _prepare(cls, context):
        cls._validate_context(context)
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
            "advice_intent_id": context.advice_intent_id,
            "communication_id": context.communication_id,
            "idempotency_key": f"disbursement-advice:{context.advice_intent_id}",
            "channel": "email",
            "recipient_address": context.recipient_address,
            "recipient_digest": hashlib.sha256(
                context.recipient_address.encode()
            ).hexdigest(),
            "content_template_id": template.pk,
            "template_code_snapshot": template.template_code,
            "template_version_snapshot": template.template_version,
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
            .filter(advice_intent_id=context.advice_intent_id)
            .first()
        )
        if outbox is None:
            return CommunicationDeliveryOutbox.objects.create(**prepared.proposed)
        cls._require_match(outbox, prepared.proposed)
        return outbox

    @staticmethod
    def _require_match(outbox, proposed):
        if any(
            getattr(outbox, field) != value
            for field, value in proposed.items()
            if field != "advice_intent_id"
        ) or outbox.advice_intent_id != proposed["advice_intent_id"]:
            raise CommunicationDispatchConflict(
                "The frozen communication outbox conflicts with current advice facts."
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
    def _decision(outbox, template):
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
                    external_message_id=outbox.provider_external_message_id,
                    delivery_status=outbox.provider_delivery_status,
                    accepted_at=outbox.provider_accepted_at,
                )
            )
        except ValueError as exc:
            raise CommunicationDispatchConflict(
                "The retained provider acceptance is stale or incoherent."
            ) from exc
        return AdviceDeliveryDecision(
            outbox_id=outbox.pk,
            advice_intent_id=outbox.advice_intent_id,
            communication_id=outbox.communication_id,
            idempotency_key=outbox.idempotency_key,
            recipient_address=outbox.recipient_address,
            recipient_digest=outbox.recipient_digest,
            template_id=template.pk,
            template_code=template.template_code,
            template_name=template.template_name,
            template_type=template.template_type,
            template_language_code=template.language_code,
            template_audience=template.audience,
            template_version=template.template_version,
            template_approval_status=template.approval_status,
            template_effective_from=template.effective_from,
            template_effective_to=template.effective_to,
            template_variables=tuple(sorted(template.variables_json or [])),
            subject_template=template.subject_template or "",
            body_template=template.body_template,
            template_checksum=outbox.template_checksum_sha256,
            subject=outbox.subject_snapshot,
            body=outbox.body_snapshot,
            payload_digest=outbox.payload_digest,
            related_entity_type=outbox.related_entity_type,
            related_entity_id=outbox.related_entity_id,
            external_message_id=outbox.provider_external_message_id,
            delivery_status=outbox.provider_delivery_status,
            accepted_at=outbox.provider_accepted_at,
        )


__all__ = [
    "AdviceDeliveryDecision",
    "CommunicationDeliveryFailed",
    "CommunicationDispatchConflict",
    "CommunicationDispatcher",
]
