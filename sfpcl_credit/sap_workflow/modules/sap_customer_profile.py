"""Public owner for SAP customer request, delivery, completion, and code reads."""

from datetime import timedelta
from dataclasses import dataclass
import hashlib
import uuid

from django.core import signing
from django.db import transaction
from django.utils import timezone

from sfpcl_credit.api import request_ip, request_user_agent
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
from sfpcl_credit.sap_workflow.modules.sap_customer_request import create_request as _create_request
from sfpcl_credit.identity.models import AuditLog, User
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.sap_workflow.adapters import ManualSapAdapter
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


def read_member_code(**kwargs):
    return _read_member_code(**kwargs)


@dataclass(frozen=True)
class SapCustomerCodeDecision:
    customer_code_id: uuid.UUID
    member_id: uuid.UUID
    profile_request_id: uuid.UUID
    loan_application_id: uuid.UUID
    status: str


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
        request_queryset = request_queryset.select_for_update()
    request = (
        request_queryset.filter(member_id=member_id)
        .select_related("assigned_to_user__primary_role")
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
        .only("sap_customer_code_id", "member_id", "status")
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
    )


def _current_completed_code_evidence(request, code):
    completion_actions = ("sap.customer_code_created", "sap.customer_code_reused")
    audits = list(AuditLog.objects.filter(
        entity_type="sap_customer_profile_request",
        entity_id=request.pk,
        action__in=completion_actions,
    ).order_by("created_at", "audit_log_id")[:2])
    send_audits = list(AuditLog.objects.filter(
        entity_type="sap_customer_profile_request",
        entity_id=request.pk,
        action="finance.sap_customer_code.sent",
    ).order_by("created_at", "audit_log_id")[:2])
    workflows = list(WorkflowEvent.objects.filter(
        workflow_name="SAPCustomerCodeCompleted",
        entity_type="sap_customer_profile_request",
        entity_id=request.pk,
        trigger_reason__in=completion_actions,
    ).order_by("created_at", "workflow_event_id")[:2])
    if len(audits) != 1 or len(send_audits) != 1 or len(workflows) != 1:
        return False
    audit, send_audit, workflow = audits[0], send_audits[0], workflows[0]
    evidence = audit.new_value_json or {}
    send_evidence = send_audit.new_value_json or {}
    action = audit.action
    expected_reuse = action == "sap.customer_code_reused"
    return bool(
        request.completed_at
        and request.sent_at
        and request.sent_communication_id
        and request.sent_task_id
        and request.delivery_reference
        and len(request.delivery_checksum_sha256 or "") == 64
        and send_evidence.get("annexure_checksum_sha256")
        == request.delivery_checksum_sha256
        and request.delivery_file_id_snapshot == request.excel_file_id
        and request.delivery_assignee_id_snapshot == request.assigned_to_user_id
        and len(request.completion_input_digest or "") == 64
        and evidence.get("completion_input_digest")
        == request.completion_input_digest
        and request.completion_reused_existing_code is expected_reuse
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


def issue_delivery_capability(*, actor, request_id, request):
    with transaction.atomic():
        actor = _locked_assignee(actor)
        row = _locked_delivery(request_id=request_id, actor=actor)
        _require_delivery_integrity(row)
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
        .select_related("excel_file", "assigned_to_user__primary_role")
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
    is_current_finance_assignee = staticmethod(is_current_finance_assignee)
    issue_delivery_capability = staticmethod(issue_delivery_capability)
    read_delivered_annexure = staticmethod(read_delivered_annexure)


__all__ = [
    "SapCustomerProfileModule",
    "SapCustomerCodeDecision",
    "SapRequestConflict",
    "complete_request",
    "create_request",
    "issue_delivery_capability",
    "is_current_finance_assignee",
    "get_customer_code_for_member",
    "read_delivered_annexure",
    "record_delivery_denial",
    "read_member_code",
    "send_request",
]
