from django.db.models import Sum

from sfpcl_credit.defaults.modules.default_workflow import (
    DefaultPermissionDenied,
    _scoped_case_candidates,
)
from sfpcl_credit.recovery.models import RecoveryDecision
from sfpcl_credit.recovery.modules.recovery_decision import EXECUTABLE_ACTIONS
from sfpcl_credit.reports.errors import ReportPermissionDenied, ReportValidation
from sfpcl_credit.reports.pagination import paginate
from sfpcl_credit.reports.query import reject_unknown


def select(*, actor, query_params):
    reject_unknown(query_params, {"decision", "action_status", "page", "page_size"})
    try:
        case_ids = _scoped_case_candidates(actor=actor).values("pk")
    except DefaultPermissionDenied as exc:
        raise ReportPermissionDenied from exc
    queryset = RecoveryDecision.objects.select_related(
        "default_case__loan_account",
        "default_case__member",
        "recovery_action",
    ).filter(default_case_id__in=case_ids)
    decision = query_params.get("decision")
    if decision:
        if decision not in EXECUTABLE_ACTIONS:
            raise ReportValidation({"decision": "Unsupported recovery decision."})
        queryset = queryset.filter(decision=decision)
    action_status = query_params.get("action_status")
    if action_status:
        if action_status not in {"pending", "completed", "failed"}:
            raise ReportValidation({"action_status": "Unsupported action status."})
        queryset = queryset.filter(recovery_action__action_status=action_status)
    total = queryset.aggregate(value=Sum("recovery_action__amount_recovered"))["value"]
    rows, pagination = paginate(
        queryset.order_by("-decided_at", "-recovery_decision_id"),
        query_params,
    )
    pagination["totals"] = {"amount_recovered": f"{(total or 0):.2f}"}
    return [_serialize(row) for row in rows], pagination


def _serialize(row):
    action = row.recovery_action if hasattr(row, "recovery_action") else None
    return {
        "recovery_decision_id": str(row.pk),
        "default_case_id": str(row.default_case_id),
        "loan_account_id": str(row.default_case.loan_account_id),
        "member_id": str(row.default_case.member_id),
        "borrower_name": row.default_case.member.display_name,
        "decision": row.decision,
        "decision_status": row.status,
        "decided_at": row.decided_at.isoformat().replace("+00:00", "Z"),
        "recovery_action_id": str(action.pk) if action else None,
        "action_type": action.action_type if action else None,
        "action_status": action.action_status if action else None,
        "amount_recovered": (
            f"{action.amount_recovered:.2f}"
            if action and action.amount_recovered is not None
            else None
        ),
    }
