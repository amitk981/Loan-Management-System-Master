import calendar
from datetime import date
from math import ceil
from uuid import UUID, uuid4

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.approvals.models import ApprovalCaseReadScopeGrant
from sfpcl_credit.defaults.models import DefaultCase
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.loans.models import LoanAccount
from sfpcl_credit.loans.modules.dpd_source_decision import (
    DpdSourcePermissionDenied,
    resolve_locked_dpd_source_decision,
)
from sfpcl_credit.workflows.events import record_workflow_event


READ_PERMISSION = "defaults.case.read"
OPEN_PERMISSION = "defaults.case.open"


class DefaultValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


class DefaultPermissionDenied(Exception):
    pass


class DefaultNotFound(Exception):
    pass


class DefaultConflict(Exception):
    pass


class DefaultWorkflow:
    @classmethod
    def open_if_missed_repayment(
        cls,
        *,
        actor,
        loan_account_id,
        as_of_date,
        scheduled_due_date,
        trigger_event=DefaultCase.TRIGGER_MISSED_PRINCIPAL,
        reason="",
        request=None,
    ):
        _require_open_authority(actor)
        cleaned = _validate_open_input(
            as_of_date=as_of_date,
            scheduled_due_date=scheduled_due_date,
            trigger_event=trigger_event,
            reason=reason,
        )
        with transaction.atomic():
            try:
                decision = resolve_locked_dpd_source_decision(
                    actor=actor,
                    loan_account_id=loan_account_id,
                    as_of_date=cleaned["as_of_date"],
                )
            except DpdSourcePermissionDenied as exc:
                raise DefaultNotFound from exc
            obligation = next(
                (
                    line
                    for line in decision.schedule_lines
                    if line.due_date == cleaned["scheduled_due_date"]
                    and line.principal_due > 0
                ),
                None,
            )
            if obligation is None:
                raise DefaultConflict(
                    "No scheduled principal obligation exists for the supplied due date."
                )
            existing = DefaultCase.objects.filter(
                repayment_schedule_id=obligation.repayment_schedule_id,
                trigger_event=cleaned["trigger_event"],
            ).first()
            if existing is not None:
                return existing
            if obligation.principal_paid_as_of >= obligation.principal_due:
                return None

            account = LoanAccount.objects.select_related("member").get(
                pk=decision.loan_account_id
            )
            case_id = uuid4()
            new_state = {
                "loan_account_id": str(account.pk),
                "member_id": str(account.member_id),
                "default_case_id": str(case_id),
                "trigger_event": cleaned["trigger_event"],
                "scheduled_due_date": cleaned["scheduled_due_date"].isoformat(),
                "default_case_status": DefaultCase.STATUS_GRACE_PERIOD_ACTIVE,
            }
            audit = AuditLog.objects.create(
                actor_user=actor,
                action="default.case_opened",
                entity_type="default_case",
                entity_id=case_id,
                old_value_json=None,
                new_value_json=new_state,
                ip_address=request_ip(request) if request is not None else "",
                user_agent=request_user_agent(request) if request is not None else "",
            )
            row = DefaultCase.objects.create(
                default_case_id=case_id,
                loan_account=account,
                member=account.member,
                repayment_schedule_id=obligation.repayment_schedule_id,
                trigger_event=cleaned["trigger_event"],
                scheduled_due_date=cleaned["scheduled_due_date"],
                grace_period_start_date=cleaned["scheduled_due_date"],
                grace_period_end_date=_add_calendar_months(
                    cleaned["scheduled_due_date"], 3
                ),
                default_case_status=DefaultCase.STATUS_GRACE_PERIOD_ACTIVE,
                reason=cleaned["reason"],
                opened_by_user=actor,
                opening_audit=audit,
            )
            record_workflow_event(
                actor=actor,
                workflow_name="default_case",
                entity_type="default_case",
                entity_id=row.pk,
                from_state=None,
                to_state=row.default_case_status,
                trigger_reason=row.reason,
                action_code="default.case_opened",
            )
            return row


def get_default_case(*, actor, default_case_id):
    row = _scoped_case_candidates(actor=actor).filter(pk=default_case_id).first()
    if row is None:
        raise DefaultNotFound
    return serialize_default_case(row, actor=actor)


def list_default_cases(*, actor, query_params):
    allowed = {
        "default_case_status",
        "member_id",
        "loan_account_id",
        "page",
        "page_size",
    }
    unknown = set(query_params) - allowed
    if unknown:
        raise DefaultValidation(
            {field: "Unknown query parameter." for field in sorted(unknown)}
        )
    filters = {}
    status = query_params.get("default_case_status")
    if status:
        if status not in _DEFAULT_CASE_STATUSES:
            raise DefaultValidation(
                {"default_case_status": "Must be a valid default case status."}
            )
        filters["default_case_status"] = status
    for field in ("member_id", "loan_account_id"):
        value = query_params.get(field)
        if value:
            try:
                filters[field] = UUID(str(value))
            except (TypeError, ValueError, AttributeError) as exc:
                raise DefaultValidation({field: "Must be a valid UUID."}) from exc
    page = _positive_int("page", query_params.get("page"), default=1, maximum=None)
    page_size = _positive_int(
        "page_size", query_params.get("page_size"), default=20, maximum=100
    )
    queryset = _scoped_case_candidates(actor=actor).filter(**filters)
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    rows = queryset[offset : offset + page_size]
    return [serialize_default_case(row, actor=actor) for row in rows], {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def serialize_default_case(row, *, actor):
    return {
        "default_case_id": str(row.pk),
        "loan_account_id": str(row.loan_account_id),
        "member_id": str(row.member_id),
        "trigger_event": row.trigger_event,
        "scheduled_due_date": row.scheduled_due_date.isoformat(),
        "repayment_schedule_id": str(row.repayment_schedule_id),
        "default_case_status": row.default_case_status,
        "grace_period_start_date": row.grace_period_start_date.isoformat(),
        "grace_period_end_date": row.grace_period_end_date.isoformat(),
        "reason": row.reason,
        # Later default actions belong to slices 011B onward.
        "available_actions": [],
    }


def serialize_opened_default_case(row):
    """Return the exact source §35.1 result plus server-owned actions."""
    return {
        "default_case_id": str(row.pk),
        "default_case_status": row.default_case_status,
        "grace_period_start_date": row.grace_period_start_date.isoformat(),
        "grace_period_end_date": row.grace_period_end_date.isoformat(),
        "available_actions": [],
    }


def _require_permission(actor, permission):
    if (
        not actor.can_authenticate()
        or permission not in auth_service.effective_permission_codes(actor)
    ):
        raise DefaultPermissionDenied


def _require_open_authority(actor):
    _require_permission(actor, OPEN_PERMISSION)
    if "credit_manager" not in auth_service.effective_role_codes(actor):
        raise DefaultPermissionDenied


def _scoped_case_candidates(*, actor):
    _require_permission(actor, READ_PERMISSION)
    roles = set(auth_service.effective_role_codes(actor))
    scope = Q(pk__in=[])
    if "credit_manager" in roles:
        scope |= Q(
            loan_account__loan_account_status__in={
                "active",
                "partially_repaid",
                "overdue",
                "grace_period",
                "extended",
                "non_recoverable_under_review",
            }
        )
    if "company_secretary" in roles:
        scope |= Q(
            loan_account__loan_application__application_status=
            LoanApplication.STATUS_APPROVED_BY_SANCTION
        )
    scope |= Q(
        loan_account__sanction_decision__approval_case__required_approver_index__user_id=actor.pk
    )
    auditor_portfolio = (
        "internal_auditor" in roles
        and ApprovalCaseReadScopeGrant.objects.filter(
            role__role_code="internal_auditor",
            scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
            status=ApprovalCaseReadScopeGrant.STATUS_ACTIVE,
        ).exists()
    )
    queryset = DefaultCase.objects.select_related("loan_account", "member")
    if not auditor_portfolio:
        queryset = queryset.filter(scope)
    return queryset.distinct().order_by("-default_detected_at", "-default_case_id")


def _validate_open_input(*, as_of_date, scheduled_due_date, trigger_event, reason):
    parsed_as_of = _parse_date("as_of_date", as_of_date)
    parsed_due = _parse_date("scheduled_due_date", scheduled_due_date)
    errors = {}
    if trigger_event != DefaultCase.TRIGGER_MISSED_PRINCIPAL:
        errors["trigger_event"] = "Must be missed_principal_repayment."
    if parsed_due >= parsed_as_of:
        errors["scheduled_due_date"] = "Must be before the detection date."
    if not isinstance(reason, str):
        errors["reason"] = "Must be a string."
    elif len(reason) > 2000:
        errors["reason"] = "Must be at most 2000 characters."
    if errors:
        raise DefaultValidation(errors)
    return {
        "as_of_date": parsed_as_of,
        "scheduled_due_date": parsed_due,
        "trigger_event": trigger_event,
        "reason": reason.strip(),
    }


def _parse_date(field, value):
    if isinstance(value, date):
        return value
    parsed = parse_date(value) if isinstance(value, str) else None
    if parsed is None:
        raise DefaultValidation({field: "Must be a valid ISO date."})
    return parsed


def _add_calendar_months(value, months):
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _positive_int(field, value, *, default, maximum):
    if value in (None, ""):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise DefaultValidation({field: "Must be a positive integer."}) from exc
    if parsed < 1 or (maximum is not None and parsed > maximum):
        message = (
            f"Must be between 1 and {maximum}."
            if maximum is not None
            else "Must be a positive integer."
        )
        raise DefaultValidation({field: message})
    return parsed


def api_open_default_case(*, actor, loan_account_id, payload, request=None):
    allowed = {"trigger_event", "scheduled_due_date", "reason"}
    unknown = set(payload) - allowed
    if unknown:
        raise DefaultValidation(
            {field: "Unknown request field." for field in sorted(unknown)}
        )
    row = DefaultWorkflow.open_if_missed_repayment(
        actor=actor,
        loan_account_id=loan_account_id,
        as_of_date=timezone.localdate(),
        scheduled_due_date=payload.get("scheduled_due_date"),
        trigger_event=payload.get("trigger_event"),
        reason=payload.get("reason", ""),
        request=request,
    )
    if row is None:
        raise DefaultConflict("The scheduled principal obligation is not missed.")
    return serialize_opened_default_case(row)


_DEFAULT_CASE_STATUSES = {
    "open",
    "grace_period_active",
    "grace_period_expired",
    "assessment_in_progress",
    "extension_granted",
    "extension_expired",
    "non_payment_under_review",
    "recovery_decision_pending",
    "recovery_approved",
    "recovery_in_progress",
    "resolved_by_repayment",
    "closed",
}
