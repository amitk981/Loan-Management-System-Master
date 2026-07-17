import re
import uuid

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.communications.adapters import (
    EmailDeliveryPayload,
    ManualEmailDeliveryAdapter,
    validate_delivery_result,
)
from sfpcl_credit.communications.models import Communication, ContentTemplate
from sfpcl_credit.disbursements.models import BankTransfer, Disbursement
from sfpcl_credit.disbursements.modules.disbursement_transfer_success import (
    _masked_reference,
    completed_success_is_coherent,
)
from sfpcl_credit.domain_errors import DomainObjectAccessDenied, DomainPermissionDenied
from sfpcl_credit.identity.models import AuditLog, Permission, User
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.workflows.events import record_workflow_event


SEND_ADVICE_PERMISSION = "finance.disbursement.send_advice"
ADVICE_ACTION = "disbursement.advice_sent"
ADVICE_VARIABLES = {
    "borrower_name",
    "application_reference_number",
    "loan_account_number",
    "sanctioned_amount",
    "disbursement_amount",
    "disbursed_at",
    "bank_reference_number",
}
_TOKEN_RE = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")
_CFC_ROLE = "chief_financial_controller"
_FINANCE_ROLE = "senior_manager_finance"


class DisbursementAdviceConflict(Exception):
    code = "CONFLICT"


class DisbursementAdviceDeliveryFailed(DisbursementAdviceConflict):
    code = "DELIVERY_FAILED"


def _send_advice(*, actor, disbursement_id, payload, request=None, adapter=None):
    cleaned = _validate_payload(payload)
    with transaction.atomic():
        operator = _locked_operator(actor)
        row = (
            Disbursement.objects.select_for_update(of=("self",))
            .select_related(
                "member",
                "loan_application",
                "loan_account",
                "loan_account__terms",
                "bank_transfer",
                "bank_transfer_evidence_document",
                "authorisation_audit",
                "authorisation_workflow_event",
                "transfer_success_actor_user",
                "transfer_success_audit",
                "transfer_success_workflow_event",
                "transfer_success_loan_status_history",
                "disbursement_advice_communication",
                "disbursement_advice_communication__content_template",
            )
            .filter(pk=disbursement_id)
            .first()
        )
        if row is None:
            raise DomainObjectAccessDenied(None)
        role_code = _require_operator_scope(operator, row)
        _lock_source_relations(row)
        canonical_email = _canonical_email(row.member.email)
        if not completed_success_is_coherent(row):
            raise DisbursementAdviceConflict(
                "The successful disbursement evidence is stale or incoherent."
            )
        if row.disbursement_advice_communication_id is not None:
            if _retained_advice_is_coherent(
                row, cleaned, operator=operator, role_code=role_code
            ):
                return serialize_advice(row.disbursement_advice_communication)
            raise DisbursementAdviceConflict(
                "The disbursement already has different or stale advice evidence."
            )
        if cleaned["channel"] != "email":
            raise ValidationError({"channel": "Only email is supported."})
        if cleaned["recipient_email"] != canonical_email:
            raise ValidationError(
                {"recipient_email": "Must match the member's current email address."}
            )

        template = _locked_current_template()
        merge_data = _merge_data(row)
        subject = _render(template.subject_template or "", merge_data)
        body = _render(template.body_template, merge_data)
        communication_id = uuid.uuid4()
        action_id = uuid.uuid4()
        idempotency_key = f"disbursement-advice:{row.pk}"
        delivery_adapter = adapter or ManualEmailDeliveryAdapter()
        try:
            delivery = delivery_adapter.send_email(
                EmailDeliveryPayload(
                    communication_id=communication_id,
                    recipient_email=canonical_email,
                    subject=subject,
                    body_text=body,
                    related_entity_type="disbursement",
                    related_entity_id=row.pk,
                ),
                idempotency_key,
            )
            validate_delivery_result(delivery)
        except (TypeError, ValueError) as exc:
            raise DisbursementAdviceDeliveryFailed(
                "The disbursement advice was not accepted for delivery."
            ) from exc

        communication = Communication.objects.create(
            communication_id=communication_id,
            related_entity_type="disbursement",
            related_entity_id=row.pk,
            recipient_party_type="borrower",
            recipient_party_id=row.member_id,
            recipient_address=canonical_email,
            channel="email",
            content_template=template,
            subject_snapshot=subject,
            body_snapshot=body,
            sent_by_user=operator,
            sent_at=delivery.accepted_at,
            delivery_status=delivery.delivery_status,
            external_message_id=delivery.external_message_id,
        )
        request_id = _request_id(request)
        ip_address = request_ip(request) if request else ""
        user_agent = request_user_agent(request) if request else ""
        reference_masked = _masked_reference(row.bank_reference_number)
        evidence = {
            "action_id": str(action_id),
            "disbursement_id": str(row.pk),
            "communication_id": str(communication.pk),
            "loan_account_id": str(row.loan_account_id),
            "loan_application_id": str(row.loan_application_id),
            "member_id": str(row.member_id),
            "template_id": str(template.pk),
            "template_code": template.template_code,
            "template_version": template.template_version,
            "recipient_email": canonical_email,
            "channel": "email",
            "delivery_status": delivery.delivery_status,
            "external_message_id": delivery.external_message_id,
            "sent_at": _iso(delivery.accepted_at),
            "disbursement_amount": f"{row.disbursement_amount:.2f}",
            "bank_reference_masked": reference_masked,
            "transfer_success_action_id": str(row.transfer_success_action_id),
            "transfer_success_evidence_digest": row.transfer_success_evidence_digest,
            "actor_user_id": str(operator.pk),
            "actor_role_code": role_code,
            "actor_team_codes": sorted(operator.team_codes()),
            "request_id": request_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "outcome": "sent",
        }
        AuditLog.objects.create(
            actor_user=operator,
            actor_type="user",
            action=ADVICE_ACTION,
            entity_type="disbursement",
            entity_id=row.pk,
            old_value_json={"disbursement_advice_communication_id": None},
            new_value_json=evidence,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        record_workflow_event(
            actor=operator,
            workflow_name="DisbursementAdviceSent",
            entity_type="disbursement",
            entity_id=row.pk,
            from_state="transfer_successful",
            to_state="advice_sent",
            trigger_reason=(
                f"action_id={action_id};communication_id={communication.pk};"
                f"request_id={request_id}"
            ),
            action_code=ADVICE_ACTION,
            metadata=evidence,
        )
        row.disbursement_advice_communication = communication
        row.save(update_fields=["disbursement_advice_communication"])
        return serialize_advice(communication)


def serialize_advice(communication):
    return {
        "disbursement_id": str(communication.related_entity_id),
        "disbursement_advice_communication_id": str(communication.pk),
        "delivery_status": communication.delivery_status,
        "sent_at": _iso(communication.sent_at),
    }


def _validate_payload(payload):
    if not isinstance(payload, dict):
        raise ValidationError({"non_field_errors": "A JSON object is required."})
    allowed = {"channel", "recipient_email"}
    errors = {field: "Unknown field." for field in sorted(set(payload) - allowed)}
    for field in allowed - set(payload):
        errors[field] = "This field is required."
    channel = payload.get("channel")
    if not isinstance(channel, str) or not channel.strip():
        errors["channel"] = "This field is required."
    email = _normalize_email(payload.get("recipient_email"))
    try:
        validate_email(email)
    except ValidationError:
        errors["recipient_email"] = "Enter a valid email address."
    if errors:
        raise ValidationError(errors)
    return {"channel": channel.strip().lower(), "recipient_email": email}


def _canonical_email(value):
    email = _normalize_email(value)
    try:
        validate_email(email)
    except ValidationError as exc:
        raise DisbursementAdviceConflict(
            "The member has no valid canonical email address."
        ) from exc
    return email


def _normalize_email(value):
    return value.strip().lower() if isinstance(value, str) else ""


def _locked_operator(actor):
    operator = (
        User.objects.select_for_update()
        .select_related("primary_role")
        .filter(pk=getattr(actor, "pk", None), status=User.ACTIVE_STATUS)
        .first()
    )
    permission = Permission.objects.filter(
        permission_code=SEND_ADVICE_PERMISSION,
        risk_level=Permission.RISK_HIGH,
    ).first()
    if (
        operator is None
        or not operator.can_authenticate()
        or operator.primary_role.status != "active"
        or permission is None
        or SEND_ADVICE_PERMISSION
        not in auth_service.effective_permission_codes(operator)
    ):
        raise DomainPermissionDenied("Active disbursement-advice authority is required.")
    return operator


def _require_operator_scope(operator, row):
    roles = set(auth_service.effective_role_codes(operator))
    if _CFC_ROLE in roles and row.authorised_by_user_id == operator.pk:
        return _CFC_ROLE
    if _FINANCE_ROLE in roles and row.initiated_by_user_id == operator.pk:
        return _FINANCE_ROLE
    raise DomainObjectAccessDenied(None)


def _lock_source_relations(row):
    from sfpcl_credit.applications.models import LoanApplication
    from sfpcl_credit.documents.models import DocumentFile
    from sfpcl_credit.loans.models import LoanAccount, LoanStatusHistory
    from sfpcl_credit.members.models import Member
    from sfpcl_credit.workflows.models import WorkflowEvent

    row.loan_application = LoanApplication.objects.select_for_update().get(
        pk=row.loan_application_id
    )
    row.loan_account = (
        LoanAccount.objects.select_for_update()
        .select_related("terms")
        .get(pk=row.loan_account_id)
    )
    row.member = Member.objects.select_for_update().get(pk=row.member_id)
    transfer = BankTransfer.objects.select_for_update().filter(disbursement=row).first()
    if transfer is not None:
        row._state.fields_cache["bank_transfer"] = transfer
    DocumentFile.objects.select_for_update().filter(
        pk=row.bank_transfer_evidence_document_id
    ).first()
    transfer_audit = AuditLog.objects.select_for_update().filter(
        pk=row.transfer_success_audit_id
    ).first()
    if transfer_audit is not None:
        row.transfer_success_audit = transfer_audit
    authorisation_audit = AuditLog.objects.select_for_update().filter(
        pk=row.authorisation_audit_id
    ).first()
    if authorisation_audit is not None:
        row.authorisation_audit = authorisation_audit
    transfer_workflow = WorkflowEvent.objects.select_for_update().filter(
        pk=row.transfer_success_workflow_event_id
    ).first()
    if transfer_workflow is not None:
        row.transfer_success_workflow_event = transfer_workflow
    authorisation_workflow = WorkflowEvent.objects.select_for_update().filter(
        pk=row.authorisation_workflow_event_id
    ).first()
    if authorisation_workflow is not None:
        row.authorisation_workflow_event = authorisation_workflow
    LoanStatusHistory.objects.select_for_update().filter(
        pk=row.transfer_success_loan_status_history_id
    ).first()


def _locked_current_template():
    today = timezone.localdate()
    rows = list(
        ContentTemplate.objects.select_for_update()
        .filter(
            template_code__startswith="disbursement_advice_email_",
            template_type="email",
            audience="borrower",
            approval_status=ContentTemplate.STATUS_APPROVED,
            effective_from__lte=today,
        )
        .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=today))
        .order_by("content_template_id")[:2]
    )
    if len(rows) != 1 or set(rows[0].variables_json or []) != ADVICE_VARIABLES:
        raise DisbursementAdviceConflict(
            "Exactly one approved effective disbursement advice template is required."
        )
    template = rows[0]
    declared_tokens = set(_TOKEN_RE.findall(template.subject_template or "")) | set(
        _TOKEN_RE.findall(template.body_template)
    )
    if declared_tokens != ADVICE_VARIABLES:
        raise DisbursementAdviceConflict(
            "The disbursement advice template variables are incomplete or unexpected."
        )
    return template


def _merge_data(row):
    return {
        "borrower_name": row.member.display_name,
        "application_reference_number": row.loan_application.application_reference_number,
        "loan_account_number": row.loan_account.loan_account_number,
        "sanctioned_amount": f"{row.loan_account.sanctioned_amount:.2f}",
        "disbursement_amount": f"{row.disbursement_amount:.2f}",
        "disbursed_at": row.disbursed_at.date().isoformat(),
        "bank_reference_number": _masked_reference(row.bank_reference_number),
    }


def _render(value, merge_data):
    rendered = value
    for key, replacement in merge_data.items():
        rendered = re.sub(
            rf"{{{{\s*{re.escape(key)}\s*}}}}", str(replacement), rendered
        )
    if _TOKEN_RE.search(rendered):
        raise DisbursementAdviceConflict(
            "The disbursement advice template could not be rendered."
        )
    return rendered


def _retained_advice_is_coherent(row, cleaned, *, operator, role_code):
    communication = row.disbursement_advice_communication
    audits = list(
        AuditLog.objects.select_for_update()
        .filter(action=ADVICE_ACTION, entity_type="disbursement", entity_id=row.pk)
        .order_by("audit_log_id")[:2]
    )
    workflows = list(
        row.transfer_success_workflow_event.__class__.objects.select_for_update()
        .filter(
            workflow_name="DisbursementAdviceSent",
            entity_type="disbursement",
            entity_id=row.pk,
        )
        .order_by("workflow_event_id")[:2]
    )
    evidence = audits[0].new_value_json if len(audits) == 1 else {}
    audit = audits[0] if len(audits) == 1 else None
    workflow = workflows[0] if len(workflows) == 1 else None
    template = communication.content_template
    try:
        uuid.UUID(evidence.get("action_id", ""))
    except (ValueError, TypeError, AttributeError):
        return False
    expected_evidence = {
        "disbursement_id": str(row.pk),
        "communication_id": str(communication.pk),
        "loan_account_id": str(row.loan_account_id),
        "loan_application_id": str(row.loan_application_id),
        "member_id": str(row.member_id),
        "template_id": str(communication.content_template_id),
        "template_code": template.template_code if template else None,
        "template_version": template.template_version if template else None,
        "recipient_email": communication.recipient_address,
        "channel": communication.channel,
        "delivery_status": communication.delivery_status,
        "external_message_id": communication.external_message_id,
        "sent_at": _iso(communication.sent_at) if communication.sent_at else None,
        "disbursement_amount": f"{row.disbursement_amount:.2f}",
        "bank_reference_masked": _masked_reference(row.bank_reference_number),
        "transfer_success_action_id": str(row.transfer_success_action_id),
        "transfer_success_evidence_digest": row.transfer_success_evidence_digest,
        "actor_user_id": str(operator.pk),
        "actor_role_code": role_code,
        "request_id": evidence.get("request_id"),
        "ip_address": evidence.get("ip_address"),
        "user_agent": evidence.get("user_agent"),
        "outcome": "sent",
    }
    return bool(
        cleaned["channel"] == communication.channel == "email"
        and cleaned["recipient_email"] == communication.recipient_address
        and communication.related_entity_type == "disbursement"
        and communication.related_entity_id == row.pk
        and communication.recipient_party_type == "borrower"
        and communication.recipient_party_id == row.member_id
        and communication.delivery_status == "sent"
        and communication.sent_at
        and communication.external_message_id
        and communication.content_template_id
        and len(audits) == 1
        and len(workflows) == 1
        and audit.actor_user_id == operator.pk
        and audit.actor_type == "user"
        and audit.entity_type == "disbursement"
        and audit.entity_id == row.pk
        and audit.old_value_json == {"disbursement_advice_communication_id": None}
        and all(evidence.get(key) == value for key, value in expected_evidence.items())
        and isinstance(evidence.get("actor_team_codes"), list)
        and audit.ip_address == evidence.get("ip_address")
        and audit.user_agent == evidence.get("user_agent")
        and workflow.entity_id == row.pk
        and workflow.from_state == "transfer_successful"
        and workflow.to_state == "advice_sent"
        and workflow.triggered_by_user_id == operator.pk
        and workflow.trigger_reason
        == (
            f"action_id={evidence['action_id']};communication_id={communication.pk};"
            f"request_id={evidence['request_id']}"
        )
    )


def _request_id(request):
    supplied = request.headers.get("X-Request-ID", "").strip() if request else ""
    return supplied if supplied and len(supplied) <= 255 else f"req_advice_{uuid.uuid4().hex}"


def _iso(value):
    return value.isoformat().replace("+00:00", "Z")


__all__ = [
    "DisbursementAdviceConflict",
    "DisbursementAdviceDeliveryFailed",
]
