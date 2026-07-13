"""Case-owned Exception Register creation, outcome projection, and reads."""

from math import ceil

from django.core.exceptions import ValidationError

from sfpcl_credit.approvals.models import ApprovalCase, ExceptionRegisterEntry
from sfpcl_credit.approvals.modules import approval_case_engine
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.workflows.events import record_workflow_event


CREATE_PERMISSION = "approvals.exception.create"
READ_PERMISSION = "approvals.exception_register.read"
EXCEEDS_DESCRIPTION = (
    "Recommended loan amount exceeds the frozen permissible loan limit."
)
DESCRIPTIONS = {
    ExceptionRegisterEntry.TYPE_EXCEEDS_LOAN_LIMIT: EXCEEDS_DESCRIPTION,
    ExceptionRegisterEntry.TYPE_STAGE_BYPASS: "A governed approval stage was bypassed.",
    ExceptionRegisterEntry.TYPE_WAIVER: "A governed policy requirement was waived.",
}
_LIST_PARAMS = {"page", "page_size", "status", "exception_type"}


def create_for_case(
    *, actor, case, exception_type, business_reason, risk_assessment=None,
    actor_permissions, request_meta=None
):
    """Create the immutable case/cycle register identity inside enrichment."""
    if CREATE_PERMISSION not in actor_permissions:
        from sfpcl_credit.domain_errors import DomainPermissionDenied

        raise DomainPermissionDenied(
            "You do not have permission to create an exception entry."
        )
    exception_type = validate_exception_type(exception_type)
    reason = _required_text("business_reason", business_reason)
    entry, created = ExceptionRegisterEntry.objects.get_or_create(
        approval_case=case,
        defaults={
            "loan_application": case.loan_application,
            "exception_type": exception_type,
            "description": DESCRIPTIONS[exception_type],
            "business_reason": reason,
            "risk_assessment": (risk_assessment or "").strip() or None,
            "closed_at": case.closed_at,
        },
    )
    if not created:
        if (
            entry.exception_type != exception_type
            or entry.business_reason != reason
            or entry.risk_assessment != ((risk_assessment or "").strip() or None)
            or entry.loan_application_id != case.loan_application_id
        ):
            from sfpcl_credit.domain_errors import DomainInvalidStateError

            raise DomainInvalidStateError(
                "The approval case already has a different immutable exception entry."
            )
        return entry
    request_meta = request_meta or {}
    AuditLog.objects.create(
        actor_user=actor,
        action="exception_register.created",
        entity_type="exception_register_entry",
        entity_id=entry.pk,
        old_value_json={},
        new_value_json={
            "approval_case_id": str(case.pk),
            "cycle_number": case.cycle_number,
            "loan_application_id": str(case.loan_application_id),
            "exception_type": entry.exception_type,
            "status": entry.status,
            "request_id": request_meta.get("request_id"),
        },
        ip_address=request_meta.get("ip_address", ""),
        user_agent=request_meta.get("user_agent", ""),
    )
    record_workflow_event(
        actor=actor,
        workflow_name="exception_register",
        entity_type="exception_register_entry",
        entity_id=entry.pk,
        from_state=None,
        to_state=entry.status,
        trigger_reason=(
            f"Exception entry created for approval case {case.pk} cycle "
            f"{case.cycle_number}."
        ),
        action_code="exception_register.created",
    )
    return entry


def project_case_outcome(*, actor, case, request_meta=None):
    """Project only the source §15.7 outcomes from the locked canonical case."""
    try:
        entry = case.exception_register_entry
    except ExceptionRegisterEntry.DoesNotExist:
        return None
    target_status = {
        ApprovalCase.STATUS_APPROVED: ExceptionRegisterEntry.STATUS_APPROVED,
        ApprovalCase.STATUS_REJECTED: ExceptionRegisterEntry.STATUS_REJECTED,
    }.get(case.current_status, ExceptionRegisterEntry.STATUS_PENDING)
    target_closed_at = case.closed_at
    if entry.status == target_status and entry.closed_at == target_closed_at:
        return entry
    previous_status = entry.status
    previous_closed_at = entry.closed_at
    entry.status = target_status
    entry.closed_at = target_closed_at
    entry.save(update_fields=["status", "closed_at"])
    request_meta = request_meta or {}
    AuditLog.objects.create(
        actor_user=actor,
        action="exception_register.status_changed",
        entity_type="exception_register_entry",
        entity_id=entry.pk,
        old_value_json={
            "status": previous_status,
            "closed_at": previous_closed_at.isoformat() if previous_closed_at else None,
        },
        new_value_json={
            "approval_case_id": str(case.pk),
            "cycle_number": case.cycle_number,
            "case_status": case.current_status,
            "status": entry.status,
            "closed_at": entry.closed_at.isoformat() if entry.closed_at else None,
            "request_id": request_meta.get("request_id"),
        },
        ip_address=request_meta.get("ip_address", ""),
        user_agent=request_meta.get("user_agent", ""),
    )
    record_workflow_event(
        actor=actor,
        workflow_name="exception_register",
        entity_type="exception_register_entry",
        entity_id=entry.pk,
        from_state=previous_status,
        to_state=entry.status,
        trigger_reason=(
            f"Approval case {case.pk} cycle {case.cycle_number} reached "
            f"{case.current_status}."
        ),
        action_code="exception_register.status_changed",
    )
    return entry


def validate_exception_type(value):
    valid = {choice[0] for choice in ExceptionRegisterEntry.EXCEPTION_TYPES}
    if value not in valid:
        raise ValidationError({"exception_type": "Unknown exception type."})
    return value


def list_entries(*, actor, query_params, actor_permissions):
    """Return a generated register after the canonical SQL object-scope selector."""
    unknown = set(query_params.keys()) - _LIST_PARAMS
    if unknown:
        raise ValidationError(
            {field: "Unknown query parameter." for field in sorted(unknown)}
        )
    page = _positive_int("page", query_params.get("page"), 1)
    page_size = min(_positive_int("page_size", query_params.get("page_size"), 20), 100)
    status = query_params.get("status")
    if status and status not in {choice[0] for choice in ExceptionRegisterEntry.STATUSES}:
        raise ValidationError({"status": "Unknown exception status."})
    exception_type = query_params.get("exception_type")
    if exception_type:
        validate_exception_type(exception_type)
    cases, _ = approval_case_engine.select_readable_approval_cases(
        actor=actor, actor_permissions=actor_permissions
    )
    queryset = (
        ExceptionRegisterEntry.objects.select_related(
            "loan_application", "approval_case__loan_application"
        )
        .prefetch_related("approval_case__actions")
        .filter(approval_case__in=cases)
    )
    if status:
        queryset = queryset.filter(status=status)
    if exception_type:
        queryset = queryset.filter(exception_type=exception_type)
    queryset = queryset.order_by("-created_at", "-exception_register_entry_id")
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    rows = [serialize_entry(entry) for entry in queryset[offset : offset + page_size]]
    return rows, {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def serialize_entry(entry):
    case = entry.approval_case
    authority = approval_case_engine.serialize_case_authority(case)
    summary = "; ".join(
        f"{_authority_label(item['role_code'])}: {item['full_name']}"
        + (f" ({item['decision']})" if item["decision"] else " (pending)")
        for item in authority["required_approvers"]
    )
    return {
        "exception_register_entry_id": str(entry.pk),
        "loan_application_id": (
            str(entry.loan_application_id) if entry.loan_application_id else None
        ),
        "loan_account_id": str(entry.loan_account_id) if entry.loan_account_id else None,
        "approval_case_id": str(case.pk),
        "cycle_number": case.cycle_number,
        "exception_type": entry.exception_type,
        "description": entry.description,
        "business_reason": entry.business_reason,
        "risk_assessment": entry.risk_assessment,
        "status": entry.status,
        "case_status": case.current_status,
        "conflict_block_reason": case.conflict_block_reason or None,
        "authority_applied_summary": summary,
        **authority,
        "created_at": entry.created_at.isoformat().replace("+00:00", "Z"),
        "closed_at": (
            entry.closed_at.isoformat().replace("+00:00", "Z")
            if entry.closed_at
            else None
        ),
    }


def _authority_label(role_code):
    return "CFO" if role_code == "cfo" else role_code.replace("_", " ").title()


def _required_text(field, value):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError({field: "This field must not be blank."})
    return value.strip()


def _positive_int(field, value, default):
    if value in (None, ""):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError({field: "Must be a positive integer."}) from exc
    if parsed < 1:
        raise ValidationError({field: "Must be a positive integer."})
    return parsed
