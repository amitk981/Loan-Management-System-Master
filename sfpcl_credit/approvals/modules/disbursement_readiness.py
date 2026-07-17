from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError

from sfpcl_credit.approvals.models import (
    ApprovalCase,
    ExceptionRegisterEntry,
    GeneralMeetingApproval,
    SanctionDecision,
)
@dataclass(frozen=True)
class ApprovalReadinessFacts:
    sanction_approved: bool
    exception_approval_complete: bool
    general_meeting_approval_complete: bool
    appraisal_complete: bool


@dataclass(frozen=True)
class TermSheetSignerRequirement:
    required_user_ids: frozenset[str]


def resolve_term_sheet_signer_requirement(*, application_id):
    """Return the approval-owned exact S32 user signer set."""
    from sfpcl_credit.approvals.modules import approval_case_engine

    case = (
        ApprovalCase.objects.filter(loan_application_id=application_id)
        .order_by("-cycle_number", "-submitted_at", "-approval_case_id")
        .first()
    )
    if case is None:
        return None
    try:
        frozen = approval_case_engine.validated_frozen_terminal_facts(case)
        above_threshold = Decimal(str(frozen["recommended_amount"])) > Decimal(
            "500000.00"
        )
    except (InvalidOperation, KeyError, TypeError, ValidationError):
        return None
    projection = case.committee_projection_json or {}
    cfo_id = str(projection.get("cfo_user_id") or "")
    excluded_ids = {
        str(row.get("user_id"))
        for row in (case.excluded_approvers_json or [])
        if isinstance(row, dict) and row.get("user_id")
    }
    directors = [
        str(value)
        for value in projection.get("director_user_ids", [])
        if value and str(value) not in excluded_ids
    ]
    if not cfo_id or (above_threshold and len(directors) < 2):
        return None
    required = {cfo_id, *(directors[:2] if above_threshold else [])}
    return TermSheetSignerRequirement(frozenset(required))


def resolve_approval_readiness(*, application_id, sanction_decision_id):
    """Project current approval-owned pre-initiation facts only."""
    case = (
        ApprovalCase.objects.select_for_update(of=("self",))
        .select_related(
            "loan_application",
            "loan_appraisal_note",
            "general_meeting_approval",
            "sanction_decision",
        )
        .filter(loan_application_id=application_id)
        .order_by("-cycle_number", "-submitted_at", "-approval_case_id")
        .first()
    )
    if case is None:
        return ApprovalReadinessFacts(False, False, False, False)
    sanction = (
        SanctionDecision.objects.select_for_update()
        .filter(pk=sanction_decision_id, loan_application_id=application_id)
        .first()
    )
    sanction_approved = bool(
        sanction
        and sanction.approval_case_id == case.pk
        and sanction.decision == "sanctioned"
        and case.current_status == ApprovalCase.STATUS_APPROVED
        and case.loan_application.application_status
        == "approved_by_sanction_committee"
    )
    exception = (
        ExceptionRegisterEntry.objects.select_for_update()
        .filter(approval_case=case, loan_application_id=application_id)
        .first()
    )
    exception_complete = not case.exception_required_flag or bool(
        exception and exception.status == ExceptionRegisterEntry.STATUS_APPROVED
    )
    meeting = case.general_meeting_approval
    meeting_complete = not case.general_meeting_evidence_required or bool(
        meeting
        and meeting.loan_application_id == application_id
        and meeting.approval_status == GeneralMeetingApproval.STATUS_APPROVED
        and not hasattr(meeting, "superseded_by")
    )
    note = case.loan_appraisal_note
    appraisal_complete = bool(
        note
        and note.loan_application_id == application_id
        and note.appraisal_status == "submitted_to_sanction_committee"
        and note.last_review_decision == "reviewed"
        and note.reviewed_at
    )
    return ApprovalReadinessFacts(
        sanction_approved,
        exception_complete,
        meeting_complete,
        appraisal_complete,
    )


__all__ = [
    "ApprovalReadinessFacts",
    "TermSheetSignerRequirement",
    "resolve_approval_readiness",
    "resolve_term_sheet_signer_requirement",
]
