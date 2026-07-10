"""Approval-owned persistence and read contract for sanction handoffs."""

from dataclasses import dataclass

from django.utils import timezone

from sfpcl_credit.approvals.models import ApprovalCase
from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.credit.modules.common import (
    CreditModuleInvalidStateError,
    CreditModuleNotFound,
    require_application_access,
)
from sfpcl_credit.workflows.models import WorkflowEvent


SANCTION_SUBMIT_PERMISSION = "credit.appraisal.submit_sanction"


@dataclass(frozen=True)
class SanctionHandoffResult:
    snapshot: dict


class SanctionHandoffModule:
    """Own the unique pending case and its canonical public projection."""

    def create_pending(
        self,
        *,
        application,
        appraisal_note,
        actor,
        remarks,
        exception_required_flag,
        submitted_at,
    ):
        if (
            ApprovalCase.objects.select_for_update(of=("self",))
            .filter(loan_application=application)
            .exists()
        ):
            raise CreditModuleInvalidStateError(
                "The appraisal has already been submitted for sanction."
            )
        return ApprovalCase.objects.create(
            loan_application=application,
            loan_appraisal_note=appraisal_note,
            exception_required_flag=exception_required_flag,
            submission_remarks=remarks,
            submitted_by_user=actor,
            submitted_at=submitted_at,
        )

    def get_pending(self, *, actor, application_id, actor_permissions=None):
        application = LoanApplication.objects.filter(pk=application_id).first()
        if application is None:
            raise CreditModuleNotFound("Loan application was not found.")
        require_application_access(
            application,
            actor,
            SANCTION_SUBMIT_PERMISSION,
            actor_permissions,
        )
        case = (
            ApprovalCase.objects.select_related(
                "loan_application",
                "loan_appraisal_note",
                "submitted_by_user",
            )
            .filter(loan_application=application)
            .first()
        )
        if case is None:
            raise CreditModuleNotFound("Pending sanction case was not found.")
        latest_review = case.loan_appraisal_note.review_decisions.order_by(
            "-decided_at", "-appraisal_review_decision_id"
        ).first()
        workflow_event = WorkflowEvent.objects.filter(
            workflow_name="sanction_submission",
            entity_type="loan_application",
            entity_id=application.pk,
        ).order_by("-created_at", "-workflow_event_id").first()
        return SanctionHandoffResult(
            snapshot=self.serialize(case, latest_review, workflow_event)
        )

    @staticmethod
    def serialize(case, latest_review_decision, workflow_event):
        return {
            "approval_case_id": str(case.pk),
            "loan_application_id": str(case.loan_application_id),
            "loan_appraisal_note_id": str(case.loan_appraisal_note_id),
            "appraisal_review_decision_id": (
                str(latest_review_decision.pk) if latest_review_decision else None
            ),
            "workflow_event_id": str(workflow_event.pk) if workflow_event else None,
            "application_status": case.loan_application.application_status,
            "appraisal_status": case.loan_appraisal_note.appraisal_status,
            "submission_status": case.current_status,
            "exception_required_flag": case.exception_required_flag,
            "submitted_by": {
                "user_id": str(case.submitted_by_user_id),
                "full_name": case.submitted_by_user.full_name,
            },
            "submitted_at": timezone.localtime(case.submitted_at).isoformat(),
            "available_actions": [],
        }
