from dataclasses import dataclass
import hashlib
import json
import uuid

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.communications.modules.communication_dispatcher import (
    AdviceDeliveryDecision,
    CommunicationDeliveryFailed,
    CommunicationDispatcher,
    CommunicationDispatchConflict,
)
from sfpcl_credit.communications.models import (
    Communication,
    DisbursementAdviceDeliveryReceipt,
)
from sfpcl_credit.disbursements.models import (
    BankTransfer,
    Disbursement,
    DisbursementAdviceIntent,
    LoanRegisterUpdate,
)
from sfpcl_credit.disbursements.modules.disbursement_transfer_success import (
    _masked_reference,
    completed_success_is_coherent,
)
from sfpcl_credit.disbursements.modules.disbursement_advice_context import (
    DisbursementAdviceContext,
)
from sfpcl_credit.domain_errors import DomainObjectAccessDenied, DomainPermissionDenied
from sfpcl_credit.identity.models import AuditLog, Permission, User
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.sap_workflow.modules.sap_customer_profile import (
    SapCustomerProfileModule,
)
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
_CREDIT_ROLE = "credit_manager"
_FINANCE_ROLE = "senior_manager_finance"
_CREDIT_ACTIVE_LOAN_STATUSES = {"active", "partially_repaid"}


class DisbursementAdviceConflict(Exception):
    code = "CONFLICT"


class DisbursementAdviceDeliveryFailed(DisbursementAdviceConflict):
    code = "DELIVERY_FAILED"


@dataclass(frozen=True)
class _AdviceContext:
    operator: User
    row: Disbursement
    role_code: str
    canonical_email: str
    intent: DisbursementAdviceIntent
    dispatch_context: DisbursementAdviceContext


def _send_advice(*, actor, disbursement_id, payload, request=None, adapter=None):
    cleaned = _validate_payload(payload)
    with transaction.atomic():
        context = _locked_advice_context(actor, disbursement_id)
        if context.row.disbursement_advice_communication_id is None:
            _validate_request_context(context, cleaned)
            _require_pending_delivery(context)
    try:
        decision = CommunicationDispatcher.dispatch(
            context=context.dispatch_context,
            adapter=adapter,
        )
    except CommunicationDeliveryFailed as exc:
        raise DisbursementAdviceDeliveryFailed(str(exc)) from exc
    except CommunicationDispatchConflict as exc:
        raise DisbursementAdviceConflict(str(exc)) from exc
    receipt = _retained_receipt(decision)

    with transaction.atomic():
        context = _locked_advice_context(actor, disbursement_id)
        try:
            decision = CommunicationDispatcher.dispatch(
                context=context.dispatch_context,
            )
        except CommunicationDispatchConflict as exc:
            raise DisbursementAdviceConflict(str(exc)) from exc
        replay = _current_replay(context, cleaned, decision)
        if replay is not None:
            return replay
        _validate_request_context(context, cleaned)
        _require_pending_delivery(context)
        if not _receipt_matches(
            receipt,
            decision=decision,
        ):
            raise DisbursementAdviceConflict(
                "The retained provider acceptance is stale or incoherent."
            )
        return _persist_accepted_delivery(
            context, receipt, decision, request=request
        )


def _locked_advice_context(actor, disbursement_id):
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
            "advice_intent",
            "loan_register_update",
            "disbursement_advice_communication",
            "disbursement_advice_communication__content_template",
        )
        .filter(pk=disbursement_id)
        .first()
    )
    if row is None:
        raise DomainObjectAccessDenied(None)
    _lock_source_relations(row)
    role_code = _require_operator_scope(operator, row)
    canonical_email = _canonical_email(row.member.email)
    if not completed_success_is_coherent(row):
        raise DisbursementAdviceConflict(
            "The successful disbursement evidence is stale or incoherent."
        )
    merge_values = (
        ("borrower_name", row.member.display_name),
        (
            "application_reference_number",
            row.loan_application.application_reference_number,
        ),
        ("loan_account_number", row.loan_account.loan_account_number),
        ("sanctioned_amount", f"{row.loan_account.sanctioned_amount:.2f}"),
        ("disbursement_amount", f"{row.disbursement_amount:.2f}"),
        ("disbursed_at", row.disbursed_at.date().isoformat()),
        ("bank_reference_number", _masked_reference(row.bank_reference_number)),
    )
    return _AdviceContext(
        operator=operator,
        row=row,
        role_code=role_code,
        canonical_email=canonical_email,
        intent=row.advice_intent,
        dispatch_context=DisbursementAdviceContext(
            actor_id=operator.pk,
            actor_role_code=role_code,
            actor_team_codes=tuple(sorted(operator.team_codes())),
            advice_intent_id=row.advice_intent.pk,
            intent_created_at=row.advice_intent.created_at,
            communication_id=row.advice_intent.pk,
            recipient_address=canonical_email,
            recipient_party_id=row.member_id,
            related_entity_type="disbursement",
            related_entity_id=row.pk,
            template_code_prefix="disbursement_advice_email_",
            template_type="email",
            template_audience="borrower",
            required_variables=tuple(sorted(ADVICE_VARIABLES)),
            merge_values=merge_values,
            sensitive_values=(row.bank_reference_number,),
            loan_account_id=row.loan_account_id,
            loan_application_id=row.loan_application_id,
            member_id=row.member_id,
            disbursement_amount=row.disbursement_amount,
            disbursed_at=row.disbursed_at.date(),
            masked_bank_reference=_masked_reference(row.bank_reference_number),
            transfer_success_action_id=row.transfer_success_action_id,
            transfer_success_evidence_digest=row.transfer_success_evidence_digest,
        ),
    )


def _current_replay(context, cleaned, decision):
    row = context.row
    if row.disbursement_advice_communication_id is None:
        return None
    if _retained_advice_is_coherent(context, cleaned, decision):
        return serialize_advice(row.disbursement_advice_communication)
    raise DisbursementAdviceConflict(
        "The disbursement already has different or stale advice evidence."
    )


def _validate_request_context(context, cleaned):
    if cleaned["channel"] != "email":
        raise ValidationError({"channel": "Only email is supported."})
    if cleaned["recipient_email"] != context.canonical_email:
        raise ValidationError(
            {"recipient_email": "Must match the member's current email address."}
        )


def _require_pending_delivery(context):
    if context.intent.delivery_status != DisbursementAdviceIntent.DELIVERY_PENDING:
        raise DisbursementAdviceConflict(
            "The pending disbursement advice identity is stale or incoherent."
        )


def _retained_receipt(decision: AdviceDeliveryDecision):
    with transaction.atomic():
        receipt, _created = (
            DisbursementAdviceDeliveryReceipt.objects.select_for_update().get_or_create(
                advice_intent_id=decision.advice_intent_id,
                defaults={
                    "idempotency_key": decision.idempotency_key,
                    "payload_digest": decision.payload_digest,
                    "external_message_id": decision.external_message_id,
                    "delivery_status": decision.delivery_status,
                    "accepted_at": decision.accepted_at,
                },
            )
        )
    if not _receipt_matches(receipt, decision=decision):
        raise DisbursementAdviceConflict(
            "The retained provider acceptance is stale or incoherent."
        )
    return receipt


def _receipt_matches(receipt, *, decision):
    return bool(
        receipt.advice_intent_id == decision.advice_intent_id
        and receipt.idempotency_key == decision.idempotency_key
        and receipt.payload_digest == decision.payload_digest
        and receipt.delivery_status == decision.delivery_status == "sent"
        and receipt.external_message_id == decision.external_message_id
        and receipt.accepted_at == decision.accepted_at
    )


def _persist_accepted_delivery(context, receipt, decision, *, request):
    operator = context.operator
    row = context.row
    intent = context.intent
    action_id = uuid.uuid4()
    communication = Communication.objects.create(
        communication_id=decision.communication_id,
        related_entity_type=decision.related_entity_type,
        related_entity_id=decision.related_entity_id,
        recipient_party_type="borrower",
        recipient_party_id=row.member_id,
        recipient_address=decision.recipient_address,
        channel="email",
        content_template_id=decision.template_id,
        subject_snapshot=decision.subject,
        body_snapshot=decision.body,
        sent_by_user=operator,
        sent_at=receipt.accepted_at,
        delivery_status=receipt.delivery_status,
        external_message_id=receipt.external_message_id,
    )
    request_id = _request_id(request)
    ip_address = request_ip(request) if request else ""
    user_agent = request_user_agent(request) if request else ""
    evidence = _advice_audit_evidence(
        context,
        receipt,
        decision,
        action_id=action_id,
        request_id=request_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    audit = AuditLog.objects.create(
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
    workflow = record_workflow_event(
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
    intent.delivery_status = DisbursementAdviceIntent.DELIVERY_SENT
    intent.delivery_action_id = action_id
    intent.delivery_audit = audit
    intent.delivery_workflow_event = workflow
    intent.delivery_evidence_digest = _delivery_evidence_digest(
        context,
        receipt,
        decision,
        evidence=evidence,
        audit=audit,
        workflow=workflow,
    )
    intent.save(
        update_fields=[
            "delivery_status",
            "delivery_action_id",
            "delivery_audit",
            "delivery_workflow_event",
            "delivery_evidence_digest",
        ]
    )
    row.disbursement_advice_communication = communication
    row.save(update_fields=["disbursement_advice_communication"])
    return serialize_advice(communication)


def _advice_audit_evidence(
    context, receipt, decision, *, action_id, request_id, ip_address, user_agent
):
    row = context.row
    return {
        "action_id": str(action_id),
        "disbursement_id": str(row.pk),
        "communication_id": str(context.intent.pk),
        "loan_account_id": str(row.loan_account_id),
        "loan_application_id": str(row.loan_application_id),
        "member_id": str(row.member_id),
        "template_id": str(decision.template_id),
        "template_code": decision.template_code,
        "template_version": decision.template_version,
        "recipient_masked": _masked_email(decision.recipient_address),
        "recipient_digest": decision.recipient_digest,
        "channel": "email",
        "delivery_status": receipt.delivery_status,
        "external_message_id": receipt.external_message_id,
        "sent_at": _iso(receipt.accepted_at),
        "disbursement_amount": f"{row.disbursement_amount:.2f}",
        "bank_reference_masked": _masked_reference(row.bank_reference_number),
        "transfer_success_action_id": str(row.transfer_success_action_id),
        "transfer_success_evidence_digest": row.transfer_success_evidence_digest,
        "actor_user_id": str(context.operator.pk),
        "actor_role_code": context.role_code,
        "actor_team_codes": sorted(context.operator.team_codes()),
        "request_id": request_id,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "outcome": "sent",
    }


def _delivery_evidence_digest(
    context, receipt, decision, *, evidence, audit, workflow
):
    facts = {
        "advice_intent_id": str(context.intent.pk),
        "intent_created_at": _iso(context.intent.created_at),
        "audit_evidence": evidence,
        "audit_id": str(audit.pk),
        "audit_created_at": _iso(audit.created_at),
        "workflow_id": str(workflow.pk),
        "workflow_created_at": _iso(workflow.created_at),
        "workflow_trigger_reason": workflow.trigger_reason,
        "receipt_id": str(receipt.pk),
        "receipt_payload_digest": receipt.payload_digest,
        "subject_digest": hashlib.sha256(decision.subject.encode()).hexdigest(),
        "body_digest": hashlib.sha256(decision.body.encode()).hexdigest(),
        "template_approval_status": decision.template_approval_status,
        "template_effective_from": decision.template_effective_from.isoformat(),
        "template_effective_to": (
            decision.template_effective_to.isoformat()
            if decision.template_effective_to
            else None
        ),
        "template_variables": list(decision.template_variables),
    }
    return hashlib.sha256(
        json.dumps(facts, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


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
    if (
        _FINANCE_ROLE in roles
        and row.initiated_by_user_id == operator.pk
        and SapCustomerProfileModule.is_current_finance_assignee(
            application_id=row.loan_application_id,
            member_id=row.member_id,
            actor_id=operator.pk,
        )
    ):
        return _FINANCE_ROLE
    if (
        _CREDIT_ROLE in roles
        and row.loan_account.loan_account_status in _CREDIT_ACTIVE_LOAN_STATUSES
        and row.loan_account.loan_application_id == row.loan_application_id
        and row.loan_account.member_id == row.member_id
        and row.loan_application.member_id == row.member_id
    ):
        return _CREDIT_ROLE
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
        LoanAccount.objects.select_for_update(of=("self",))
        .select_related("terms")
        .get(pk=row.loan_account_id)
    )
    row.member = Member.objects.select_for_update().get(pk=row.member_id)
    intent = (
        DisbursementAdviceIntent.objects.select_for_update()
        .filter(disbursement=row)
        .first()
    )
    if intent is not None:
        row._state.fields_cache["advice_intent"] = intent
    register_update = (
        LoanRegisterUpdate.objects.select_for_update()
        .filter(disbursement=row)
        .first()
    )
    if register_update is not None:
        row._state.fields_cache["loan_register_update"] = register_update
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


def _retained_advice_is_coherent(context, cleaned, decision):
    row = context.row
    intent = context.intent
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
    audit = audits[0] if len(audits) == 1 else None
    workflow = workflows[0] if len(workflows) == 1 else None
    receipt = (
        DisbursementAdviceDeliveryReceipt.objects.select_for_update()
        .filter(advice_intent=intent)
        .first()
    )
    if audit is None or workflow is None or receipt is None:
        return False
    evidence = audit.new_value_json
    if not isinstance(evidence, dict):
        return False
    try:
        action_id = uuid.UUID(evidence.get("action_id", ""))
    except (ValueError, TypeError, AttributeError):
        return False
    expected_evidence = _advice_audit_evidence(
        context,
        receipt,
        decision,
        action_id=action_id,
        request_id=evidence.get("request_id"),
        ip_address=evidence.get("ip_address"),
        user_agent=evidence.get("user_agent"),
    )
    expected_trigger = (
        f"action_id={action_id};communication_id={communication.pk};"
        f"request_id={evidence.get('request_id')}"
    )
    receipt_current = _receipt_matches(
        receipt,
        decision=decision,
    )
    expected_digest = _delivery_evidence_digest(
        context,
        receipt,
        decision,
        evidence=evidence,
        audit=audit,
        workflow=workflow,
    )
    return bool(
        cleaned["channel"] == communication.channel == "email"
        and cleaned["recipient_email"]
        == context.canonical_email
        == decision.recipient_address
        == communication.recipient_address
        and communication.related_entity_type == decision.related_entity_type
        and communication.related_entity_id == decision.related_entity_id == row.pk
        and communication.recipient_party_type == "borrower"
        and communication.recipient_party_id == row.member_id
        and communication.sent_by_user_id == context.operator.pk
        and communication.delivery_status == receipt.delivery_status == "sent"
        and communication.sent_at == receipt.accepted_at
        and communication.external_message_id == receipt.external_message_id
        and communication.content_template_id == decision.template_id
        and communication.subject_snapshot == decision.subject
        and communication.body_snapshot == decision.body
        and intent.pk == communication.pk
        and intent.delivery_status == DisbursementAdviceIntent.DELIVERY_SENT
        and intent.delivery_action_id == action_id
        and intent.delivery_audit_id == audit.pk
        and intent.delivery_workflow_event_id == workflow.pk
        and intent.delivery_evidence_digest == expected_digest
        and receipt_current
        and len(audits) == 1
        and len(workflows) == 1
        and audit.actor_user_id == context.operator.pk
        and audit.actor_type == "user"
        and audit.action == ADVICE_ACTION
        and audit.entity_type == "disbursement"
        and audit.entity_id == row.pk
        and audit.old_value_json == {"disbursement_advice_communication_id": None}
        and evidence == expected_evidence
        and audit.ip_address == evidence.get("ip_address")
        and audit.user_agent == evidence.get("user_agent")
        and workflow.workflow_name == "DisbursementAdviceSent"
        and workflow.entity_id == row.pk
        and workflow.from_state == "transfer_successful"
        and workflow.to_state == "advice_sent"
        and workflow.triggered_by_user_id == context.operator.pk
        and workflow.trigger_reason == expected_trigger
    )


def _request_id(request):
    supplied = request.headers.get("X-Request-ID", "").strip() if request else ""
    return supplied if supplied and len(supplied) <= 255 else f"req_advice_{uuid.uuid4().hex}"


def _masked_email(email):
    local, domain = email.split("@", 1)
    return f"{local[:1]}***@{domain}"


def _iso(value):
    return value.isoformat().replace("+00:00", "Z")


__all__ = [
    "DisbursementAdviceConflict",
    "DisbursementAdviceDeliveryFailed",
]
