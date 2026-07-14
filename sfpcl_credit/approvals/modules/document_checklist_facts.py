"""Approval-owned immutable sanction facts for the legal checklist boundary."""

from dataclasses import dataclass

from sfpcl_credit.approvals.models import ApprovalCase, SanctionDecision


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
        or not latest_case.routing_snapshot_is_coherent
    ):
        return None
    review = latest_case.appraisal_facts_json or {}
    shareholding = review.get("shareholding") or {}
    active_member = ((review.get("eligibility") or {}).get("active_member_snapshot") or {})
    subsidiary_route = None
    if active_member:
        subsidiary_route = bool(
            active_member.get("supplied_to_subsidiary_flag")
            or active_member.get("supplied_to_stepdown_flag")
        )
    return ApprovedChecklistFacts(
        sanction_decision_id=decision.pk,
        approval_case_id=latest_case.pk,
        holding_mode=shareholding.get("holding_mode"),
        subsidiary_route=subsidiary_route,
    )
