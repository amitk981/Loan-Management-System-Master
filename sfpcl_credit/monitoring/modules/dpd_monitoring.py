from decimal import Decimal
from uuid import UUID, uuid4

from django.db import transaction
from django.db.models import F, Q
from django.utils import timezone
from django.utils.dateparse import parse_date

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.loans.models import LoanAccount
from sfpcl_credit.loans.modules.dpd_source_decision import (
    DpdSourcePermissionDenied,
    resolve_locked_dpd_source_decision,
)
from sfpcl_credit.loans.modules.loan_account_read import (
    LoanAccountReadPermissionDenied,
    scoped_account_candidates,
)
from sfpcl_credit.monitoring.models import DpdOperationalBucketScheme, DpdStatus


READ_PERMISSION = "monitoring.dpd.read"
CALCULATE_PERMISSION = "monitoring.dpd.calculate"
CALCULATION_VERSION = "DPD-CALC-1"
SOP_POLICY_VERSION = "SFPCL-SOP-DPD-1"
SERVICEABLE_STATUSES = {
    "active",
    "partially_repaid",
    "overdue",
    "grace_period",
    "extended",
    "non_recoverable_under_review",
}
PORTFOLIO_LIMIT = 100


class DpdValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


class DpdPermissionDenied(Exception):
    pass


class DpdNotFound(Exception):
    pass


class DpdConflict(Exception):
    pass


def calculate_for_loan(*, actor, loan_account_id, payload, request=None):
    as_of_date = _validate_as_of_payload(payload)
    _require_permission(actor, CALCULATE_PERMISSION)
    account = _scoped_accounts(actor).filter(pk=loan_account_id).first()
    if account is None:
        raise DpdNotFound
    if account.loan_account_status not in SERVICEABLE_STATUSES:
        raise DpdConflict("The loan is not active for DPD calculation.")
    return _calculate_locked(
        actor=actor,
        loan_account_id=account.pk,
        as_of_date=as_of_date,
        request=request,
    )


def get_current_for_loan(*, actor, loan_account_id):
    _require_permission(actor, READ_PERMISSION)
    account = _scoped_accounts(actor).filter(pk=loan_account_id).first()
    if account is None or account.current_dpd_status_id is None:
        raise DpdNotFound
    row = DpdStatus.objects.select_related("operational_scheme").filter(
        pk=account.current_dpd_status_id,
        loan_account=account,
    ).first()
    if row is None:
        raise DpdNotFound
    return serialize_dpd_status(row)


def current_portfolio_projection(*, actor):
    _require_permission(actor, READ_PERMISSION)
    scoped = _scoped_accounts(actor)
    rows = list(
        DpdStatus.objects.select_related("loan_account__member")
        .filter(
            loan_account__in=scoped,
            loan_account__current_dpd_status_id=F("dpd_status_id"),
        )
        .order_by("loan_account__loan_account_number", "dpd_status_id")
    )
    bucket_counts = {
        "current": 0,
        "one_to_two_years": 0,
        "two_to_three_years": 0,
        "more_than_three_years": 0,
    }
    projected = []
    for row in rows:
        bucket_counts[row.sop_bucket] += 1
        projected.append(
            {
                **serialize_dpd_status(row),
                "loan_account_number": row.loan_account.loan_account_number,
                "member_display_name": row.loan_account.member.display_name,
                "loan_account_status": row.loan_account.loan_account_status,
                "principal_outstanding": f"{row.loan_account.principal_outstanding:.2f}",
                "interest_outstanding": f"{row.loan_account.interest_outstanding:.2f}",
                "repayment_date": row.loan_account.repayment_date.isoformat(),
            }
        )
    return {
        "sop_bucket_counts": bucket_counts,
        "total_count": len(projected),
        "rows": projected,
    }


def current_reminder_eligibility_decision(*, actor, loan_account_id):
    """Return current serviceability evidence without exposing a private DPD row."""
    _require_permission(actor, READ_PERMISSION)
    account = _scoped_accounts(actor).filter(pk=loan_account_id).first()
    if account is None or account.current_dpd_status_id is None:
        raise DpdNotFound
    row = DpdStatus.objects.filter(
        pk=account.current_dpd_status_id,
        loan_account=account,
    ).first()
    if row is None:
        raise DpdNotFound
    decision = reminder_eligibility_decision(
        dpd_status=row,
        quarter_end_date=row.as_of_date,
    )
    try:
        source = resolve_locked_dpd_source_decision(
            actor=actor,
            loan_account_id=account.pk,
            as_of_date=timezone.localdate(),
        )
    except DpdSourcePermissionDenied as exc:
        raise DpdPermissionDenied from exc
    if not any(
        line.principal_paid_as_of < line.principal_due
        or line.interest_paid_as_of < line.interest_due
        for line in source.schedule_lines
    ):
        return {**decision, "eligible": False, "reason": "loan_fully_paid"}
    return decision


def calculate_portfolio(*, actor, payload, request=None):
    cleaned = _validate_portfolio_payload(payload)
    _require_permission(actor, CALCULATE_PERMISSION)
    scoped = _scoped_accounts(actor)
    if cleaned["include_all_active_loans"]:
        account_ids = list(
            scoped.filter(loan_account_status__in=SERVICEABLE_STATUSES)
            .order_by("loan_account_id")
            .values_list("loan_account_id", flat=True)[:PORTFOLIO_LIMIT]
        )
    else:
        requested = cleaned["loan_account_ids"]
        accessible = set(
            scoped.filter(pk__in=requested).values_list("loan_account_id", flat=True)
        )
        account_ids = requested

    results = []
    for account_id in account_ids:
        if not cleaned["include_all_active_loans"] and account_id not in accessible:
            results.append(
                {"loan_account_id": str(account_id), "outcome": "failed", "reason": "inaccessible"}
            )
            continue
        if not cleaned["include_all_active_loans"]:
            account_status = LoanAccount.objects.filter(pk=account_id).values_list(
                "loan_account_status", flat=True
            ).first()
            if account_status not in SERVICEABLE_STATUSES:
                results.append(
                    {
                        "loan_account_id": str(account_id),
                        "outcome": "skipped",
                        "reason": "not_active",
                    }
                )
                continue
        try:
            snapshot = _calculate_locked(
                actor=actor,
                loan_account_id=account_id,
                as_of_date=cleaned["as_of_date"],
                request=request,
            )
            results.append(
                {
                    "loan_account_id": str(account_id),
                    "outcome": "calculated",
                    "dpd_status": snapshot,
                }
            )
        except (DpdConflict, DpdNotFound, DpdPermissionDenied) as exc:
            results.append(
                {"loan_account_id": str(account_id), "outcome": "failed", "reason": str(exc)}
            )
    run_id = uuid4()
    AuditLog.objects.create(
        actor_user=actor,
        action="monitoring.dpd.portfolio_calculated",
        entity_type="dpd_portfolio_run",
        entity_id=run_id,
        new_value_json={
            "as_of_date": cleaned["as_of_date"].isoformat(),
            "calculated_count": sum(row["outcome"] == "calculated" for row in results),
            "skipped_count": sum(row["outcome"] == "skipped" for row in results),
            "failed_count": sum(row["outcome"] == "failed" for row in results),
        },
        ip_address=request_ip(request) if request is not None else "",
        user_agent=request_user_agent(request) if request is not None else "",
    )
    return {
        "run_id": str(run_id),
        "as_of_date": cleaned["as_of_date"].isoformat(),
        "calculated_count": sum(row["outcome"] == "calculated" for row in results),
        "skipped_count": sum(row["outcome"] == "skipped" for row in results),
        "failed_count": sum(row["outcome"] == "failed" for row in results),
        "results": results,
    }


@transaction.atomic
def _calculate_locked(*, actor, loan_account_id, as_of_date, request):
    try:
        source_decision = resolve_locked_dpd_source_decision(
            actor=actor,
            loan_account_id=loan_account_id,
            as_of_date=as_of_date,
        )
    except DpdSourcePermissionDenied as exc:
        raise DpdPermissionDenied from exc
    if source_decision.loan_account_status not in SERVICEABLE_STATUSES:
        raise DpdConflict("The loan is not active for DPD calculation.")
    retained = DpdStatus.objects.filter(
        loan_account_id=source_decision.loan_account_id,
        as_of_date=as_of_date,
    ).first()
    if retained is not None:
        _advance_current_pointer(source_decision=source_decision, candidate=retained)
        return serialize_dpd_status(retained)

    calculation = _calculate_amounts(source_decision=source_decision)
    scheme = _effective_scheme(as_of_date)
    standard_bucket = _standard_bucket(
        calculation["days_past_due"],
        scheme,
        has_unpaid_schedule=calculation["earliest_unpaid_due_date"] is not None,
    )
    policy_decision = _freeze_policy_decision(scheme)
    audit = AuditLog.objects.create(
        actor_user=actor,
        action="monitoring.dpd.calculated",
        entity_type="loan_account",
        entity_id=source_decision.loan_account_id,
        new_value_json={
            "as_of_date": as_of_date.isoformat(),
            "calculation_version": CALCULATION_VERSION,
        },
        ip_address=request_ip(request) if request is not None else "",
        user_agent=request_user_agent(request) if request is not None else "",
    )
    row = DpdStatus.objects.create(
        loan_account_id=source_decision.loan_account_id,
        as_of_date=as_of_date,
        days_past_due=calculation["days_past_due"],
        sop_bucket=_sop_bucket(calculation["earliest_unpaid_due_date"], as_of_date),
        standard_bucket=standard_bucket,
        principal_overdue_amount=calculation["principal_overdue"],
        interest_overdue_amount=calculation["interest_overdue"],
        total_overdue_amount=(
            calculation["principal_overdue"] + calculation["interest_overdue"]
        ),
        earliest_unpaid_due_date=calculation["earliest_unpaid_due_date"],
        calculation_version=CALCULATION_VERSION,
        operational_scheme=scheme,
        calculation_inputs_json={
            **calculation["inputs"],
            "policy_decision": policy_decision,
        },
        calculated_by_user=actor,
        calculation_audit=audit,
    )
    _advance_current_pointer(source_decision=source_decision, candidate=row)
    return serialize_dpd_status(row)


def _advance_current_pointer(*, source_decision, candidate):
    if source_decision.current_dpd_status_id == candidate.pk:
        return
    current_date = DpdStatus.objects.filter(
        pk=source_decision.current_dpd_status_id,
        loan_account_id=source_decision.loan_account_id,
    ).values_list("as_of_date", flat=True).first()
    if current_date is not None and current_date > candidate.as_of_date:
        return
    updated = LoanAccount.objects.filter(
        pk=source_decision.loan_account_id
    ).update_current_dpd_status_if_open(dpd_status_id=candidate.pk)
    if updated != 1:
        raise DpdConflict("The loan is not active for DPD calculation.")


def _calculate_amounts(*, source_decision):
    principal = Decimal("0.00")
    interest = Decimal("0.00")
    earliest = None
    schedule_inputs = []
    for row in source_decision.schedule_lines:
        principal_remaining = row.principal_due - row.principal_paid_as_of
        interest_remaining = row.interest_due - row.interest_paid_as_of
        schedule_inputs.append(
            {
                "repayment_schedule_id": str(row.repayment_schedule_id),
                "due_date": row.due_date.isoformat(),
                "principal_due": f"{row.principal_due:.2f}",
                "interest_due": f"{row.interest_due:.2f}",
                "principal_paid_as_of": f"{row.principal_paid_as_of:.2f}",
                "interest_paid_as_of": f"{row.interest_paid_as_of:.2f}",
            }
        )
        if principal_remaining > 0 or interest_remaining > 0:
            earliest = earliest or row.due_date
            principal += max(principal_remaining, Decimal("0.00"))
            interest += max(interest_remaining, Decimal("0.00"))
    return {
        "days_past_due": (
            (source_decision.as_of_date - earliest).days if earliest else 0
        ),
        "earliest_unpaid_due_date": earliest,
        "principal_overdue": principal,
        "interest_overdue": interest,
        "inputs": {
            "schedule_lines": schedule_inputs,
            "applied_allocation_ids": [
                str(value) for value in source_decision.applied_allocation_ids
            ],
            "applied_capitalisation_ids": [
                str(value) for value in source_decision.applied_capitalisation_ids
            ],
            "as_of_date": source_decision.as_of_date.isoformat(),
        },
    }


def _sop_bucket(earliest_unpaid_due_date, as_of_date):
    if earliest_unpaid_due_date is None:
        return "current"
    first = _anniversary(earliest_unpaid_due_date, 1)
    second = _anniversary(earliest_unpaid_due_date, 2)
    third = _anniversary(earliest_unpaid_due_date, 3)
    if as_of_date < first:
        return "current"
    if as_of_date < second:
        return "one_to_two_years"
    if as_of_date <= third:
        return "two_to_three_years"
    return "more_than_three_years"


def _anniversary(value, years):
    try:
        return value.replace(year=value.year + years)
    except ValueError:
        return value.replace(year=value.year + years, day=28)


def reminder_eligibility_decision(*, dpd_status, quarter_end_date):
    """Return the retained DPD owner's calendar decision for a quarter reminder."""
    first_unpaid = dpd_status.earliest_unpaid_due_date
    first_anniversary = _anniversary(first_unpaid, 1) if first_unpaid else None
    policy = (dpd_status.calculation_inputs_json or {}).get("policy_decision", {})
    eligible = bool(
        dpd_status.as_of_date == quarter_end_date
        and first_anniversary is not None
        and quarter_end_date >= first_anniversary
        and dpd_status.total_overdue_amount > 0
    )
    if dpd_status.as_of_date != quarter_end_date:
        reason = "quarter_snapshot_mismatch"
    elif first_anniversary is None or dpd_status.total_overdue_amount <= 0:
        reason = "no_outstanding_due"
    elif quarter_end_date < first_anniversary:
        reason = "calendar_anniversary_not_reached"
    else:
        reason = "outstanding_beyond_one_year"
    return {
        "eligible": eligible,
        "reason": reason,
        "first_unpaid_due_date": first_unpaid.isoformat() if first_unpaid else None,
        "quarter_cutoff": quarter_end_date.isoformat(),
        "first_anniversary": first_anniversary.isoformat() if first_anniversary else None,
        "boundary_position": (
            "unavailable"
            if first_anniversary is None
            else "day_before"
            if quarter_end_date < first_anniversary
            else "on"
            if quarter_end_date == first_anniversary
            else "after"
        ),
        "calculation_version": dpd_status.calculation_version,
        "sop_policy_version": policy.get("sop_policy_version"),
        "sop_boundary_convention": policy.get("sop_boundary_convention"),
    }


def _effective_scheme(as_of_date):
    rows = list(
        DpdOperationalBucketScheme.objects.filter(
            effective_from__lte=as_of_date,
        )
        .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=as_of_date))
        .order_by("effective_from", "dpd_operational_bucket_scheme_id")
    )
    active_rows = [row for row in rows if row.status == "active"]
    if len(active_rows) > 1:
        raise DpdConflict("Multiple operational DPD bucket schemes are effective.")
    if rows and not active_rows:
        raise DpdConflict("The effective operational DPD bucket scheme is not approved.")
    return active_rows[0] if active_rows else None


def _standard_bucket(days_past_due, scheme, *, has_unpaid_schedule):
    if scheme is None or not has_unpaid_schedule:
        return None
    if days_past_due <= scheme.first_upper_days:
        return "0_30"
    if days_past_due <= scheme.second_upper_days:
        return "31_60"
    if days_past_due <= scheme.third_upper_days:
        return "61_90"
    return "over_90"


def _freeze_policy_decision(scheme):
    return {
        "sop_policy_version": SOP_POLICY_VERSION,
        "sop_boundary_convention": {
            "anniversary_basis": "calendar_anniversary",
            "leap_day_anniversary": "february_28",
            "first_anniversary_inclusive": True,
            "second_anniversary_inclusive": True,
            "third_anniversary_inclusive": True,
            "after_third_anniversary_bucket": "more_than_three_years",
        },
        "operational_scheme_id": str(scheme.pk) if scheme is not None else None,
        "operational_scheme_version": scheme.version if scheme is not None else None,
        "operational_effective_from": (
            scheme.effective_from.isoformat() if scheme is not None else None
        ),
        "operational_effective_to": (
            scheme.effective_to.isoformat()
            if scheme is not None and scheme.effective_to is not None
            else None
        ),
        "operational_boundaries": (
            {
                "first_upper_days": scheme.first_upper_days,
                "second_upper_days": scheme.second_upper_days,
                "third_upper_days": scheme.third_upper_days,
            }
            if scheme is not None
            else None
        ),
    }


def _validate_as_of_payload(payload):
    if set(payload) != {"as_of_date"}:
        raise DpdValidation({"body": "Only as_of_date is accepted."})
    value = payload.get("as_of_date")
    parsed = parse_date(value) if isinstance(value, str) else None
    if parsed is None:
        raise DpdValidation({"as_of_date": "Must be an ISO date."})
    return parsed


def _validate_portfolio_payload(payload):
    allowed = {"as_of_date", "loan_account_ids", "include_all_active_loans"}
    if set(payload) != allowed:
        raise DpdValidation(
            {"body": "Use as_of_date, loan_account_ids and include_all_active_loans."}
        )
    as_of_date = _validate_as_of_payload({"as_of_date": payload.get("as_of_date")})
    raw_ids = payload.get("loan_account_ids")
    include_all = payload.get("include_all_active_loans")
    if not isinstance(raw_ids, list):
        raise DpdValidation({"loan_account_ids": "Must be a list."})
    if len(raw_ids) > PORTFOLIO_LIMIT:
        raise DpdValidation({"loan_account_ids": "Must contain at most 100 ids."})
    try:
        account_ids = [UUID(str(value)) for value in raw_ids]
    except (ValueError, TypeError, AttributeError) as exc:
        raise DpdValidation({"loan_account_ids": "Each item must be a UUID."}) from exc
    if len(set(account_ids)) != len(account_ids):
        raise DpdValidation({"loan_account_ids": "Ids must be unique."})
    if not isinstance(include_all, bool):
        raise DpdValidation({"include_all_active_loans": "Must be a boolean."})
    if include_all == bool(account_ids):
        raise DpdValidation(
            {"include_all_active_loans": "Select either all active loans or one or more ids."}
        )
    return {
        "as_of_date": as_of_date,
        "loan_account_ids": account_ids,
        "include_all_active_loans": include_all,
    }


def _require_permission(actor, permission):
    if (
        not actor.can_authenticate()
        or permission not in auth_service.effective_permission_codes(actor)
    ):
        raise DpdPermissionDenied


def _scoped_accounts(actor):
    try:
        return scoped_account_candidates(actor=actor)
    except LoanAccountReadPermissionDenied as exc:
        raise DpdPermissionDenied from exc


def serialize_dpd_status(row):
    inputs = row.calculation_inputs_json
    policy_decision = inputs.get("policy_decision", {})
    return {
        "dpd_status_id": str(row.pk),
        "loan_account_id": str(row.loan_account_id),
        "as_of_date": row.as_of_date.isoformat(),
        "days_past_due": row.days_past_due,
        "sop_bucket": row.sop_bucket,
        "standard_bucket": row.standard_bucket,
        "principal_overdue_amount": f"{row.principal_overdue_amount:.2f}",
        "interest_overdue_amount": f"{row.interest_overdue_amount:.2f}",
        "total_overdue_amount": f"{row.total_overdue_amount:.2f}",
        "calculation_version": row.calculation_version,
        "operational_scheme_version": (
            policy_decision.get("operational_scheme_version")
            if policy_decision
            else (row.operational_scheme.version if row.operational_scheme_id else None)
        ),
        "policy_decision": policy_decision,
        "calculation_inputs": inputs,
        "created_at": row.created_at.isoformat().replace("+00:00", "Z"),
    }


__all__ = [
    "DpdConflict",
    "DpdNotFound",
    "DpdPermissionDenied",
    "DpdValidation",
    "calculate_for_loan",
    "current_portfolio_projection",
    "calculate_portfolio",
    "current_reminder_eligibility_decision",
    "get_current_for_loan",
    "reminder_eligibility_decision",
    "serialize_dpd_status",
]
