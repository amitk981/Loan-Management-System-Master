"""Public owner for SAP customer request, delivery, completion, and code reads."""

from datetime import timedelta
from dataclasses import dataclass
import hashlib
import json
import uuid

from django.core import signing
from django.db import transaction
from django.db.models import Count, Exists, F, OuterRef, Q, Subquery
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.communications.models import Communication, Notification
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.domain_errors import (
    DomainInvalidStateError,
    DomainObjectAccessDenied,
    DomainPermissionDenied,
)
from sfpcl_credit.sap_workflow.models import SapCustomerCode, SapCustomerProfileRequest
from sfpcl_credit.sap_workflow.modules.annexure_storage import EncryptedAnnexureStorage
from sfpcl_credit.sap_workflow.modules.sap_customer_code import (
    complete_request as _complete_request,
    read_member_code as _read_member_code,
    send_request as _send_request,
)
from sfpcl_credit.sap_workflow.modules.sap_customer_request import (
    create_request as _create_request,
    current_terminal_sanction,
)
from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.approvals.models import ApprovalCase, SanctionDecision
from sfpcl_credit.identity.models import AuditLog, User
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.sap_workflow.adapters import (
    ManualSapAdapter,
    XLSX_MIME_TYPE,
    validate_xlsx_workbook_bytes,
)
from sfpcl_credit.sap_workflow.errors import SapRequestConflict
from sfpcl_credit.workflows.models import WorkflowEvent


_CAPABILITY_SALT = "sfpcl.sap-annexure-delivery.v1"
_CAPABILITY_TTL_SECONDS = 15 * 60
_DELIVERY_ACTION = "sap.annexure_i_downloaded"
_DELIVERY_DENIED_ACTION = "sap.annexure_i_download_denied"
_CAPABILITY_ACTION = "sap.annexure_i_capability_issued"


def create_request(**kwargs):
    return _create_request(**kwargs)


def send_request(*, adapter=None, **kwargs):
    try:
        return _send_request(adapter=adapter or ManualSapAdapter(), **kwargs)
    except ValueError as exc:
        raise SapRequestConflict("The manual SAP delivery could not be accepted.") from exc


def complete_request(**kwargs):
    return _complete_request(**kwargs)


def read_member_code(*, actor, member_id, request):
    with transaction.atomic():
        result = _read_member_code(actor=actor, member_id=member_id, request=request)
        if get_customer_code_for_member(member_id, for_update=True) is None:
            raise DomainInvalidStateError("An active SAP customer code is unavailable.")
        return result


def staff_workspace_row_count(*, actor):
    """Count exact current S36 application identities before pagination."""
    _require_staff_workspace_authority(actor)
    return _staff_workspace_applications(actor=actor).count()


def staff_workspace_rows(*, actor, offset=0, limit=None):
    """Project safe S36 actions through the SAP owner's mutation interface."""
    permissions = set(auth_service.effective_permission_codes(actor))
    _require_staff_workspace_authority(actor)
    assignees = [
        candidate
        for candidate in User.objects.select_related("primary_role")
        .filter(
            status=User.ACTIVE_STATUS,
            primary_role__role_code="senior_manager_finance",
            primary_role__status="active",
        )
        .order_by("full_name", "user_id")
        if "finance.sap_request.complete"
        in auth_service.effective_permission_codes(candidate)
    ]
    candidates = _staff_workspace_applications(actor=actor).select_related("member").prefetch_related(
        "sap_customer_profile_requests"
    )
    if limit is not None:
        candidates = candidates[offset : offset + limit]
    elif offset:
        candidates = candidates[offset:]
    rows = []
    for application in candidates:
        requests = sorted(
            application.sap_customer_profile_requests.all(),
            key=lambda row: (row.created_at, row.pk),
            reverse=True,
        )
        if len(requests) > 1:
            continue
        profile_request = requests[0] if requests else None
        actions = []
        if profile_request is None and assignees:
            actions.append(
                {
                    "action_code": "create_sap_request",
                    "label": "Create SAP request",
                    "enabled": True,
                    "disabled_reason": None,
                    "required_permission": "finance.sap_request.create",
                    "action_url": (
                        f"/api/v1/loan-applications/{application.pk}/"
                        "sap-customer-profile-request/"
                    ),
                    "method": "POST",
                    "fields": [
                        {
                            "name": "assigned_to_user_id",
                            "label": "Senior Manager - Finance",
                            "type": "select",
                            "required": True,
                            "value": None,
                            "options": [
                                {"value": str(user.pk), "label": user.full_name}
                                for user in assignees
                            ],
                        }
                    ],
                    "fixed_payload": {},
                }
            )
        elif (
            profile_request is not None
            and profile_request.request_status == profile_request.STATUS_DRAFT
            and profile_request.requested_by_user_id == actor.pk
            and "finance.sap_request.send" in permissions
        ):
            actions.append(
                {
                    "action_code": "send_sap_request",
                    "label": "Send SAP request",
                    "enabled": True,
                    "disabled_reason": None,
                    "required_permission": "finance.sap_request.send",
                    "action_url": (
                        f"/api/v1/sap-customer-profile-requests/"
                        f"{profile_request.pk}/send/"
                    ),
                    "method": "POST",
                    "fields": [
                        {
                            "name": "remarks",
                            "label": "Delivery remarks",
                            "type": "textarea",
                            "required": True,
                            "value": None,
                        }
                    ],
                    "fixed_payload": {},
                }
            )
        rows.append(
            {
                "workspace_id": str(profile_request.pk if profile_request else application.pk),
                "loan_application_id": str(application.pk),
                "application_reference_number": application.application_reference_number,
                "member": {
                    "member_id": str(application.member_id),
                    "display_name": application.member.display_name,
                },
                "sanctioned_amount": f"{application._terminal_sanctioned_amount:.2f}",
                "request_id": str(profile_request.pk) if profile_request else None,
                "request_status": (
                    profile_request.request_status if profile_request else "not_started"
                ),
                "available_actions": actions,
            }
        )
    return rows


def _require_staff_workspace_authority(actor):
    roles = set(auth_service.effective_role_codes(actor))
    permissions = set(auth_service.effective_permission_codes(actor))
    if (
        not actor.can_authenticate()
        or "credit_manager" not in roles
        or "finance.sap_request.create" not in permissions
    ):
        raise DomainPermissionDenied(
            "Active Credit Manager SAP request authority is required."
        )


def _staff_workspace_applications(*, actor):
    latest_case = ApprovalCase.objects.filter(
        loan_application_id=OuterRef("pk")
    ).order_by("-cycle_number", "-submitted_at", "-approval_case_id")
    current_sanction = SanctionDecision.objects.filter(
        loan_application_id=OuterRef("pk"),
        approval_case_id=OuterRef("_latest_case_id"),
        decision="sanctioned",
        sanctioned_amount__gt=0,
        recorded_at__isnull=False,
    ).order_by("sanction_decision_id")
    request_counts = (
        SapCustomerProfileRequest.objects.filter(loan_application_id=OuterRef("pk"))
        .order_by()
        .values("loan_application_id")
        .annotate(total=Count("pk"))
        .values("total")
    )
    return (
        LoanApplication.objects.annotate(
            _latest_case_id=Subquery(latest_case.values("approval_case_id")[:1]),
            _latest_case_status=Subquery(latest_case.values("current_status")[:1]),
            _has_current_sanction=Exists(current_sanction),
            _terminal_sanctioned_amount=Subquery(
                current_sanction.values("sanctioned_amount")[:1]
            ),
            _sap_request_count=Subquery(request_counts[:1]),
        )
        .filter(
            application_status=LoanApplication.STATUS_APPROVED_BY_SANCTION,
            _latest_case_status=ApprovalCase.STATUS_APPROVED,
            _has_current_sanction=True,
        )
        .filter(
            Q(current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT)
            | Q(created_by_user_id=actor.pk)
            | Q(received_by_user_id=actor.pk)
        )
        .filter(Q(_sap_request_count__isnull=True) | Q(_sap_request_count=1))
        .order_by("-updated_at", "loan_application_id")
    )


def assigned_workspace_row_count(*, actor, without_loan_account=False):
    """Count the database-bounded S37 candidate identities for combined pagination."""
    return _assigned_workspace_requests(
        actor=actor, without_loan_account=without_loan_account
    ).count()


def assigned_workspace_rows(
    *, actor, without_loan_account=False, offset=0, limit=None
):
    """Project only current S37 requests assigned to the governed Finance actor."""
    requests = _assigned_workspace_requests(
        actor=actor, without_loan_account=without_loan_account
    )
    if limit is not None:
        requests = requests[offset : offset + limit]
    elif offset:
        requests = requests[offset:]
    rows = []
    for profile_request in requests:
        if (
            profile_request.request_status == profile_request.STATUS_SENT
            and not _current_send_evidence(profile_request)
        ):
            continue
        actions = []
        if profile_request.request_status == profile_request.STATUS_SENT:
            actions.append(
                {
                    "action_code": "complete_sap_request",
                    "label": "Confirm SAP customer code",
                    "enabled": True,
                    "disabled_reason": None,
                    "required_permission": "finance.sap_request.complete",
                    "action_url": (
                        f"/api/v1/sap-customer-profile-requests/"
                        f"{profile_request.pk}/complete/"
                    ),
                    "method": "POST",
                    "fields": [
                        _workspace_field("sap_customer_code", "SAP customer code", "text"),
                        _workspace_field("sap_vendor_code", "SAP vendor code", "text", required=False),
                        _workspace_field("created_at_sap", "SAP creation date and time", "datetime-local", required=False),
                        _workspace_field("confirmation_document_id", "Confirmation document ID", "text", required=False),
                        _workspace_field("confirmation_notes", "Finance comments", "textarea", required=False),
                    ],
                    "fixed_payload": {},
                }
            )
        rows.append(
            {
                "workspace_id": str(profile_request.pk),
                "loan_application_id": str(profile_request.loan_application_id),
                "application_reference_number": (
                    profile_request.loan_application.application_reference_number
                ),
                "member": {
                    "member_id": str(profile_request.member_id),
                    "display_name": profile_request.member.display_name,
                },
                "sanctioned_amount": f"{profile_request.sanctioned_amount:.2f}",
                "request_id": str(profile_request.pk),
                "request_status": profile_request.request_status,
                "customer_code_masked": (
                    f"******{profile_request.sap_customer_code.sap_customer_code[-4:]}"
                    if profile_request.sap_customer_code_id else None
                ),
                "available_actions": actions,
            }
        )
    return rows


def _assigned_workspace_requests(*, actor, without_loan_account):
    roles = set(auth_service.effective_role_codes(actor))
    permissions = set(auth_service.effective_permission_codes(actor))
    if (
        not actor.can_authenticate()
        or "senior_manager_finance" not in roles
        or "finance.sap_request.complete" not in permissions
    ):
        raise DomainPermissionDenied(
            "Active Senior Manager Finance SAP completion authority is required."
        )
    send_audits = (
        AuditLog.objects.filter(
            entity_type="sap_customer_profile_request",
            entity_id=OuterRef("pk"),
            action="finance.sap_customer_code.sent",
            new_value_json__annexure_checksum_sha256=OuterRef(
                "delivery_checksum_sha256"
            ),
        )
        .order_by()
        .values("entity_id")
        .annotate(total=Count("pk"))
        .values("total")
    )
    send_workflows = (
        WorkflowEvent.objects.filter(
            workflow_name="SAPCustomerCodeSent",
            entity_type="sap_customer_profile_request",
            entity_id=OuterRef("pk"),
            from_state=SapCustomerProfileRequest.STATUS_DRAFT,
            to_state=SapCustomerProfileRequest.STATUS_SENT,
            trigger_reason="finance.sap_customer_code.sent",
        )
        .order_by()
        .values("entity_id")
        .annotate(total=Count("pk"))
        .values("total")
    )
    requests = (
        SapCustomerProfileRequest.objects.select_related(
            "loan_application", "member", "sap_customer_code", "assigned_to_user__primary_role",
            "requested_by_user__primary_role", "excel_file", "sent_communication", "sent_task",
        )
        .annotate(
            _send_audit_count=Subquery(send_audits[:1]),
            _send_workflow_count=Subquery(send_workflows[:1]),
        )
        .filter(
            assigned_to_user=actor,
            request_status=SapCustomerProfileRequest.STATUS_SENT,
            sent_at__isnull=False,
            sent_communication_id__isnull=False,
            sent_task_id__isnull=False,
            delivery_reference__isnull=False,
            delivery_file_id_snapshot=F("excel_file_id"),
            delivery_assignee_id_snapshot=F("assigned_to_user_id"),
            _send_audit_count=1,
            _send_workflow_count=1,
        )
        .order_by("-created_at", "-sap_customer_profile_request_id")
    )
    if without_loan_account:
        requests = requests.filter(loan_application__loan_account__isnull=True)
    return requests


def _workspace_field(name, label, field_type, *, required=True):
    return {
        "name": name,
        "label": label,
        "type": field_type,
        "required": required,
        "value": None,
    }


@dataclass(frozen=True)
class SapCustomerCodeDecision:
    customer_code_id: uuid.UUID
    member_id: uuid.UUID
    profile_request_id: uuid.UUID
    loan_application_id: uuid.UUID
    status: str
    completed_at: object
    customer_code_masked: str


def is_current_finance_assignee(*, application_id, member_id, actor_id):
    """Decide the persisted pre-disbursement Senior Finance object scope."""
    request = (
        SapCustomerProfileRequest.objects.select_for_update()
        .select_related("assigned_to_user__primary_role")
        .filter(loan_application_id=application_id, member_id=member_id)
        .order_by("-created_at", "-sap_customer_profile_request_id")
        .first()
    )
    return bool(
        request
        and request.assigned_to_user_id == actor_id
        and request.assigned_to_user.can_authenticate()
        and request.assigned_to_user.primary_role.status == "active"
        and request.assigned_to_user.primary_role.role_code == "senior_manager_finance"
    )


def get_customer_code_for_member(member_id, *, for_update=False):
    """Return only coherent SAP-owned linkage for trusted downstream modules."""
    request_queryset = SapCustomerProfileRequest.objects
    if for_update:
        request_queryset = request_queryset.select_for_update(of=("self",))
    request = (
        request_queryset.filter(member_id=member_id)
        .select_related(
            "assigned_to_user__primary_role",
            "requested_by_user__primary_role",
            "excel_file",
            "sent_communication",
            "sent_task",
        )
        .order_by("-created_at", "-sap_customer_profile_request_id")
        .first()
    )
    if request is None or request.request_status != request.STATUS_COMPLETED:
        return None
    code_queryset = SapCustomerCode.objects
    if for_update:
        code_queryset = code_queryset.select_for_update()
    code = (
        code_queryset.filter(
            member_id=member_id, status=SapCustomerCode.STATUS_ACTIVE
        )
        .select_related("created_for_loan_application")
        .first()
    )
    if code is None:
        return None
    if request.sap_customer_code_id != code.pk or not _current_completed_code_evidence(request, code):
        return None
    return SapCustomerCodeDecision(
        customer_code_id=code.pk,
        member_id=code.member_id,
        profile_request_id=request.pk,
        loan_application_id=request.loan_application_id,
        status=code.status,
        completed_at=request.completed_at,
        customer_code_masked=f"******{code.sap_customer_code[-4:]}",
    )


def get_account_customer_code(*, application_id, member_id, customer_code_id):
    """Validate an account edge against the one current member completion decision."""
    decision = get_customer_code_for_member(member_id)
    return (
        decision
        if decision is not None
        and decision.customer_code_id == customer_code_id
        and decision.member_id == member_id
        and decision.loan_application_id == application_id
        else None
    )


def filter_current_account_completions(queryset):
    """Apply the one current member-completion decision to account identity queries."""
    latest = SapCustomerProfileRequest.objects.filter(
        member_id=OuterRef("member_id")
    ).order_by("-created_at", "-sap_customer_profile_request_id")
    queryset = queryset.annotate(
        _latest_sap_request_id=Subquery(
            latest.values("sap_customer_profile_request_id")[:1]
        ),
        _latest_sap_status=Subquery(latest.values("request_status")[:1]),
        _latest_sap_application_id=Subquery(latest.values("loan_application_id")[:1]),
        _latest_sap_code_id=Subquery(latest.values("sap_customer_code_id")[:1]),
        _latest_sap_assignee_id=Subquery(latest.values("assigned_to_user_id")[:1]),
        _latest_sap_completion_digest=Subquery(
            latest.values("completion_input_digest")[:1]
        ),
    )
    completion_audits = (
        AuditLog.objects.filter(
            entity_type="sap_customer_profile_request",
            entity_id=OuterRef("_latest_sap_request_id"),
            action__in=("sap.customer_code_created", "sap.customer_code_reused"),
            new_value_json__completion_input_digest=OuterRef(
                "_latest_sap_completion_digest"
            ),
        )
        .order_by()
        .values("entity_id")
        .annotate(total=Count("pk"))
        .values("total")
    )
    completion_workflows = (
        WorkflowEvent.objects.filter(
            entity_type="sap_customer_profile_request",
            entity_id=OuterRef("_latest_sap_request_id"),
            workflow_name="SAPCustomerCodeCompleted",
        )
        .order_by()
        .values("entity_id")
        .annotate(total=Count("pk"))
        .values("total")
    )
    queryset = queryset.annotate(
        _completion_audit_count=Subquery(completion_audits[:1]),
        _completion_workflow_count=Subquery(completion_workflows[:1]),
    )
    return queryset.filter(
        Q(sap_customer_code_id__isnull=True)
        | Q(
            sap_customer_code__status=SapCustomerCode.STATUS_ACTIVE,
            sap_customer_code__member_id=F("member_id"),
            _latest_sap_status=SapCustomerProfileRequest.STATUS_COMPLETED,
            _latest_sap_application_id=F("loan_application_id"),
            _latest_sap_code_id=F("sap_customer_code_id"),
            _completion_audit_count=1,
            _completion_workflow_count=1,
        )
    )


def _current_completed_code_evidence(request, code):
    completion_actions = ("sap.customer_code_created", "sap.customer_code_reused")
    audits = list(AuditLog.objects.filter(
        entity_type="sap_customer_profile_request",
        entity_id=request.pk,
        action__in=completion_actions,
    ).order_by("created_at", "audit_log_id")[:2])
    workflows = list(WorkflowEvent.objects.filter(
        workflow_name="SAPCustomerCodeCompleted",
        entity_type="sap_customer_profile_request",
        entity_id=request.pk,
    ).order_by("created_at", "workflow_event_id")[:2])
    if len(audits) != 1 or len(workflows) != 1:
        return False
    audit, workflow = audits[0], workflows[0]
    evidence = audit.new_value_json or {}
    action = audit.action
    expected_reuse = action == "sap.customer_code_reused"
    return bool(
        _current_send_evidence(request)
        and request.completed_at
        and _audit_body_is_intact(audit)
        and _exact_action_audit(
            audit,
            request=request,
            actor=request.assigned_to_user,
            action=action,
            old_state=request.STATUS_SENT,
            new_state=request.STATUS_COMPLETED,
            outcome="reused" if expected_reuse else "created",
            extra={
                "sap_customer_code_id": str(code.pk),
                "confirmation_document_id": (
                    str(code.confirmation_document_id)
                    if code.confirmation_document_id else None
                ),
                "reuse": expected_reuse,
                "completion_input_digest": request.completion_input_digest,
                "provenance": "manual_sap_confirmation",
            },
        )
        and len(request.completion_input_digest or "") == 64
        and evidence.get("completion_input_digest")
        == request.completion_input_digest
        and request.completion_reused_existing_code is expected_reuse
        and _exact_code_identity(request, code, reused=expected_reuse)
        and request.member_id == code.member_id
        and request.sap_customer_code_id == code.pk
        and request.assigned_to_user.can_authenticate()
        and request.assigned_to_user.primary_role.status == "active"
        and request.assigned_to_user.primary_role.role_code == "senior_manager_finance"
        and audit.actor_user_id == request.assigned_to_user_id
        and evidence.get("sap_customer_profile_request_id") == str(request.pk)
        and evidence.get("loan_application_id") == str(request.loan_application_id)
        and evidence.get("member_id") == str(request.member_id)
        and evidence.get("sap_customer_code_id") == str(code.pk)
        and evidence.get("assigned_to_user_id") == str(request.assigned_to_user_id)
        and evidence.get("request_status") == request.STATUS_COMPLETED
        and evidence.get("reuse") is expected_reuse
        and workflow.from_state == request.STATUS_SENT
        and workflow.to_state == request.STATUS_COMPLETED
        and workflow.triggered_by_user_id == request.assigned_to_user_id
        and workflow.trigger_reason == action
    )


def _current_send_evidence(request):
    audits = list(AuditLog.objects.filter(
        entity_type="sap_customer_profile_request",
        entity_id=request.pk,
        action="finance.sap_customer_code.sent",
    ).order_by("created_at", "audit_log_id")[:2])
    workflows = list(WorkflowEvent.objects.filter(
        workflow_name="SAPCustomerCodeSent",
        entity_type="sap_customer_profile_request",
        entity_id=request.pk,
    ).order_by("created_at", "workflow_event_id")[:2])
    if len(audits) != 1 or len(workflows) != 1:
        return False
    audit, workflow = audits[0], workflows[0]
    evidence = audit.new_value_json or {}
    return bool(
        request.request_status in {request.STATUS_SENT, request.STATUS_COMPLETED}
        and request.sent_at
        and request.sent_communication_id
        and request.sent_task_id
        and request.delivery_reference
        and len(request.delivery_checksum_sha256 or "") == 64
        and evidence.get("annexure_checksum_sha256")
        == request.delivery_checksum_sha256
        and evidence.get("assigned_to_user_id") == str(request.assigned_to_user_id)
        and request.delivery_file_id_snapshot == request.excel_file_id
        and request.delivery_assignee_id_snapshot == request.assigned_to_user_id
        and _audit_body_is_intact(audit)
        and _exact_action_audit(
            audit,
            request=request,
            actor=request.requested_by_user,
            action="finance.sap_customer_code.sent",
            old_state=request.STATUS_DRAFT,
            new_state=request.STATUS_SENT,
            outcome="sent",
            extra={
                "communication_id": str(request.sent_communication_id),
                "task_id": str(request.sent_task_id),
                "excel_file_id": str(request.excel_file_id),
                "annexure_checksum_sha256": request.delivery_checksum_sha256,
                "delivery_reference": request.delivery_reference,
                "provenance": "manual_file_annexure_i",
            },
        )
        and _exact_send_delivery_ledger(request, workflow)
        and _exact_annexure_file(request)
    )


def _exact_code_identity(request, code, *, reused):
    if (
        code.member_id != request.member_id
        or code.created_for_loan_application.member_id != request.member_id
        or not code.sap_customer_code
        or code.sap_customer_code != code.sap_customer_code.strip().upper()
        or code.status != SapCustomerCode.STATUS_ACTIVE
    ):
        return False
    if reused:
        return True
    return bool(
        code.created_for_loan_application_id == request.loan_application_id
        and code.created_by_user_id == request.assigned_to_user_id
    )


def _exact_annexure_file(request):
    document = request.excel_file
    if (
        document.pk != request.delivery_file_id_snapshot
        or not document.file_name.lower().endswith(".xlsx")
        or document.file_extension != ".xlsx"
        or document.mime_type != XLSX_MIME_TYPE
        or document.sensitivity_level != DocumentFile.SENSITIVITY_RESTRICTED
        or document.uploaded_by_user_id != request.requested_by_user_id
        or not document.storage_provider
        or not document.storage_key
        or not document.checksum_sha256
        or not document.file_size_bytes
        or document.file_size_bytes <= 0
    ):
        return False
    try:
        workbook = EncryptedAnnexureStorage().read_verified(document)
        validate_xlsx_workbook_bytes(workbook)
    except (OSError, ValueError):
        return False
    return hashlib.sha256(workbook).hexdigest() == request.delivery_checksum_sha256


def _audit_body_is_intact(audit):
    evidence = audit.new_value_json
    retained = audit.old_value_json
    if not isinstance(evidence, dict) or not isinstance(retained, dict):
        return False
    if set(retained) != {
        "request_status", "evidence_sha256", "request_id", "timestamp"
    }:
        return False
    digest = hashlib.sha256(
        json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return bool(
        retained["evidence_sha256"] == digest
        and retained["request_status"] == evidence.get("old_state")
        and retained["request_id"] == evidence.get("request_id")
        and retained["timestamp"] == evidence.get("timestamp")
    )


def _exact_action_audit(
    audit, *, request, actor, action, old_state, new_state, outcome, extra
):
    evidence = audit.new_value_json or {}
    timestamp = evidence.get("timestamp")
    parsed_timestamp = parse_datetime(timestamp) if isinstance(timestamp, str) else None
    request_id = evidence.get("request_id")
    if (
        parsed_timestamp is None
        or not timezone.is_aware(parsed_timestamp)
        or abs((audit.created_at - parsed_timestamp).total_seconds()) > 2
        or not isinstance(request_id, str)
        or not request_id
    ):
        return False
    expected = {
        "sap_customer_profile_request_id": str(request.pk),
        "loan_application_id": str(request.loan_application_id),
        "member_id": str(request.member_id),
        "sanction_decision_id": str(request.sanction_decision_id_snapshot),
        "sanction_approval_case_id": str(request.sanction_approval_case_id_snapshot),
        "actor_user_id": str(actor.pk),
        "assigned_to_user_id": str(request.assigned_to_user_id),
        "request_status": new_state,
        "outcome": outcome,
        **extra,
        "request_id": request_id,
        "actor_type": "user",
        "actor_role_codes": sorted(auth_service.effective_role_codes(actor)),
        "actor_team_codes": sorted(actor.team_codes()),
        "action": action,
        "entity_type": "sap_customer_profile_request",
        "entity_id": str(request.pk),
        "old_state": old_state,
        "new_state": new_state,
        "ip_address": audit.ip_address,
        "user_agent": audit.user_agent,
        "timestamp": timestamp,
        "reason": "SAP customer profile workflow action accepted.",
    }
    return bool(
        evidence == expected
        and audit.actor_user_id == actor.pk
        and audit.actor_type == "user"
        and audit.action == action
        and audit.entity_type == "sap_customer_profile_request"
        and audit.entity_id == request.pk
    )


def _exact_send_delivery_ledger(request, workflow):
    communications = list(Communication.objects.filter(
        related_entity_type="sap_customer_profile_request",
        related_entity_id=request.pk,
    ).order_by("communication_id")[:2])
    tasks = list(Notification.objects.filter(
        related_entity_type="sap_customer_profile_request",
        related_entity_id=request.pk,
        notification_type="sap_customer_profile_request",
    ).order_by("notification_id")[:2])
    if len(communications) != 1 or len(tasks) != 1:
        return False
    communication, task = communications[0], tasks[0]
    capability_path = (
        f"/api/v1/sap-customer-profile-requests/{request.pk}/"
        "annexure-i-delivery-capability/"
    )
    subject = "SAP customer profile creation request"
    body = "A checksum-verified Annexure-I is ready in the governed SAP workspace."
    return bool(
        request.sent_communication_id == communication.pk
        and request.sent_task_id == task.pk
        and communication.recipient_party_type == "user"
        and communication.recipient_party_id == request.assigned_to_user_id
        and communication.recipient_address == request.assigned_to_user.email
        and communication.channel == Communication.CHANNEL_EMAIL
        and communication.content_template_id is None
        and communication.subject_snapshot == subject
        and communication.body_snapshot == body
        and communication.sent_by_user_id == request.requested_by_user_id
        and communication.sent_at is None
        and communication.delivery_status == "delivered"
        and communication.acknowledgement_status is None
        and communication.external_message_id == request.delivery_reference
        and task.communication_id == communication.pk
        and task.notification_type == "sap_customer_profile_request"
        and task.category == "Finance"
        and task.severity == Notification.SEVERITY_INFO
        and task.title == subject
        and task.message == body
        and task.action_label == "Open SAP delivery"
        and task.action_url == capability_path
        and task.sender_user_id == request.requested_by_user_id
        and task.recipient_user_id == request.assigned_to_user_id
        and task.recipient_role_code == ""
        and task.recipient_team_code == ""
        and workflow.from_state == request.STATUS_DRAFT
        and workflow.to_state == request.STATUS_SENT
        and workflow.triggered_by_user_id == request.requested_by_user_id
        and workflow.trigger_reason == "finance.sap_customer_code.sent"
    )


def issue_delivery_capability(*, actor, request_id, request):
    with transaction.atomic():
        actor = _locked_assignee(actor)
        row = _locked_delivery(request_id=request_id, actor=actor)
        _require_delivery_integrity(row)
        _require_current_public_delivery(row)
        previous_version = row.delivery_capability_version
        row.delivery_capability_version += 1
        row.delivery_capability_expires_at = timezone.now() + timedelta(
            seconds=_CAPABILITY_TTL_SECONDS
        )
        row.delivery_capability_consumed_at = None
        row.save(
            update_fields=[
                "delivery_capability_version",
                "delivery_capability_expires_at",
                "delivery_capability_consumed_at",
            ]
        )
        claims = _capability_claims(row)
        AuditLog.objects.create(
            actor_user=actor,
            actor_type="user",
            action=_CAPABILITY_ACTION,
            entity_type="sap_customer_profile_request",
            entity_id=row.pk,
            old_value_json={"capability_version": previous_version},
            new_value_json=_audit_context(
                actor=actor,
                row=row,
                request=request,
                action=_CAPABILITY_ACTION,
                old_state="unissued" if previous_version == 0 else "replaced",
                new_state="available",
                outcome="issued",
                reason="Frozen assignee requested a one-use Annexure-I capability.",
            ),
            ip_address=request_ip(request),
            user_agent=request_user_agent(request),
        )
        return {
            "delivery_reference": row.delivery_reference,
            "checksum_sha256": row.delivery_checksum_sha256,
            "capability": signing.dumps(claims, salt=_CAPABILITY_SALT, compress=True),
            "expires_at": _iso(row.delivery_capability_expires_at),
        }


def read_delivered_annexure(*, actor, request_id, capability, request, storage=None):
    try:
        claims = signing.loads(
            capability,
            salt=_CAPABILITY_SALT,
            max_age=_CAPABILITY_TTL_SECONDS,
        )
    except (signing.BadSignature, signing.SignatureExpired) as exc:
        raise SapRequestConflict("The SAP delivery capability is invalid or expired.") from exc

    with transaction.atomic():
        actor = _locked_assignee(actor)
        row = _locked_delivery(request_id=request_id, actor=actor)
        _require_delivery_integrity(row)
        _require_current_public_delivery(row)
        if claims != _capability_claims(row):
            raise SapRequestConflict("The SAP delivery capability is invalid or expired.")
        if (
            row.delivery_capability_expires_at is None
            or row.delivery_capability_expires_at <= timezone.now()
            or row.delivery_capability_consumed_at is not None
        ):
            raise SapRequestConflict("The SAP delivery capability is invalid or expired.")

        workbook = EncryptedAnnexureStorage(storage).read_verified(row.excel_file)
        if hashlib.sha256(workbook).hexdigest() != row.delivery_checksum_sha256:
            raise DomainInvalidStateError("The retained SAP Annexure-I delivery is invalid.")
        row.delivery_capability_consumed_at = timezone.now()
        row.save(update_fields=["delivery_capability_consumed_at"])
        AuditLog.objects.create(
            actor_user=actor,
            actor_type="user",
            action=_DELIVERY_ACTION,
            entity_type="sap_customer_profile_request",
            entity_id=row.pk,
            old_value_json={"delivery_state": "available"},
            new_value_json=_audit_context(
                actor=actor,
                row=row,
                request=request,
                action=_DELIVERY_ACTION,
                old_state="available",
                new_state="consumed",
                outcome="downloaded",
                reason="Frozen assignee read checksum-verified Annexure-I.",
            ),
            ip_address=request_ip(request),
            user_agent=request_user_agent(request),
        )
        return workbook, row.excel_file


def record_delivery_denial(*, actor, request_id, request, reason):
    """Record a safe denial after the rejected transaction has rolled back."""
    persisted = (
        User.objects.select_related("primary_role")
        .filter(pk=getattr(actor, "pk", None))
        .first()
    )
    if persisted is None:
        return None
    status = (
        SapCustomerProfileRequest.objects.filter(pk=request_id)
        .values_list("request_status", flat=True)
        .first()
    )
    evidence = {
        "actor_user_id": str(persisted.pk),
        "actor_type": "user",
        "actor_role_codes": sorted(auth_service.effective_role_codes(persisted)),
        "actor_team_codes": sorted(persisted.team_codes()),
        "action": _DELIVERY_DENIED_ACTION,
        "entity_type": "sap_customer_profile_request",
        "entity_id": str(request_id),
        "old_state": status,
        "new_state": status,
        "request_id": request.headers.get("X-Request-ID"),
        "ip_address": request_ip(request),
        "user_agent": request_user_agent(request),
        "timestamp": _iso(timezone.now()),
        "reason": str(reason)[:200],
        "outcome": "denied",
    }
    return AuditLog.objects.create(
        actor_user=persisted,
        actor_type="user",
        action=_DELIVERY_DENIED_ACTION,
        entity_type="sap_customer_profile_request",
        entity_id=request_id,
        old_value_json={"request_status": status},
        new_value_json=evidence,
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )


def _locked_assignee(actor):
    persisted = (
        User.objects.select_for_update()
        .select_related("primary_role")
        .filter(pk=getattr(actor, "pk", None))
        .first()
    )
    permissions = set(auth_service.effective_permission_codes(persisted)) if persisted else set()
    roles = set(auth_service.effective_role_codes(persisted)) if persisted else set()
    if (
        persisted is None
        or not persisted.can_authenticate()
        or "finance.sap_request.complete" not in permissions
        or "senior_manager_finance" not in roles
    ):
        raise DomainPermissionDenied("You do not have SAP delivery read permission.")
    return persisted


def _locked_delivery(*, request_id, actor):
    row = (
        SapCustomerProfileRequest.objects.select_for_update()
        .select_related(
            "excel_file",
            "assigned_to_user__primary_role",
            "requested_by_user__primary_role",
            "sent_communication",
            "sent_task",
        )
        .filter(pk=request_id, assigned_to_user=actor)
        .first()
    )
    if row is None:
        raise DomainObjectAccessDenied(None)
    if row.request_status not in {
        SapCustomerProfileRequest.STATUS_SENT,
        SapCustomerProfileRequest.STATUS_COMPLETED,
    }:
        raise DomainInvalidStateError("The SAP Annexure-I has not been delivered.")
    return row


def _require_current_public_delivery(row):
    if not _current_send_evidence(row):
        raise DomainInvalidStateError("The retained SAP Annexure-I delivery is invalid.")
    if row.request_status != SapCustomerProfileRequest.STATUS_COMPLETED:
        return
    code = (
        SapCustomerCode.objects.select_for_update()
        .select_related("created_for_loan_application")
        .filter(
            pk=row.sap_customer_code_id,
            member_id=row.member_id,
            status=SapCustomerCode.STATUS_ACTIVE,
        )
        .first()
    )
    if code is None or not _current_completed_code_evidence(row, code):
        raise DomainInvalidStateError("The retained SAP Annexure-I delivery is invalid.")


def _require_delivery_integrity(row):
    if (
        not row.delivery_reference
        or len(row.delivery_checksum_sha256) != 64
        or row.delivery_file_id_snapshot != row.excel_file_id
        or row.delivery_assignee_id_snapshot != row.assigned_to_user_id
    ):
        raise DomainInvalidStateError("The retained SAP Annexure-I delivery is invalid.")


def _capability_claims(row):
    return {
        "request_id": str(row.pk),
        "delivery_reference": row.delivery_reference,
        "document_id": str(row.delivery_file_id_snapshot),
        "assignee_user_id": str(row.delivery_assignee_id_snapshot),
        "checksum_sha256": row.delivery_checksum_sha256,
        "version": row.delivery_capability_version,
    }


def _audit_context(*, actor, row, request, action, old_state, new_state, outcome, reason):
    return {
        "actor_user_id": str(actor.pk),
        "actor_type": "user",
        "actor_role_codes": sorted(auth_service.effective_role_codes(actor)),
        "actor_team_codes": sorted(actor.team_codes()),
        "action": action,
        "entity_type": "sap_customer_profile_request",
        "entity_id": str(row.pk),
        "old_state": old_state,
        "new_state": new_state,
        "request_id": request.headers.get("X-Request-ID"),
        "ip_address": request_ip(request),
        "user_agent": request_user_agent(request),
        "timestamp": _iso(timezone.now()),
        "reason": reason,
        "outcome": outcome,
        "delivery_reference": row.delivery_reference,
        "checksum_sha256": row.delivery_checksum_sha256,
    }


def _iso(value):
    return value.isoformat().replace("+00:00", "Z") if value else None


class SapCustomerProfileModule:
    create_request = staticmethod(create_request)
    send_request = staticmethod(send_request)
    complete = staticmethod(complete_request)
    get_customer_code_for_member = staticmethod(get_customer_code_for_member)
    filter_current_account_completions = staticmethod(filter_current_account_completions)
    is_current_finance_assignee = staticmethod(is_current_finance_assignee)
    issue_delivery_capability = staticmethod(issue_delivery_capability)
    read_delivered_annexure = staticmethod(read_delivered_annexure)


__all__ = [
    "SapCustomerProfileModule",
    "SapCustomerCodeDecision",
    "SapRequestConflict",
    "assigned_workspace_row_count",
    "assigned_workspace_rows",
    "complete_request",
    "create_request",
    "filter_current_account_completions",
    "issue_delivery_capability",
    "is_current_finance_assignee",
    "get_customer_code_for_member",
    "read_delivered_annexure",
    "record_delivery_denial",
    "read_member_code",
    "send_request",
    "staff_workspace_row_count",
    "staff_workspace_rows",
]
