from dataclasses import dataclass

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


def resolve_approval_readiness(*, application_id, sanction_decision_id):
    """Project current approval-owned pre-initiation facts only."""
    case = (
        ApprovalCase.objects.select_for_update()
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


__all__ = ["ApprovalReadinessFacts", "resolve_approval_readiness"]
