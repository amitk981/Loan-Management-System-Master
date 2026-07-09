import uuid
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from sfpcl_credit.applications.models import (
    ApplicationDeficiency,
    ApplicationDocument,
    LoanApplication,
    LoanRequestRegisterEntry,
    SystemSequence,
)
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.identity.modules.object_permissions import evaluate_object_access
from sfpcl_credit.members.models import BankAccount, CancelledCheque, CropPlan, LandHolding, Member
from sfpcl_credit.workflows.events import record_workflow_event
from sfpcl_credit.workflows.guard import (
    InvalidStateTransition,
    TransitionDefinition,
    evaluate_transition,
)


APPLICATION_READ_PERMISSION = "applications.loan_application.read"
APPLICATION_CREATE_PERMISSION = "applications.loan_application.create"
APPLICATION_UPDATE_PERMISSION = "applications.loan_application.update"
APPLICATION_SUBMIT_PERMISSION = "applications.loan_application.submit"
APPLICATION_COMPLETE_CHECK_PERMISSION = "applications.loan_application.complete_check"
APPLICATION_DOCUMENT_UPLOAD_PERMISSION = "applications.document.upload"
APPLICATION_DOCUMENT_VERIFY_PERMISSION = "applications.document.verify"
LOAN_APPLICATION_REFERENCE_SEQUENCE_CODE = "loan_application_reference"
APPLICATION_DOCUMENT_ATTACH_AUDIT_ACTION = "applications.application_document.attached"
APPLICATION_DOCUMENT_VERIFY_AUDIT_ACTION = "applications.application_document.verified"
APPLICATION_RETURN_DEFICIENCIES_AUDIT_ACTION = (
    "applications.loan_application.returned_with_deficiencies"
)
APPLICATION_DEFICIENCY_RESOLVED_AUDIT_ACTION = "applications.deficiency.resolved"
APPLICATION_DOCUMENT_TYPES = {
    "loan_application_form",
    "borrower_pan",
    "borrower_aadhaar_ovd",
    "nominee_pan",
    "nominee_aadhaar_ovd",
    "share_certificate_copy",
    "land_document_7_12",
    "crop_plan",
    "six_month_bank_statement",
    "cancelled_cheque",
}
REQUIRED_APPLICATION_DOCUMENT_TYPES = (
    "loan_application_form",
    "borrower_pan",
    "borrower_aadhaar_ovd",
    "nominee_pan",
    "nominee_aadhaar_ovd",
    "share_certificate_copy",
    "land_document_7_12",
    "crop_plan",
    "six_month_bank_statement",
)
APPLICATION_DOCUMENT_PARTY_TYPES = ("borrower", "nominee", "witness")
APPLICATION_DOCUMENT_VERIFICATION_STATUSES = ("pending", "verified", "rejected")
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
    TransitionDefinition(
        entity_type="loan_application",
        action_code="generate_reference",
        from_states=frozenset({LoanApplication.STATUS_SUBMITTED}),
        to_state=LoanApplication.STATUS_REFERENCE_GENERATED,
        required_permission=APPLICATION_COMPLETE_CHECK_PERMISSION,
        audit_action="applications.loan_application.reference_generated",
        workflow_name="loan_application",
        workflow_label="Completeness passed and reference generated.",
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


class LoanApplicationInvalidStateError(Exception):
    pass


def user_can_read_applications(user):
    return APPLICATION_READ_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_create_applications(user):
    return APPLICATION_CREATE_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_update_applications(user):
    return APPLICATION_UPDATE_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_submit_applications(user):
    return APPLICATION_SUBMIT_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_complete_check_applications(user):
    return APPLICATION_COMPLETE_CHECK_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_upload_application_documents(user):
    return APPLICATION_DOCUMENT_UPLOAD_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_verify_application_documents(user):
    return APPLICATION_DOCUMENT_VERIFY_PERMISSION in auth_service.effective_permission_codes(user)


def evaluate_application_object_access(application, actor, required_permission, actor_permissions=None):
    permissions = actor_permissions or auth_service.effective_permission_codes(actor)
    allow_global = _has_credit_manager_domain_access(application, actor)
    result = evaluate_object_access(
        actor_user_id=actor.user_id,
        actor_team_codes=actor.team_codes(),
        actor_permission_codes=permissions,
        required_permission=required_permission,
        object_owner_user_id=application.created_by_user_id,
        allow_global=allow_global,
    )
    if result.allowed or result.error_code != "OBJECT_ACCESS_DENIED":
        return result
    if (
        application.received_by_user_id
        and application.received_by_user_id != application.created_by_user_id
    ):
        return evaluate_object_access(
            actor_user_id=actor.user_id,
            actor_team_codes=actor.team_codes(),
            actor_permission_codes=permissions,
            required_permission=required_permission,
            object_owner_user_id=application.received_by_user_id,
            allow_global=allow_global,
        )
    return result


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
            "loan_request_register_entry",
        )
        .filter(loan_application_id=application_id)
        .first()
    )


def get_application_document(application_document_id):
    return (
        ApplicationDocument.objects.select_related(
            "loan_application",
            "loan_application__member",
            "document_file",
            "created_by_user",
            "updated_by_user",
            "verified_by_user",
        )
        .filter(application_document_id=application_document_id)
        .first()
    )


def get_application_deficiency(deficiency_id):
    return (
        ApplicationDeficiency.objects.select_related(
            "loan_application",
            "loan_application__member",
            "loan_application__created_by_user",
            "loan_application__received_by_user",
            "raised_by_user",
            "resolved_by_user",
        )
        .filter(deficiency_id=deficiency_id)
        .first()
    )


def _has_credit_manager_domain_access(application, actor):
    return (
        "credit_manager" in actor.role_codes()
        and application.current_stage == LoanApplication.STAGE_CREDIT_ASSESSMENT
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


@transaction.atomic
def generate_reference_after_completeness_pass(
    application,
    actor,
    request_ip="",
    request_user_agent="",
    request_id=None,
    actor_permissions=None,
):
    application = (
        LoanApplication.objects.select_for_update()
        .select_related("member", "received_by_user")
        .get(loan_application_id=application.loan_application_id)
    )
    transition = evaluate_transition(
        current_state=application.application_status,
        requested_action="generate_reference",
        actor_permissions=actor_permissions or auth_service.effective_permission_codes(actor),
        transitions=APPLICATION_TRANSITIONS,
    )
    if application.application_reference_number:
        raise LoanApplicationValidationError(
            {"application_reference_number": "Application already has a reference number."}
        )
    if LoanRequestRegisterEntry.objects.filter(loan_application=application).exists():
        raise LoanApplicationValidationError(
            {"loan_request_register_entry": "Loan request register entry already exists."}
        )

    old_value_json = _audit_snapshot(application)
    reference_number = _next_loan_application_reference()
    now = timezone.now()
    application.application_reference_number = reference_number
    application.application_status = transition.next_state
    application.current_stage = LoanApplication.STAGE_CREDIT_ASSESSMENT
    application.completeness_status = LoanApplication.COMPLETENESS_COMPLETE
    application.updated_at = now
    application.updated_by_user = actor
    application.save()
    register_entry = LoanRequestRegisterEntry.objects.create(
        loan_application=application,
        application_reference_number=reference_number,
        member=application.member,
        date_received=application.application_date,
        reference_generated_date=timezone.localdate(now),
        received_channel=application.application_channel,
        received_by_user=application.received_by_user,
        register_status=LoanRequestRegisterEntry.STATUS_REFERENCE_GENERATED,
        requested_amount=application.required_loan_amount,
        declared_purpose=application.declared_purpose,
        purpose_category=application.purpose_category,
        borrower_name=application.member.display_name,
        folio_number=application.member.folio_number,
        member_type=application.member.member_type,
        current_stage=application.current_stage,
        current_owner_role="Deputy Manager / Credit Manager",
    )
    _audit_application(
        application,
        actor,
        transition.definition.audit_action,
        old_value_json,
        request_ip,
        request_user_agent,
        request_id,
        register_entry=register_entry,
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
    application.loan_request_register_entry = register_entry
    return application


def list_application_documents(application):
    return (
        ApplicationDocument.objects.select_related(
            "document_file",
            "created_by_user",
            "updated_by_user",
            "verified_by_user",
        )
        .filter(loan_application=application)
        .order_by("document_type", "party_type", "party_id", "version_number")
    )


@transaction.atomic
def attach_application_document(
    application,
    payload,
    actor,
    request_ip="",
    request_user_agent="",
    request_id=None,
):
    if application.application_status == LoanApplication.STATUS_DRAFT:
        raise LoanApplicationValidationError(
            {"application_status": "Documents can be attached only after application submit."}
        )
    cleaned = _clean_application_document_payload(payload)
    latest_version = (
        ApplicationDocument.objects.filter(
            loan_application=application,
            document_type=cleaned["document_type"],
            party_type=cleaned["party_type"],
            party_id=cleaned["party_id"],
        ).aggregate(max_version=Max("version_number"))["max_version"]
        or 0
    )
    now = timezone.now()
    application_document = ApplicationDocument.objects.create(
        loan_application=application,
        document_type=cleaned["document_type"],
        party_type=cleaned["party_type"],
        party_id=cleaned["party_id"],
        document_file=cleaned["document_file"],
        required_flag=cleaned["document_type"] in REQUIRED_APPLICATION_DOCUMENT_TYPES,
        submission_status=ApplicationDocument.SUBMISSION_SUBMITTED,
        verification_status=ApplicationDocument.VERIFICATION_PENDING,
        remarks=cleaned["remarks"],
        version_number=latest_version + 1,
        created_by_user=actor,
        updated_by_user=actor,
        updated_at=now,
    )
    _audit_application_document(
        application_document,
        actor,
        APPLICATION_DOCUMENT_ATTACH_AUDIT_ACTION,
        None,
        request_ip,
        request_user_agent,
        request_id,
    )
    return application_document


@transaction.atomic
def verify_application_document(
    application_document,
    payload,
    actor,
    request_ip="",
    request_user_agent="",
    request_id=None,
):
    if application_document.submission_status != ApplicationDocument.SUBMISSION_SUBMITTED:
        raise LoanApplicationValidationError(
            {"submission_status": "Only submitted document metadata can be verified."}
        )
    status = (payload.get("verification_status") or "").strip().lower()
    errors = {}
    if status not in APPLICATION_DOCUMENT_VERIFICATION_STATUSES:
        errors["verification_status"] = "Must be one of pending, verified, rejected."
    unknown = set(payload.keys()) - {"verification_status", "remarks"}
    errors.update({field: "Unknown field." for field in sorted(unknown)})
    if errors:
        raise LoanApplicationValidationError(errors)

    old_value_json = _application_document_audit_snapshot(application_document)
    now = timezone.now()
    application_document.verification_status = status
    application_document.remarks = _optional_text(payload.get("remarks"))
    application_document.verified_by_user = actor
    application_document.verified_at = now
    application_document.updated_by_user = actor
    application_document.updated_at = now
    application_document.save()
    _audit_application_document(
        application_document,
        actor,
        APPLICATION_DOCUMENT_VERIFY_AUDIT_ACTION,
        old_value_json,
        request_ip,
        request_user_agent,
        request_id,
    )
    return application_document


def build_document_checklist(application):
    latest_by_type = {}
    documents = list_application_documents(application)
    for application_document in documents:
        current = latest_by_type.get(application_document.document_type)
        if current is None or application_document.version_number > current.version_number:
            latest_by_type[application_document.document_type] = application_document

    items = []
    for document_type in REQUIRED_APPLICATION_DOCUMENT_TYPES:
        latest = latest_by_type.get(document_type)
        if latest is None:
            items.append(
                {
                    "document_type": document_type,
                    "required_flag": True,
                    "submission_status": ApplicationDocument.SUBMISSION_PENDING,
                    "verification_status": ApplicationDocument.VERIFICATION_PENDING,
                    "latest_application_document_id": None,
                    "latest_version_number": None,
                }
            )
            continue
        items.append(
            {
                "document_type": document_type,
                "required_flag": True,
                "submission_status": latest.submission_status,
                "verification_status": latest.verification_status,
                "latest_application_document_id": str(latest.application_document_id),
                "latest_version_number": latest.version_number,
            }
        )
    return {
        "loan_application_id": str(application.loan_application_id),
        "items": items,
    }


def build_completeness_workbench(application):
    checklist = build_document_checklist(application)
    required_items = [_completeness_checklist_item(item) for item in checklist["items"]]
    blocking_document_types = [
        item["document_type"] for item in required_items if not item["complete"]
    ]
    return {
        "loan_application_id": str(application.loan_application_id),
        "application_reference_number": application.application_reference_number,
        "application_status": application.application_status,
        "current_stage": application.current_stage,
        "completeness_status": application.completeness_status,
        "member": _member_summary(application.member),
        "required_checklist_items": required_items,
        "blocking_document_types": blocking_document_types,
        "can_generate_reference": (
            application.application_status == LoanApplication.STATUS_SUBMITTED
            and not application.application_reference_number
            and not LoanRequestRegisterEntry.objects.filter(loan_application=application).exists()
            and not blocking_document_types
        ),
    }


def validate_completeness_ready_for_reference(application):
    workbench = build_completeness_workbench(application)
    if workbench["blocking_document_types"]:
        raise LoanApplicationValidationError(
            {
                "required_checklist_items": [
                    {
                        "document_type": item["document_type"],
                        "reason_code": item["reason_code"],
                        "submission_status": item["submission_status"],
                        "verification_status": item["verification_status"],
                    }
                    for item in workbench["required_checklist_items"]
                    if not item["complete"]
                ]
            }
        )
    return workbench


def completeness_pass_invalid_state_message(application):
    if application.application_status != LoanApplication.STATUS_SUBMITTED:
        return (
            "Invalid state transition for loan_application: "
            f"generate_reference is not allowed from {application.application_status}."
        )
    if application.application_reference_number:
        return "Application already has a reference number."
    if LoanRequestRegisterEntry.objects.filter(loan_application=application).exists():
        return "Loan request register entry already exists."
    return None


def return_deficiencies_invalid_state_message(application):
    if application.application_status != LoanApplication.STATUS_SUBMITTED:
        return (
            "Invalid state transition for loan_application: "
            f"return_with_deficiencies is not allowed from {application.application_status}."
        )
    if application.application_reference_number:
        return "Application already has a reference number."
    if LoanRequestRegisterEntry.objects.filter(loan_application=application).exists():
        return "Loan request register entry already exists."
    return None


def list_application_deficiencies(application):
    return (
        ApplicationDeficiency.objects.select_related("raised_by_user", "resolved_by_user")
        .filter(loan_application=application)
        .order_by("item_code", "raised_at", "deficiency_id")
    )


@transaction.atomic
def return_application_with_deficiencies(
    application,
    payload,
    actor,
    request_ip="",
    request_user_agent="",
    request_id=None,
):
    application = (
        LoanApplication.objects.select_for_update()
        .select_related("member", "received_by_user")
        .get(loan_application_id=application.loan_application_id)
    )
    invalid_state_message = return_deficiencies_invalid_state_message(application)
    if invalid_state_message:
        raise LoanApplicationInvalidStateError(invalid_state_message)
    cleaned = _clean_return_deficiencies_payload(application, payload)
    old_value_json = _audit_snapshot(application)
    now = timezone.now()
    application.application_status = LoanApplication.STATUS_INCOMPLETE_RETURNED
    application.completeness_status = LoanApplication.COMPLETENESS_INCOMPLETE
    application.current_stage = LoanApplication.STAGE_INITIAL
    application.updated_at = now
    application.updated_by_user = actor
    application.save()
    deficiencies = []
    for item in cleaned["items"]:
        deficiencies.append(
            ApplicationDeficiency.objects.create(
                loan_application=application,
                item_code=item["item_code"],
                deficiency_type=item["deficiency_type"],
                source_reason_code=item["source_reason_code"],
                description=item["description"],
                remarks=item["remarks"],
                resolution_status=ApplicationDeficiency.STATUS_OPEN,
                raised_by_user=actor,
                raised_at=now,
                communication_mode=cleaned["communication_mode"],
                message=cleaned["message"],
            )
        )
    _audit_returned_with_deficiencies(
        application,
        deficiencies,
        actor,
        old_value_json,
        request_ip,
        request_user_agent,
        request_id,
        cleaned["communication_mode"],
        cleaned["message"],
    )
    record_workflow_event(
        actor=actor,
        workflow_name="loan_application",
        entity_type="loan_application",
        entity_id=application.loan_application_id,
        from_state=LoanApplication.STATUS_SUBMITTED,
        to_state=LoanApplication.STATUS_INCOMPLETE_RETURNED,
        trigger_reason="Application returned with completeness deficiencies.",
        action_code="return_with_deficiencies",
    )
    return {
        "application": application,
        "items": sorted(deficiencies, key=lambda item: (item.item_code, item.raised_at)),
        "communication_mode": cleaned["communication_mode"],
        "message": cleaned["message"],
    }


@transaction.atomic
def resolve_application_deficiency(
    deficiency,
    payload,
    actor,
    request_ip="",
    request_user_agent="",
    request_id=None,
):
    unknown = set(payload.keys()) - {"resolution_notes"}
    errors = {field: "Unknown field." for field in sorted(unknown)}
    resolution_notes = _optional_text(payload.get("resolution_notes"))
    if not resolution_notes:
        errors["resolution_notes"] = "This field is required."
    if deficiency.resolution_status != ApplicationDeficiency.STATUS_OPEN:
        errors["resolution_status"] = "Only open deficiencies can be resolved."
    if errors:
        raise LoanApplicationValidationError(errors)

    old_value_json = _application_deficiency_audit_snapshot(deficiency)
    now = timezone.now()
    deficiency.resolution_status = ApplicationDeficiency.STATUS_RESOLVED
    deficiency.resolution_notes = resolution_notes
    deficiency.resolved_by_user = actor
    deficiency.resolved_at = now
    deficiency.updated_at = now
    deficiency.save()
    _audit_application_deficiency(
        deficiency,
        actor,
        APPLICATION_DEFICIENCY_RESOLVED_AUDIT_ACTION,
        old_value_json,
        request_ip,
        request_user_agent,
        request_id,
    )
    record_workflow_event(
        actor=actor,
        workflow_name="loan_application",
        entity_type="application_deficiency",
        entity_id=deficiency.deficiency_id,
        from_state=ApplicationDeficiency.STATUS_OPEN,
        to_state=ApplicationDeficiency.STATUS_RESOLVED,
        trigger_reason="Deficiency resolved.",
        action_code="resolve_deficiency",
    )
    return deficiency


def serialize_application(application):
    register_entry = getattr(application, "loan_request_register_entry", None)
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
        "loan_request_register_entry": _register_summary(register_entry),
    }


def _completeness_checklist_item(item):
    complete = (
        item["submission_status"] == ApplicationDocument.SUBMISSION_SUBMITTED
        and item["verification_status"] == ApplicationDocument.VERIFICATION_VERIFIED
    )
    reason_code = None
    if item["latest_application_document_id"] is None:
        reason_code = "missing_metadata"
    elif not complete:
        reason_code = "not_verified"
    return {
        **item,
        "complete": complete,
        "reason_code": reason_code,
    }


def serialize_application_document(application_document):
    return {
        "application_document_id": str(application_document.application_document_id),
        "loan_application_id": str(application_document.loan_application_id),
        "document_type": application_document.document_type,
        "party_type": application_document.party_type,
        "party_id": str(application_document.party_id)
        if application_document.party_id
        else None,
        "document_file": _document_file_summary(application_document.document_file),
        "required_flag": application_document.required_flag,
        "submission_status": application_document.submission_status,
        "verification_status": application_document.verification_status,
        "verified_by_user_id": str(application_document.verified_by_user_id)
        if application_document.verified_by_user_id
        else None,
        "verified_at": _datetime(application_document.verified_at),
        "remarks": application_document.remarks,
        "version_number": application_document.version_number,
        "created_at": _datetime(application_document.created_at),
        "created_by_user_id": str(application_document.created_by_user_id),
        "updated_at": _datetime(application_document.updated_at),
        "updated_by_user_id": str(application_document.updated_by_user_id)
        if application_document.updated_by_user_id
        else None,
    }


def serialize_application_deficiency(deficiency):
    return {
        "deficiency_id": str(deficiency.deficiency_id),
        "loan_application_id": str(deficiency.loan_application_id),
        "item_code": deficiency.item_code,
        "deficiency_type": deficiency.deficiency_type,
        "source_reason_code": deficiency.source_reason_code,
        "description": deficiency.description,
        "remarks": deficiency.remarks,
        "resolution_status": deficiency.resolution_status,
        "raised_by_user_id": str(deficiency.raised_by_user_id),
        "raised_at": _datetime(deficiency.raised_at),
        "resolved_by_user_id": str(deficiency.resolved_by_user_id)
        if deficiency.resolved_by_user_id
        else None,
        "resolved_at": _datetime(deficiency.resolved_at),
        "resolution_notes": deficiency.resolution_notes,
    }


def serialize_returned_deficiencies(result):
    application = result["application"]
    return {
        "loan_application_id": str(application.loan_application_id),
        "application_reference_number": application.application_reference_number,
        "application_status": application.application_status,
        "current_stage": application.current_stage,
        "completeness_status": application.completeness_status,
        "communication_mode": result["communication_mode"],
        "message": result["message"],
        "items": [serialize_application_deficiency(item) for item in result["items"]],
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


def _clean_application_document_payload(payload):
    unknown = set(payload.keys()) - {
        "document_type",
        "party_type",
        "party_id",
        "document_file_id",
        "remarks",
    }
    errors = {field: "Unknown field." for field in sorted(unknown)}
    document_type = (payload.get("document_type") or "").strip().lower()
    party_type = (payload.get("party_type") or "").strip().lower()
    document_file_id = _parse_uuid("document_file_id", payload.get("document_file_id"), errors)
    party_id = _optional_uuid("party_id", payload.get("party_id"), errors)

    if not document_type:
        errors["document_type"] = "This field is required."
    elif document_type not in APPLICATION_DOCUMENT_TYPES:
        errors["document_type"] = "Unsupported application document type."
    if not party_type:
        errors["party_type"] = "This field is required."
    elif party_type not in APPLICATION_DOCUMENT_PARTY_TYPES:
        errors["party_type"] = "Must be one of borrower, nominee, witness."

    document_file = None
    if document_file_id:
        document_file = DocumentFile.objects.filter(document_id=document_file_id).first()
        if document_file is None:
            errors["document_file_id"] = "Document file was not found."

    if errors:
        raise LoanApplicationValidationError(errors)
    return {
        "document_type": document_type,
        "party_type": party_type,
        "party_id": party_id,
        "document_file": document_file,
        "remarks": _optional_text(payload.get("remarks")),
    }


def _clean_return_deficiencies_payload(application, payload):
    unknown = set(payload.keys()) - {"communication_mode", "message", "items"}
    errors = {field: "Unknown field." for field in sorted(unknown)}
    communication_mode = _optional_text(payload.get("communication_mode"))
    message = _optional_text(payload.get("message"))
    raw_items = payload.get("items")
    if not communication_mode:
        errors["communication_mode"] = "This field is required."
    if not message:
        errors["message"] = "This field is required."
    if not isinstance(raw_items, list) or not raw_items:
        errors["items"] = "At least one deficiency item is required."
        raw_items = []

    blocking_items = {
        item["document_type"]: item
        for item in build_completeness_workbench(application)["required_checklist_items"]
        if not item["complete"]
    }
    cleaned_items = []
    seen = set()
    item_errors = []
    for index, raw_item in enumerate(raw_items):
        if not isinstance(raw_item, dict):
            item_errors.append({"index": index, "error": "Each deficiency item must be an object."})
            continue
        unknown_item_fields = set(raw_item.keys()) - {"item_code", "remarks"}
        item_code = _optional_text(raw_item.get("item_code")).lower()
        if not item_code:
            item_errors.append({"index": index, "item_code": "This field is required."})
            continue
        if unknown_item_fields:
            item_errors.append(
                {
                    "index": index,
                    "unknown_fields": sorted(unknown_item_fields),
                }
            )
            continue
        if item_code in seen:
            item_errors.append({"index": index, "item_code": "Duplicate deficiency item."})
            continue
        source_item = blocking_items.get(item_code)
        if source_item is None:
            item_errors.append(
                {
                    "index": index,
                    "item_code": "Must match a current blocking completeness checklist item.",
                }
            )
            continue
        seen.add(item_code)
        cleaned_items.append(
            {
                "item_code": item_code,
                "deficiency_type": _deficiency_type_for_source_reason(
                    source_item["reason_code"]
                ),
                "source_reason_code": source_item["reason_code"],
                "description": _deficiency_description(source_item),
                "remarks": _optional_text(raw_item.get("remarks")),
            }
        )
    if item_errors:
        errors["items"] = item_errors
    if errors:
        raise LoanApplicationValidationError(errors)
    return {
        "communication_mode": communication_mode,
        "message": message,
        "items": cleaned_items,
    }


def _deficiency_type_for_source_reason(reason_code):
    if reason_code == "missing_metadata":
        return ApplicationDeficiency.TYPE_MISSING_DOCUMENT
    return ApplicationDeficiency.TYPE_NOT_VERIFIED


def _deficiency_description(source_item):
    document_label = source_item["document_type"].replace("_", " ")
    if source_item["reason_code"] == "missing_metadata":
        return f"{document_label} is missing."
    return f"{document_label} is submitted but not verified."


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
    register_entry=None,
):
    new_value_json = {
        "loan_application_id": str(application.loan_application_id),
        "member_id": str(application.member_id),
        "application_reference_number": application.application_reference_number,
        "application_status": application.application_status,
        "current_stage": application.current_stage,
        "completeness_status": application.completeness_status,
        "required_loan_amount": _money(application.required_loan_amount),
        "purpose_category": application.purpose_category or None,
        "land_holding_id": str(application.land_holding_id)
        if application.land_holding_id
        else None,
        "crop_plan_id": str(application.crop_plan_id) if application.crop_plan_id else None,
        "bank_account_id": str(application.bank_account_id)
        if application.bank_account_id
        else None,
        "masked_bank_account_number": _masked_last4(application.bank_account.account_number_last4)
        if application.bank_account_id
        else None,
        "cancelled_cheque_id": str(application.cancelled_cheque_id)
        if application.cancelled_cheque_id
        else None,
        "request_id": request_id,
    }
    if register_entry is not None:
        new_value_json["loan_request_register_entry_id"] = str(
            register_entry.loan_request_register_entry_id
        )
    AuditLog.objects.create(
        actor_user=actor,
        action=action,
        entity_type="loan_application",
        entity_id=application.loan_application_id,
        old_value_json=old_value_json,
        new_value_json=new_value_json,
        ip_address=request_ip,
        user_agent=request_user_agent,
    )


def _audit_application_document(
    application_document,
    actor,
    action,
    old_value_json,
    request_ip,
    request_user_agent,
    request_id,
):
    new_value_json = _application_document_audit_snapshot(application_document)
    new_value_json["request_id"] = request_id
    AuditLog.objects.create(
        actor_user=actor,
        action=action,
        entity_type="application_document",
        entity_id=application_document.application_document_id,
        old_value_json=old_value_json,
        new_value_json=new_value_json,
        ip_address=request_ip,
        user_agent=request_user_agent,
    )


def _audit_returned_with_deficiencies(
    application,
    deficiencies,
    actor,
    old_value_json,
    request_ip,
    request_user_agent,
    request_id,
    communication_mode,
    message,
):
    new_value_json = _audit_snapshot(application)
    new_value_json.update(
        {
            "deficiency_ids": [str(item.deficiency_id) for item in deficiencies],
            "deficiency_item_codes": [item.item_code for item in deficiencies],
            "communication_mode": communication_mode,
            "message": message,
            "request_id": request_id,
        }
    )
    AuditLog.objects.create(
        actor_user=actor,
        action=APPLICATION_RETURN_DEFICIENCIES_AUDIT_ACTION,
        entity_type="loan_application",
        entity_id=application.loan_application_id,
        old_value_json=old_value_json,
        new_value_json=new_value_json,
        ip_address=request_ip,
        user_agent=request_user_agent,
    )


def _audit_application_deficiency(
    deficiency,
    actor,
    action,
    old_value_json,
    request_ip,
    request_user_agent,
    request_id,
):
    new_value_json = _application_deficiency_audit_snapshot(deficiency)
    new_value_json["request_id"] = request_id
    AuditLog.objects.create(
        actor_user=actor,
        action=action,
        entity_type="application_deficiency",
        entity_id=deficiency.deficiency_id,
        old_value_json=old_value_json,
        new_value_json=new_value_json,
        ip_address=request_ip,
        user_agent=request_user_agent,
    )


def _audit_snapshot(application):
    return {
        "loan_application_id": str(application.loan_application_id),
        "member_id": str(application.member_id),
        "application_reference_number": application.application_reference_number,
        "application_status": application.application_status,
        "current_stage": application.current_stage,
        "completeness_status": application.completeness_status,
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


def _application_document_audit_snapshot(application_document):
    return {
        "application_document_id": str(application_document.application_document_id),
        "loan_application_id": str(application_document.loan_application_id),
        "document_type": application_document.document_type,
        "party_type": application_document.party_type,
        "party_id": str(application_document.party_id)
        if application_document.party_id
        else None,
        "document_file_id": str(application_document.document_file_id),
        "required_flag": application_document.required_flag,
        "submission_status": application_document.submission_status,
        "verification_status": application_document.verification_status,
        "verified_by_user_id": str(application_document.verified_by_user_id)
        if application_document.verified_by_user_id
        else None,
        "verified_at": _datetime(application_document.verified_at),
        "remarks": application_document.remarks,
        "version_number": application_document.version_number,
    }


def _application_deficiency_audit_snapshot(deficiency):
    return {
        "deficiency_id": str(deficiency.deficiency_id),
        "loan_application_id": str(deficiency.loan_application_id),
        "item_code": deficiency.item_code,
        "deficiency_type": deficiency.deficiency_type,
        "source_reason_code": deficiency.source_reason_code,
        "description": deficiency.description,
        "remarks": deficiency.remarks,
        "resolution_status": deficiency.resolution_status,
        "raised_by_user_id": str(deficiency.raised_by_user_id),
        "raised_at": _datetime(deficiency.raised_at),
        "resolved_by_user_id": str(deficiency.resolved_by_user_id)
        if deficiency.resolved_by_user_id
        else None,
        "resolved_at": _datetime(deficiency.resolved_at),
        "resolution_notes": deficiency.resolution_notes,
    }


def _next_loan_application_reference():
    sequence, _created = SystemSequence.objects.select_for_update().get_or_create(
        sequence_code=LOAN_APPLICATION_REFERENCE_SEQUENCE_CODE,
        defaults={
            "prefix": "LO",
            "current_value": 0,
            "padding_length": 8,
        },
    )
    return sequence.next_value()


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


def _register_summary(register_entry):
    if register_entry is None:
        return None
    return {
        "loan_request_register_entry_id": str(
            register_entry.loan_request_register_entry_id
        ),
        "loan_application_id": str(register_entry.loan_application_id),
        "application_reference_number": register_entry.application_reference_number,
        "member_id": str(register_entry.member_id),
        "date_received": register_entry.date_received.isoformat(),
        "reference_generated_date": register_entry.reference_generated_date.isoformat(),
        "received_channel": register_entry.received_channel,
        "register_status": register_entry.register_status,
        "borrower_name": register_entry.borrower_name or None,
        "folio_number": register_entry.folio_number or None,
        "member_type": register_entry.member_type or None,
        "requested_amount": _money(register_entry.requested_amount),
        "purpose_category": register_entry.purpose_category or None,
        "current_stage": register_entry.current_stage or None,
        "current_owner_role": register_entry.current_owner_role or None,
        "eligibility_status": register_entry.eligibility_status,
        "sanction_status": register_entry.sanction_status,
        "documentation_status": register_entry.documentation_status,
        "disbursement_status": register_entry.disbursement_status,
        "created_at": _datetime(register_entry.created_at),
    }


def _document_file_summary(document):
    return {
        "document_id": str(document.document_id),
        "file_name": document.file_name,
        "mime_type": document.mime_type,
        "file_size_bytes": document.file_size_bytes,
        "sensitivity_level": document.sensitivity_level,
        "uploaded_at": _datetime(document.uploaded_at),
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
