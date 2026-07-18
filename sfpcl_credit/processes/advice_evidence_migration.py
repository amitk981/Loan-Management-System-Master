"""Cross-owner legacy advice classification for communications migration 0005."""

import hashlib
import json
import uuid


_ATTEMPT_NAMESPACE = uuid.UUID("6ed7f425-07d0-4b0d-b5f9-5106b2f5548e")


def _iso(value):
    return value.isoformat().replace("+00:00", "Z")


def _template_values(template):
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
        "effective_to": template.effective_to.isoformat() if template.effective_to else None,
        "variables": sorted(template.variables_json or []),
        "subject_template": template.subject_template,
        "body_template": template.body_template,
    }
    return {
        "template_provenance_status": "verified",
        "template_name_snapshot": template.template_name,
        "template_type_snapshot": template.template_type,
        "template_language_code_snapshot": template.language_code,
        "template_audience_snapshot": template.audience,
        "template_approval_status_snapshot": template.approval_status,
        "template_effective_from_snapshot": template.effective_from,
        "template_effective_to_snapshot": template.effective_to,
        "template_variables_snapshot": sorted(template.variables_json or []),
        "subject_template_snapshot": template.subject_template or "",
        "body_template_snapshot": template.body_template,
        "template_checksum_sha256": hashlib.sha256(
            json.dumps(facts, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }


def _create_acceptance(Attempt, outbox, adapter_kind):
    attempted_at = outbox.provider_accepted_at
    facts = {
        "outbox_id": str(outbox.pk),
        "advice_intent_id": str(outbox.advice_intent),
        "communication_id": str(outbox.communication_id),
        "idempotency_key": outbox.idempotency_key,
        "payload_digest": outbox.payload_digest,
        "adapter_kind": adapter_kind,
        "outcome": "accepted",
        "provider_external_message_id": outbox.provider_external_message_id,
        "provider_delivery_status": outbox.provider_delivery_status,
        "provider_accepted_at": _iso(outbox.provider_accepted_at),
        "attempted_at": _iso(attempted_at),
        "prior_attempt_digests": [],
    }
    attempt = Attempt.objects.create(
        provider_attempt_id=uuid.uuid5(_ATTEMPT_NAMESPACE, f"{outbox.pk}:accepted"),
        outbox_id=outbox.pk,
        advice_intent_id=outbox.advice_intent,
        communication_id=outbox.communication_id,
        idempotency_key=outbox.idempotency_key,
        payload_digest=outbox.payload_digest,
        adapter_kind=adapter_kind,
        outcome="accepted",
        provider_external_message_id=outbox.provider_external_message_id,
        provider_delivery_status=outbox.provider_delivery_status,
        provider_accepted_at=outbox.provider_accepted_at,
        attempted_at=attempted_at,
        evidence_digest=hashlib.sha256(
            json.dumps(facts, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    )
    outbox.accepted_provider_attempt_id = attempt.pk
    outbox.save(update_fields=["accepted_provider_attempt"])


def backfill_advice_evidence(apps, schema_editor):
    Outbox = apps.get_model("communications", "CommunicationDeliveryOutbox")
    Attempt = apps.get_model("communications", "CommunicationProviderAttempt")
    Receipt = apps.get_model("communications", "DisbursementAdviceDeliveryReceipt")
    Communication = apps.get_model("communications", "Communication")
    Intent = apps.get_model("disbursements", "DisbursementAdviceIntent")
    Disbursement = apps.get_model("disbursements", "Disbursement")
    Audit = apps.get_model("identity", "AuditLog")
    Workflow = apps.get_model("workflows", "WorkflowEvent")

    for outbox in Outbox.objects.select_related("content_template").all():
        values = _template_values(outbox.content_template)
        for field, value in values.items():
            setattr(outbox, field, value)
        outbox.save(update_fields=list(values))
        if outbox.delivery_status == "sent":
            _create_acceptance(Attempt, outbox, "legacy:retained-outbox")

    owned = set(Outbox.objects.values_list("advice_intent", flat=True))
    for receipt in Receipt.objects.exclude(advice_intent__in=owned):
        intent = Intent.objects.filter(pk=receipt.advice_intent).first()
        communication = Communication.objects.filter(pk=receipt.advice_intent).first()
        if intent is None or communication is None:
            continue
        disbursement = Disbursement.objects.filter(pk=intent.disbursement_id).first()
        audit = Audit.objects.filter(pk=intent.delivery_audit_id).first()
        workflow = Workflow.objects.filter(pk=intent.delivery_workflow_event_id).first()
        evidence = audit.new_value_json if audit is not None else None
        coherent = (
            intent.delivery_status == "sent"
            and intent.delivery_action_id
            and intent.delivery_evidence_digest
            and disbursement is not None
            and disbursement.disbursement_advice_communication_id == communication.pk
            and communication.content_template_id
            and communication.delivery_status == receipt.delivery_status == "sent"
            and communication.external_message_id == receipt.external_message_id
            and communication.sent_at == receipt.accepted_at
            and communication.subject_snapshot
            and communication.body_snapshot
            and communication.recipient_address
            and audit is not None
            and isinstance(evidence, dict)
            and audit.action == "disbursement.advice_sent"
            and audit.entity_type == "disbursement"
            and audit.entity_id == disbursement.pk
            and audit.actor_user_id == communication.sent_by_user_id
            and evidence.get("action_id") == str(intent.delivery_action_id)
            and evidence.get("communication_id") == str(communication.pk)
            and Audit.objects.filter(action="disbursement.advice_sent", entity_type="disbursement", entity_id=disbursement.pk).count() == 1
            and workflow is not None
            and workflow.workflow_name == "DisbursementAdviceSent"
            and workflow.entity_type == "disbursement"
            and workflow.entity_id == disbursement.pk
            and workflow.to_state == "advice_sent"
            and workflow.triggered_by_user_id == communication.sent_by_user_id
            and str(intent.delivery_action_id) in workflow.trigger_reason
            and str(communication.pk) in workflow.trigger_reason
            and Workflow.objects.filter(workflow_name="DisbursementAdviceSent", entity_type="disbursement", entity_id=disbursement.pk).count() == 1
        )
        if not coherent:
            continue
        template = communication.content_template
        provenance = _template_values(template)
        outbox = Outbox.objects.create(
            outbox_id=communication.pk,
            advice_intent=receipt.advice_intent,
            communication_id=communication.pk,
            idempotency_key=receipt.idempotency_key,
            channel=communication.channel,
            recipient_address=communication.recipient_address,
            recipient_digest=hashlib.sha256(communication.recipient_address.encode()).hexdigest(),
            content_template_id=communication.content_template_id,
            template_code_snapshot=template.template_code,
            template_version_snapshot=template.template_version,
            subject_snapshot=communication.subject_snapshot,
            body_snapshot=communication.body_snapshot,
            payload_digest=receipt.payload_digest,
            related_entity_type=communication.related_entity_type,
            related_entity_id=communication.related_entity_id,
            delivery_status="sent",
            provider_external_message_id=receipt.external_message_id,
            provider_delivery_status=receipt.delivery_status,
            provider_accepted_at=receipt.accepted_at,
            created_at=receipt.created_at,
            delivery_receipt_id=receipt.pk,
            final_communication_id=communication.pk,
            **provenance,
        )
        _create_acceptance(Attempt, outbox, "legacy:pre-outbox")


def reverse_advice_evidence(apps, schema_editor):
    Outbox = apps.get_model("communications", "CommunicationDeliveryOutbox")
    Attempt = apps.get_model("communications", "CommunicationProviderAttempt")
    if Attempt.objects.exclude(
        adapter_kind__in=("legacy:pre-outbox", "legacy:retained-outbox")
    ).exists():
        raise RuntimeError("Cannot reverse communications 0005 after new provider evidence exists.")
    created_ids = list(
        Attempt.objects.filter(adapter_kind="legacy:pre-outbox").values_list("outbox_id", flat=True)
    )
    Outbox.objects.update(
        accepted_provider_attempt_id=None,
        delivery_receipt_id=None,
        final_communication_id=None,
    )
    Attempt.objects.all().delete()
    Outbox.objects.filter(pk__in=created_ids).delete()


__all__ = ["backfill_advice_evidence", "reverse_advice_evidence"]
