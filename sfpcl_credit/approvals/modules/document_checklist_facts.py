"""Approval-owned immutable sanction facts for the legal checklist boundary."""

from dataclasses import dataclass

from django.core.exceptions import ValidationError

from sfpcl_credit.approvals.models import ApprovalCase, SanctionDecision
from sfpcl_credit.approvals.modules import approval_case_engine


@dataclass(frozen=True)
class ApprovedChecklistFacts:
    sanction_decision_id: object
    approval_case_id: object
    holding_mode: str | None
    subsidiary_route: bool | None


def resolve_approved_facts(*, application_id):
    latest_case = (
        ApprovalCase.objects.filter(loan_application_id=application_id)
        .order_by("-cycle_number", "-submitted_at", "-approval_case_id")
        .first()
    )
    decision = (
        SanctionDecision.objects.select_related("approval_case")
        .filter(loan_application_id=application_id, decision="sanctioned")
        .first()
    )
    if (
        latest_case is None
        or decision is None
        or decision.approval_case_id != latest_case.pk
        or latest_case.current_status != ApprovalCase.STATUS_APPROVED
    ):
        return None
    try:
        terminal_facts = approval_case_engine.validated_frozen_terminal_facts(
            latest_case
        )
    except (KeyError, TypeError, ValidationError):
        return None
    review = terminal_facts["review_facts"]
    shareholding = review.get("shareholding") or {}
    active_member = ((review.get("eligibility") or {}).get("active_member_snapshot") or {})
    subsidiary_route = None
    subsidiary_flags = (
        "supplied_to_subsidiary_flag",
        "supplied_to_stepdown_flag",
    )
    if all(
        key in active_member and isinstance(active_member[key], bool)
        for key in subsidiary_flags
    ):
        subsidiary_route = any(
            active_member[key] for key in subsidiary_flags
        )
    return ApprovedChecklistFacts(
        sanction_decision_id=decision.pk,
        approval_case_id=latest_case.pk,
        holding_mode=shareholding.get("holding_mode"),
        subsidiary_route=subsidiary_route,
    )
