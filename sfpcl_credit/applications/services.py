import uuid
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.members.models import BankAccount, CancelledCheque, CropPlan, LandHolding, Member
from sfpcl_credit.workflows.events import record_workflow_event
from sfpcl_credit.workflows.guard import (
    TransitionDefinition,
    evaluate_transition,
)


APPLICATION_READ_PERMISSION = "applications.loan_application.read"
APPLICATION_CREATE_PERMISSION = "applications.loan_application.create"
APPLICATION_UPDATE_PERMISSION = "applications.loan_application.update"
APPLICATION_SUBMIT_PERMISSION = "applications.loan_application.submit"
APPLICATION_TRANSITIONS = (
    TransitionDefinition(
        entity_type="loan_application",
        action_code="submit",
        from_states=frozenset({LoanApplication.STATUS_DRAFT}),
        to_state=LoanApplication.STATUS_SUBMITTED,
        required_permission=APPLICATION_SUBMIT_PERMISSION,
        audit_action="applications.loan_application.submitted",
        workflow_name="loan_application",
        workflow_label="Application submitted for completeness review.",
    ),
)
_CREATE_FIELDS = {
    "member_id",
    "required_loan_amount",
    "requested_tenure_months",
    "declared_purpose",
    "purpose_category",
    "loan_type_requested",
    "land_holding_id",
    "crop_plan_id",
    "bank_account_id",
    "cancelled_cheque_id",
    "borrower_request_notes",
    "terms_acceptance_flag",
}
_UPDATE_FIELDS = _CREATE_FIELDS - {"member_id"}


class LoanApplicationValidationError(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors
        super().__init__("Loan application payload failed validation.")


def user_can_read_applications(user):
    return APPLICATION_READ_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_create_applications(user):
    return APPLICATION_CREATE_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_update_applications(user):
    return APPLICATION_UPDATE_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_submit_applications(user):
    return APPLICATION_SUBMIT_PERMISSION in auth_service.effective_permission_codes(user)


def get_application(application_id):
    return (
        LoanApplication.objects.select_related(
            "member",
            "land_holding",
            "crop_plan",
            "bank_account",
            "cancelled_cheque",
            "created_by_user",
            "updated_by_user",
            "submitted_by_user",
        )
        .filter(loan_application_id=application_id)
        .first()
    )


@transaction.atomic
def create_draft(payload, actor, request_ip="", request_user_agent="", request_id=None):
    cleaned = _clean_payload(payload, require_member=True)
    application = LoanApplication(
        member=cleaned["member"],
        borrower_type=cleaned["member"].member_type,
        received_by_user=actor,
        created_by_user=actor,
        updated_by_user=actor,
        updated_at=timezone.now(),
    )
    _assign_fields(application, cleaned)
    application.save()
    _audit_application(
        application,
        actor,
        "applications.loan_application.created",
        None,
        request_ip,
        request_user_agent,
        request_id,
    )
    record_workflow_event(
        actor=actor,
        workflow_name="loan_application",
        entity_type="loan_application",
        entity_id=application.loan_application_id,
        from_state=None,
        to_state=LoanApplication.STATUS_DRAFT,
        trigger_reason="Draft application created.",
    )
    return application


@transaction.atomic
def update_draft(application, payload, actor, request_ip="", request_user_agent="", request_id=None):
    if application.application_status != LoanApplication.STATUS_DRAFT:
        raise LoanApplicationValidationError(
            {"application_status": "Only draft applications can be updated."}
        )
    cleaned = _clean_update_payload(payload, application.member)
    old_value_json = _audit_snapshot(application)
    for field, value in cleaned.items():
        setattr(application, field, value)
    application.updated_by_user = actor
    application.updated_at = timezone.now()
    application.save()
    _audit_application(
        application,
        actor,
        "applications.loan_application.updated",
        old_value_json,
        request_ip,
        request_user_agent,
        request_id,
    )
    return application


@transaction.atomic
def submit_application(
    application,
    actor,
    request_ip="",
    request_user_agent="",
    request_id=None,
    actor_permissions=None,
):
    transition = evaluate_transition(
        current_state=application.application_status,
        requested_action="submit",
        actor_permissions=actor_permissions or auth_service.effective_permission_codes(actor),
        transitions=APPLICATION_TRANSITIONS,
    )
    _validate_submit_facts(application)
    old_value_json = _audit_snapshot(application)
    application.application_status = transition.next_state
    application.submitted_at = timezone.now()
    application.submitted_by_user = actor
    application.updated_at = application.submitted_at
    application.updated_by_user = actor
    application.save()
    _audit_application(
        application,
        actor,
        transition.definition.audit_action,
        old_value_json,
        request_ip,
        request_user_agent,
        request_id,
    )
    record_workflow_event(
        actor=actor,
        workflow_name=transition.definition.workflow_name,
        entity_type=transition.definition.entity_type,
        entity_id=application.loan_application_id,
        from_state=transition.previous_state,
        to_state=transition.next_state,
        trigger_reason=transition.definition.workflow_label,
        action_code=transition.definition.action_code,
    )
    return application


def serialize_application(application):
    return {
        "loan_application_id": str(application.loan_application_id),
        "application_reference_number": application.application_reference_number,
        "member": _member_summary(application.member),
        "application_date": application.application_date.isoformat(),
        "required_loan_amount": _money(application.required_loan_amount),
        "requested_tenure_months": application.requested_tenure_months,
        "declared_purpose": application.declared_purpose,
        "purpose_category": application.purpose_category,
        "loan_type_requested": application.loan_type_requested or None,
        "land_holding": _land_summary(application.land_holding),
        "crop_plan": _crop_summary(application.crop_plan),
        "bank_account": _bank_summary(application.bank_account),
        "cancelled_cheque": _cheque_summary(application.cancelled_cheque),
        "borrower_request_notes": application.borrower_request_notes,
        "application_status": application.application_status,
        "current_stage": application.current_stage,
        "completeness_status": application.completeness_status,
        "terms_acceptance_flag": application.terms_acceptance_flag,
        "created_at": _datetime(application.created_at),
        "created_by_user_id": str(application.created_by_user_id)
        if application.created_by_user_id
        else None,
        "submitted_at": _datetime(application.submitted_at),
        "submitted_by_user_id": str(application.submitted_by_user_id)
        if application.submitted_by_user_id
        else None,
        "updated_at": _datetime(application.updated_at),
        "updated_by_user_id": str(application.updated_by_user_id)
        if application.updated_by_user_id
        else None,
    }


def validation_field_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    if isinstance(exc, LoanApplicationValidationError):
        return exc.field_errors
    return {"non_field_errors": str(exc)}


def _validate_submit_facts(application):
    errors = {}
    if application.member_id is None:
        errors["member_id"] = "Borrower member is required."
    if application.required_loan_amount is None or application.required_loan_amount <= 0:
        errors["required_loan_amount"] = "Requested amount must be greater than zero."
    if not application.declared_purpose.strip():
        errors["declared_purpose"] = "Declared purpose is required before submit."
    if not application.purpose_category.strip():
        errors["purpose_category"] = "Purpose category is required before submit."
    if errors:
        raise LoanApplicationValidationError(errors)


def _clean_update_payload(payload, member):
    unknown = set(payload.keys()) - _UPDATE_FIELDS
    errors = {field: "Unknown field." for field in sorted(unknown)}
    cleaned = {}
    if "required_loan_amount" in payload:
        cleaned["required_loan_amount"] = _optional_positive_decimal(
            payload.get("required_loan_amount"),
            "required_loan_amount",
            errors,
        )
    if "requested_tenure_months" in payload:
        cleaned["requested_tenure_months"] = _optional_positive_int(
            payload.get("requested_tenure_months"),
            "requested_tenure_months",
            errors,
        )
    for field in (
        "declared_purpose",
        "purpose_category",
        "loan_type_requested",
        "borrower_request_notes",
    ):
        if field in payload:
            cleaned[field] = _optional_text(payload.get(field))
    if "terms_acceptance_flag" in payload:
        cleaned["terms_acceptance_flag"] = bool(payload.get("terms_acceptance_flag", False))
    if "land_holding_id" in payload:
        cleaned["land_holding"] = _member_ref(
            LandHolding,
            "land_holding_id",
            payload.get("land_holding_id"),
            "land_holding_id",
            member,
            errors,
        )
    if "crop_plan_id" in payload:
        cleaned["crop_plan"] = _member_ref(
            CropPlan,
            "crop_plan_id",
            payload.get("crop_plan_id"),
            "crop_plan_id",
            member,
            errors,
        )
    if "bank_account_id" in payload:
        cleaned["bank_account"] = _bank_ref(payload.get("bank_account_id"), member, errors)
    if "cancelled_cheque_id" in payload:
        cleaned["cancelled_cheque"] = _member_ref(
            CancelledCheque,
            "cancelled_cheque_id",
            payload.get("cancelled_cheque_id"),
            "cancelled_cheque_id",
            member,
            errors,
        )
    if errors:
        raise LoanApplicationValidationError(errors)
    return cleaned


def _clean_payload(payload, *, require_member):
    unknown = set(payload.keys()) - _CREATE_FIELDS
    errors = {field: "Unknown field." for field in sorted(unknown)}
    member = None
    member_id = payload.get("member_id")
    if require_member or member_id is not None:
        member_uuid = _parse_uuid("member_id", member_id, errors)
        if member_uuid:
            member = Member.objects.filter(member_id=member_uuid, is_deleted=False).first()
            if member is None:
                errors["member_id"] = "Borrower member was not found."

    amount = _optional_positive_decimal(payload.get("required_loan_amount"), "required_loan_amount", errors)
    tenure = _optional_positive_int(payload.get("requested_tenure_months"), "requested_tenure_months", errors)
    cleaned = {
        "member": member,
        "required_loan_amount": amount,
        "requested_tenure_months": tenure,
        "declared_purpose": _optional_text(payload.get("declared_purpose")),
        "purpose_category": _optional_text(payload.get("purpose_category")),
        "loan_type_requested": _optional_text(payload.get("loan_type_requested")),
        "borrower_request_notes": _optional_text(payload.get("borrower_request_notes")),
        "terms_acceptance_flag": bool(payload.get("terms_acceptance_flag", False)),
    }
    if member:
        cleaned["land_holding"] = _member_ref(
            LandHolding,
            "land_holding_id",
            payload.get("land_holding_id"),
            "land_holding_id",
            member,
            errors,
        )
        cleaned["crop_plan"] = _member_ref(
            CropPlan,
            "crop_plan_id",
            payload.get("crop_plan_id"),
            "crop_plan_id",
            member,
            errors,
        )
        cleaned["bank_account"] = _bank_ref(payload.get("bank_account_id"), member, errors)
        cleaned["cancelled_cheque"] = _member_ref(
            CancelledCheque,
            "cancelled_cheque_id",
            payload.get("cancelled_cheque_id"),
            "cancelled_cheque_id",
            member,
            errors,
        )
    if errors:
        raise LoanApplicationValidationError(errors)
    return cleaned


def _assign_fields(application, cleaned):
    for field in (
        "required_loan_amount",
        "requested_tenure_months",
        "declared_purpose",
        "purpose_category",
        "loan_type_requested",
        "land_holding",
        "crop_plan",
        "bank_account",
        "cancelled_cheque",
        "borrower_request_notes",
        "terms_acceptance_flag",
    ):
        setattr(application, field, cleaned[field])


def _audit_application(
    application,
    actor,
    action,
    old_value_json,
    request_ip,
    request_user_agent,
    request_id,
):
    AuditLog.objects.create(
        actor_user=actor,
        action=action,
        entity_type="loan_application",
        entity_id=application.loan_application_id,
        old_value_json=old_value_json,
        new_value_json={
            "loan_application_id": str(application.loan_application_id),
            "member_id": str(application.member_id),
            "application_status": application.application_status,
            "current_stage": application.current_stage,
            "required_loan_amount": _money(application.required_loan_amount),
            "purpose_category": application.purpose_category or None,
            "land_holding_id": str(application.land_holding_id)
            if application.land_holding_id
            else None,
            "crop_plan_id": str(application.crop_plan_id)
            if application.crop_plan_id
            else None,
            "bank_account_id": str(application.bank_account_id)
            if application.bank_account_id
            else None,
            "masked_bank_account_number": _masked_last4(
                application.bank_account.account_number_last4
            )
            if application.bank_account_id
            else None,
            "cancelled_cheque_id": str(application.cancelled_cheque_id)
            if application.cancelled_cheque_id
            else None,
            "request_id": request_id,
        },
        ip_address=request_ip,
        user_agent=request_user_agent,
    )


def _audit_snapshot(application):
    return {
        "loan_application_id": str(application.loan_application_id),
        "member_id": str(application.member_id),
        "application_status": application.application_status,
        "current_stage": application.current_stage,
        "required_loan_amount": _money(application.required_loan_amount),
        "purpose_category": application.purpose_category or None,
        "land_holding_id": str(application.land_holding_id)
        if application.land_holding_id
        else None,
        "crop_plan_id": str(application.crop_plan_id) if application.crop_plan_id else None,
        "bank_account_id": str(application.bank_account_id)
        if application.bank_account_id
        else None,
        "cancelled_cheque_id": str(application.cancelled_cheque_id)
        if application.cancelled_cheque_id
        else None,
    }


def _member_summary(member):
    return {
        "member_id": str(member.member_id),
        "display_name": member.display_name,
        "member_type": member.member_type,
        "folio_number": member.folio_number,
        "membership_status": member.membership_status,
        "kyc_status": member.kyc_status,
    }


def _land_summary(land):
    if land is None:
        return None
    return {
        "land_holding_id": str(land.land_holding_id),
        "survey_number": land.survey_number or None,
        "village": land.village or None,
        "area_acres": _money(land.area_acres),
        "verification_status": land.verification_status,
    }


def _crop_summary(crop):
    if crop is None:
        return None
    return {
        "crop_plan_id": str(crop.crop_plan_id),
        "crop_type": crop.crop_type,
        "season": crop.season or None,
        "planned_area_acres": _money(crop.planned_area_acres),
        "loan_purpose_alignment": crop.loan_purpose_alignment,
        "verification_status": crop.verification_status,
    }


def _bank_summary(bank):
    if bank is None:
        return None
    return {
        "bank_account_id": str(bank.bank_account_id),
        "account_holder_name": bank.account_holder_name,
        "account_number": {
            "masked": _masked_last4(bank.account_number_last4),
            "last4": bank.account_number_last4 or None,
            "can_view_full": False,
        },
        "ifsc": bank.ifsc,
        "bank_name": bank.bank_name or None,
        "branch_name": bank.branch_name or None,
        "verification_status": bank.verification_status,
        "status": bank.status,
    }


def _cheque_summary(cheque):
    if cheque is None:
        return None
    return {
        "cancelled_cheque_id": str(cheque.cancelled_cheque_id),
        "document_id": str(cheque.document_id),
        "account_number": {
            "masked": _masked_last4(cheque.account_number_last4),
            "last4": cheque.account_number_last4 or None,
            "can_view_full": False,
        },
        "ifsc": cheque.ifsc,
        "branch_name": cheque.branch_name or None,
        "verification_status": cheque.verification_status,
        "signature_mismatch_flag": cheque.signature_mismatch_flag,
    }


def _parse_uuid(field, value, errors):
    if value in (None, ""):
        errors[field] = "This field is required."
        return None
    try:
        return uuid.UUID(str(value))
    except (TypeError, ValueError) as exc:
        errors[field] = "Must be a valid UUID."
        return None


def _optional_uuid(field, value, errors):
    if value in (None, ""):
        return None
    try:
        return uuid.UUID(str(value))
    except (TypeError, ValueError):
        errors[field] = "Must be a valid UUID."
        return None


def _member_ref(model, payload_field, value, pk_field, member, errors):
    parsed = _optional_uuid(payload_field, value, errors)
    if parsed is None:
        return None
    instance = model.objects.filter(**{pk_field: parsed, "member": member}).first()
    if instance is None:
        errors[payload_field] = "Referenced record was not found for this member."
    return instance


def _bank_ref(value, member, errors):
    parsed = _optional_uuid("bank_account_id", value, errors)
    if parsed is None:
        return None
    bank = BankAccount.objects.filter(
        bank_account_id=parsed,
        owner_party_type="member",
        owner_party_id=member.member_id,
    ).first()
    if bank is None:
        errors["bank_account_id"] = "Referenced record was not found for this member."
    return bank


def _optional_positive_decimal(value, field, errors):
    if value in (None, ""):
        return None
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        errors[field] = "Must be a valid decimal amount."
        return None
    if parsed <= 0:
        errors[field] = "Requested amount must be greater than zero."
    return parsed


def _optional_positive_int(value, field, errors):
    if value in (None, ""):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        errors[field] = "Must be a positive integer."
        return None
    if parsed <= 0:
        errors[field] = "Must be a positive integer."
    return parsed


def _optional_text(value):
    return value.strip() if isinstance(value, str) else ""


def _masked_last4(last4):
    return f"********{last4}" if last4 else None


def _money(value):
    return f"{value:.2f}" if value is not None else None


def _datetime(value):
    return value.isoformat().replace("+00:00", "Z") if value else None
