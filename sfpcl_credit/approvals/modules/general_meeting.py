"""Immutable application-level general-meeting evidence for related-party cases."""

import uuid
from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.dateparse import parse_date

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.approvals.models import ApprovalCase, GeneralMeetingApproval
from sfpcl_credit.approvals.modules import approval_case_engine
from sfpcl_credit.documents import services as document_services
from sfpcl_credit.domain_errors import (
    DomainInvalidStateError,
    DomainObjectAccessDenied,
    DomainPermissionDenied,
)
from sfpcl_credit.identity.models import AuditLog, User
from sfpcl_credit.workflows.events import record_workflow_event


RECORD_PERMISSION = "approvals.general_meeting.record"
CASE_READ_PERMISSION = "approvals.case.read"
DOCUMENT_READ_PERMISSION = "documents.file.download"


@dataclass(frozen=True)
class GeneralMeetingGateConflict(Exception):
    code: str
    message: str
    details: dict

    def __str__(self):
        return self.message


def record_action_availability(*, case, actor, actor_permissions):
    """Project the §25.11 recorder decision for this exact routed case."""
    permissions = set(actor_permissions)
    case_access = approval_case_engine.can_read_approval_case(
        actor=actor, case=case, actor_permissions=permissions
    )
    legal_audience = (
        case_access.scope_type == "approval_assigned"
        or bool(
            set(actor.role_codes())
            & {"compliance_team_member", "company_secretary", "credit_manager"}
        )
    )
    required = {RECORD_PERMISSION, CASE_READ_PERMISSION, DOCUMENT_READ_PERMISSION}
    enabled = (
        case.general_meeting_evidence_required
        and case_access.allowed
        and legal_audience
        and required.issubset(permissions)
    )
    if not case.general_meeting_evidence_required:
        reason = "General meeting evidence is not required for this approval case."
    elif not case_access.allowed or not legal_audience:
        reason = "The current user is not in the related-party legal audience for this case."
    elif not required.issubset(permissions):
        reason = "Required general meeting record, case read, and document access permissions are not granted."
    else:
        reason = None
    return {
        "action_code": "record_general_meeting_approval",
        "label": "Record General Meeting Approval",
        "enabled": enabled,
        "disabled_reason": reason,
        "required_permission": RECORD_PERMISSION,
    }


def record_for_application(
    *, actor, application_id, payload, actor_permissions, request_meta=None
):
    """Record one immutable §25.11 evidence row through the approval-owned seam."""
    permissions = set(actor_permissions)
    if RECORD_PERMISSION not in permissions:
        raise DomainPermissionDenied(
            "You do not have permission to record general meeting approval evidence."
        )
    if CASE_READ_PERMISSION not in permissions:
        raise DomainObjectAccessDenied(None)
    if DOCUMENT_READ_PERMISSION not in permissions:
        raise DomainPermissionDenied(
            "You do not have permission to access the referenced document files."
        )
    cleaned = _validate_payload(payload)
    request_meta = request_meta or {}

    with transaction.atomic():
        application = LoanApplication.objects.select_for_update().get(pk=application_id)
        case = (
            ApprovalCase.objects.select_for_update()
            .select_related("loan_application", "loan_appraisal_note__risk_assessment")
            .prefetch_related("actions")
            .filter(loan_application=application)
            .order_by("-cycle_number")
            .first()
        )
        case_access = approval_case_engine.can_read_approval_case(
            actor=actor,
            case=case,
            actor_permissions=permissions,
        ) if case is not None else None
        if (
            case is None
            or not approval_case_engine.is_routable_approval_case(case)
            or not case_access.allowed
        ):
            raise DomainObjectAccessDenied(None)
        if not case.general_meeting_evidence_required:
            raise DomainInvalidStateError(
                "General meeting evidence is not required for this approval case."
            )

        related_party_user = None
        if cleaned["related_party_user_id"] is not None:
            related_party_user = User.objects.filter(
                pk=cleaned["related_party_user_id"], status=User.ACTIVE_STATUS
            ).first()
            if related_party_user is None:
                raise ValidationError(
                    {"related_party_user_id": "Active related party user was not found."}
                )
        document_ids = {
            cleaned["notice_document_id"],
            cleaned["minutes_document_id"],
            cleaned["resolution_document_id"],
        }
        if len(document_ids) != 3:
            raise ValidationError(
                {"document_ids": "Notice, minutes, and resolution must be distinct documents."}
            )
        documents = document_services.resolve_referenceable_documents(
            actor_permissions=permissions,
            document_ids_by_field={
                field: cleaned[field]
                for field in (
                    "notice_document_id",
                    "minutes_document_id",
                    "resolution_document_id",
                )
            },
            context=document_services.DocumentReferenceContext(
                related_entity_type="application",
                related_entity_id=application.pk,
                related_entity_access_allowed=case_access.allowed,
                workflow_scope=document_services.GENERAL_MEETING_WORKFLOW_SCOPE,
                actor_role_codes=frozenset(actor.role_codes()),
                actor_is_related_case_approver=(
                    case_access.scope_type == "approval_assigned"
                ),
            ),
            purpose=document_services.GENERAL_MEETING_REFERENCE_PURPOSE,
        )

        latest = (
            GeneralMeetingApproval.objects.filter(
                loan_application=application,
                superseded_by__isnull=True,
            )
            .order_by("-recorded_at", "-general_meeting_approval_id")
            .first()
        )
        if latest is not None and _matches(latest, cleaned):
            return serialize(latest)

        meeting = GeneralMeetingApproval.objects.create(
            loan_application=application,
            related_party_type=cleaned["related_party_type"],
            related_party_user=related_party_user,
            relationship_description=cleaned["relationship_description"],
            meeting_date=cleaned["meeting_date"],
            notice_document=documents["notice_document_id"],
            minutes_document=documents["minutes_document_id"],
            resolution_document=documents["resolution_document_id"],
            approval_status=cleaned["approval_status"],
            recorded_by_user=actor,
            supersedes=latest,
        )
        audit_action = "general_meeting_approval.recorded"
        if latest is not None:
            audit_action = (
                "general_meeting_approval.status_changed"
                if latest.approval_status != meeting.approval_status
                else "general_meeting_approval.superseded"
            )
        AuditLog.objects.create(
            actor_user=actor,
            action=audit_action,
            entity_type="general_meeting_approval",
            entity_id=meeting.pk,
            old_value_json=serialize(latest) if latest is not None else {},
            new_value_json={
                **serialize(meeting),
                "approval_case_id": str(case.pk),
                "cycle_number": case.cycle_number,
                "request_id": request_meta.get("request_id"),
            },
            ip_address=request_meta.get("ip_address", ""),
            user_agent=request_meta.get("user_agent", ""),
        )
        record_workflow_event(
            actor=actor,
            workflow_name="general_meeting_approval",
            entity_type="general_meeting_approval",
            entity_id=meeting.pk,
            from_state=latest.approval_status if latest is not None else None,
            to_state=meeting.approval_status,
            trigger_reason=(
                f"General meeting evidence recorded for approval case {case.pk} "
                f"cycle {case.cycle_number}."
            ),
            action_code=audit_action,
        )
        return serialize(meeting)


def serialize(meeting):
    return {
        "general_meeting_approval_id": str(meeting.pk),
        "loan_application_id": str(meeting.loan_application_id),
        "related_party_type": meeting.related_party_type,
        "related_party_user_id": (
            str(meeting.related_party_user_id)
            if meeting.related_party_user_id
            else None
        ),
        "relationship_description": meeting.relationship_description,
        "meeting_date": meeting.meeting_date.isoformat(),
        "notice_document_id": str(meeting.notice_document_id),
        "minutes_document_id": str(meeting.minutes_document_id),
        "resolution_document_id": str(meeting.resolution_document_id),
        "approval_status": meeting.approval_status,
        "recorded_by_user_id": str(meeting.recorded_by_user_id),
        "recorded_at": meeting.recorded_at.isoformat().replace("+00:00", "Z"),
        "supersedes_general_meeting_approval_id": (
            str(meeting.supersedes_id) if meeting.supersedes_id else None
        ),
    }


def serialize_for_case(case):
    """Project current evidence for an open cycle or its immutable frozen evidence."""
    if not case.general_meeting_evidence_required:
        return None
    if case.current_status == ApprovalCase.STATUS_PENDING:
        meeting = latest_evidence_for_case(case)
        evidence_scope = "current_pending"
    else:
        meeting = case.general_meeting_approval
        evidence_scope = "cycle_frozen"
    if meeting is None:
        return None
    return {**serialize(meeting), "evidence_scope": evidence_scope}


def approved_evidence_for_final_action(case):
    """Return the latest approved application evidence or deny final sanction."""
    if not case.general_meeting_evidence_required:
        return None
    latest = latest_evidence_for_case(case)
    projection = serialize_for_case(case)
    details = {
        "approval_case_id": str(case.pk),
        "cycle_number": case.cycle_number,
        "general_meeting_approval": projection,
    }
    if latest is None:
        raise GeneralMeetingGateConflict(
            code="GENERAL_MEETING_EVIDENCE_REQUIRED",
            message=(
                "Approved general meeting evidence is required before final sanction."
            ),
            details=details,
        )
    if latest.approval_status != GeneralMeetingApproval.STATUS_APPROVED:
        raise GeneralMeetingGateConflict(
            code={
                GeneralMeetingApproval.STATUS_PENDING: "GENERAL_MEETING_APPROVAL_PENDING",
                GeneralMeetingApproval.STATUS_REJECTED: "GENERAL_MEETING_APPROVAL_REJECTED",
            }[latest.approval_status],
            message=(
                "The current general meeting approval must be approved before final sanction."
            ),
            details=details,
        )
    return latest


def latest_evidence_for_case(case):
    """Resolve application history only for a cycle frozen as evidence-required."""
    if not case.general_meeting_evidence_required:
        return None
    return (
        GeneralMeetingApproval.objects.filter(
            loan_application_id=case.loan_application_id,
            superseded_by__isnull=True,
        )
        .order_by("-recorded_at", "-general_meeting_approval_id")
        .first()
    )


def _matches(meeting, cleaned):
    return (
        meeting.related_party_type == cleaned["related_party_type"]
        and meeting.related_party_user_id == cleaned["related_party_user_id"]
        and meeting.relationship_description == cleaned["relationship_description"]
        and meeting.meeting_date == cleaned["meeting_date"]
        and meeting.notice_document_id == cleaned["notice_document_id"]
        and meeting.minutes_document_id == cleaned["minutes_document_id"]
        and meeting.resolution_document_id == cleaned["resolution_document_id"]
        and meeting.approval_status == cleaned["approval_status"]
    )


def _validate_payload(payload):
    if not isinstance(payload, dict):
        raise ValidationError({"non_field_errors": "Request body must be an object."})
    fields = {
        "related_party_type",
        "related_party_user_id",
        "relationship_description",
        "meeting_date",
        "notice_document_id",
        "minutes_document_id",
        "resolution_document_id",
        "approval_status",
    }
    unknown = set(payload) - fields
    errors = {field: "Unknown field." for field in sorted(unknown)}
    related_party_type = payload.get("related_party_type")
    if related_party_type not in {
        choice[0] for choice in GeneralMeetingApproval.RELATED_PARTY_TYPES
    }:
        errors["related_party_type"] = "Unknown related party type."
    approval_status = payload.get("approval_status")
    if approval_status not in {choice[0] for choice in GeneralMeetingApproval.STATUSES}:
        errors["approval_status"] = "Unknown approval status."
    description = payload.get("relationship_description")
    if not isinstance(description, str) or not description.strip():
        errors["relationship_description"] = "This field must not be blank."
    meeting_date = parse_date(str(payload.get("meeting_date") or ""))
    if meeting_date is None:
        errors["meeting_date"] = "Must be a valid ISO date."
    parsed_ids = {}
    for field in (
        "related_party_user_id",
        "notice_document_id",
        "minutes_document_id",
        "resolution_document_id",
    ):
        raw = payload.get(field)
        if field == "related_party_user_id" and raw in (None, ""):
            parsed_ids[field] = None
            continue
        try:
            parsed_ids[field] = uuid.UUID(str(raw))
        except (ValueError, TypeError, AttributeError):
            errors[field] = "Must be a valid UUID."
    if errors:
        raise ValidationError(errors)
    return {
        "related_party_type": related_party_type,
        "related_party_user_id": parsed_ids["related_party_user_id"],
        "relationship_description": description.strip(),
        "meeting_date": meeting_date,
        "notice_document_id": parsed_ids["notice_document_id"],
        "minutes_document_id": parsed_ids["minutes_document_id"],
        "resolution_document_id": parsed_ids["resolution_document_id"],
        "approval_status": approval_status,
    }
