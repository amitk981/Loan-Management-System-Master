from dataclasses import dataclass
import uuid

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

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


SEND_ADVICE_PERMISSION = "finance.disbursement.send_advice"
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

    def __init__(self, message, *, failure_code="provider_rejected"):
        super().__init__(message)
        self.failure_code = failure_code


@dataclass(frozen=True)
class _AdviceContext:
    operator: User
    row: Disbursement
    role_code: str
    canonical_email: str
    intent: DisbursementAdviceIntent
    dispatch_context: DisbursementAdviceContext


def _queue_advice(*, actor, disbursement_id, payload, request=None):
    from sfpcl_credit.processes.disbursement_advice_delivery import (
        queue_disbursement_advice,
    )

    return queue_disbursement_advice(
        actor=actor,
        disbursement_id=disbursement_id,
        payload=payload,
        request=request,
    )


def _send_advice(*, actor, disbursement_id, payload, request=None, adapter=None):
    from sfpcl_credit.processes.disbursement_advice_delivery import (
        send_disbursement_advice_now,
    )

    return send_disbursement_advice_now(
        actor=actor,
        disbursement_id=disbursement_id,
        payload=payload,
        request=request,
        adapter=adapter,
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
    intent = context.intent
    if (
        cleaned["channel"] == "email"
        and cleaned["recipient_email"] == context.canonical_email
        and row.disbursement_advice_communication_id == decision.communication_id
        and intent.delivery_status == DisbursementAdviceIntent.DELIVERY_SENT
        and intent.delivery_action_id == decision.action_id
        and intent.delivery_audit_id == decision.audit_id
        and intent.delivery_workflow_event_id == decision.workflow_id
        and intent.delivery_evidence_digest == decision.delivery_evidence_digest
    ):
        return serialize_advice(row.pk, decision)
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


def _consume_finalization(context, decision):
    row = context.row
    intent = context.intent
    intent.delivery_status = DisbursementAdviceIntent.DELIVERY_SENT
    intent.delivery_action_id = decision.action_id
    intent.delivery_audit_id = decision.audit_id
    intent.delivery_workflow_event_id = decision.workflow_id
    intent.delivery_evidence_digest = decision.delivery_evidence_digest
    intent.save(
        update_fields=[
            "delivery_status",
            "delivery_action_id",
            "delivery_audit",
            "delivery_workflow_event",
            "delivery_evidence_digest",
        ]
    )
    row.disbursement_advice_communication_id = decision.communication_id
    row.save(update_fields=["disbursement_advice_communication"])
    return serialize_advice(row.pk, decision)


def serialize_advice(disbursement_id, decision):
    return {
        "disbursement_id": str(disbursement_id),
        "disbursement_advice_communication_id": str(decision.communication_id),
        "delivery_status": decision.delivery_status,
        "sent_at": _iso(decision.sent_at),
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


def resolve_current_advice_context(*, disbursement_id):
    """Return immutable primitive context only for the current sent advice chain."""
    row = (
        Disbursement.objects.select_related(
            "member",
            "loan_application",
            "loan_account",
            "loan_account__terms",
            "bank_transfer",
            "bank_transfer_evidence_document",
            "authorisation_audit",
            "authorisation_workflow_event",
            "transfer_success_audit",
            "transfer_success_workflow_event",
            "transfer_success_loan_status_history",
            "advice_intent",
            "advice_intent__delivery_audit",
            "advice_intent__delivery_workflow_event",
            "loan_register_update",
            "register_update",
            "disbursement_advice_communication",
        )
        .filter(pk=disbursement_id)
        .first()
    )
    if row is None or not row.disbursement_advice_communication_id:
        return None
    intent = row.advice_intent
    audit = intent.delivery_audit
    communication = row.disbursement_advice_communication
    evidence = audit.new_value_json if audit else None
    if not (
        completed_success_is_coherent(row)
        and intent.delivery_status == DisbursementAdviceIntent.DELIVERY_SENT
        and intent.delivery_action_id
        and intent.delivery_evidence_digest
        and intent.delivery_workflow_event_id
        and audit
        and isinstance(evidence, dict)
        and audit.actor_user_id == communication.sent_by_user_id
        and evidence.get("actor_user_id") == str(audit.actor_user_id)
        and isinstance(evidence.get("actor_role_code"), str)
        and evidence.get("actor_role_code")
        and isinstance(evidence.get("actor_team_codes"), list)
    ):
        return None
    try:
        canonical_email = _canonical_email(row.member.email)
    except DisbursementAdviceConflict:
        return None
    merge_values = (
        ("borrower_name", row.member.display_name),
        ("application_reference_number", row.loan_application.application_reference_number),
        ("loan_account_number", row.loan_account.loan_account_number),
        ("sanctioned_amount", f"{row.loan_account.sanctioned_amount:.2f}"),
        ("disbursement_amount", f"{row.disbursement_amount:.2f}"),
        ("disbursed_at", row.disbursed_at.date().isoformat()),
        ("bank_reference_number", _masked_reference(row.bank_reference_number)),
    )
    return DisbursementAdviceContext(
        actor_id=audit.actor_user_id,
        actor_role_code=evidence["actor_role_code"],
        actor_team_codes=tuple(evidence["actor_team_codes"]),
        advice_intent_id=intent.pk,
        intent_created_at=intent.created_at,
        communication_id=communication.pk,
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
    )


def _request_id(request):
    supplied = request.headers.get("X-Request-ID", "").strip() if request else ""
    return supplied if supplied and len(supplied) <= 255 else f"req_advice_{uuid.uuid4().hex}"


def _iso(value):
    return value.isoformat().replace("+00:00", "Z")


__all__ = [
    "DisbursementAdviceConflict",
    "DisbursementAdviceDeliveryFailed",
    "resolve_current_advice_context",
]
