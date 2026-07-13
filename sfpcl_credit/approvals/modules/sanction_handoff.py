"""Approval-owned persistence and read contract for sanction handoffs."""

from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from sfpcl_credit.approvals.models import ApprovalCase
from sfpcl_credit.applications import services as application_services
from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.credit.modules.appraisal_workflow import AppraisalWorkflow
from sfpcl_credit.domain_errors import (
    DomainInvalidStateError,
    DomainNotFound,
    DomainObjectAccessDenied,
)
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.workflows.events import record_workflow_event


SANCTION_SUBMIT_PERMISSION = "credit.appraisal.submit_sanction"


@dataclass(frozen=True)
class SanctionHandoffResult:
    snapshot: dict


class SanctionHandoffModule:
    """Own the unique pending case and its canonical public projection."""

    @transaction.atomic
    def submit_reviewed_appraisal(
        self,
        *,
        actor,
        application_id,
        payload,
        request_meta=None,
        actor_permissions=None,
    ):
        prepared = AppraisalWorkflow().prepare_sanction_handoff(
            actor=actor,
            application_id=application_id,
            payload=payload,
            actor_permissions=actor_permissions,
        )
        application = prepared.application
        appraisal_note = prepared.appraisal_note
        if (
            ApprovalCase.objects.select_for_update(of=("self",))
            .filter(loan_application=application)
            .exists()
        ):
            raise DomainInvalidStateError(
                "The appraisal has already been submitted for sanction."
            )
        now = timezone.now()
        case = ApprovalCase.objects.create(
            loan_application=application,
            loan_appraisal_note=appraisal_note,
            exception_required_flag=prepared.exception_required_flag,
            submission_remarks=payload["remarks"].strip(),
            submitted_by_user=actor,
            submitted_at=now,
        )
        application.application_status = LoanApplication.STATUS_SUBMITTED_TO_SANCTION
        application.save(update_fields=["application_status"])
        appraisal_note.appraisal_status = appraisal_note.STATUS_SUBMITTED_TO_SANCTION
        appraisal_note.save(update_fields=["appraisal_status"])
        request_meta = request_meta or {}
        AuditLog.objects.create(
            actor_user=actor,
            action="appraisal.submitted_to_sanction",
            entity_type="loan_appraisal_note",
            entity_id=appraisal_note.pk,
            old_value_json={
                "application_status": prepared.previous_application_status,
                "appraisal_status": prepared.previous_appraisal_status,
            },
            new_value_json={
                "approval_case_id": str(case.pk),
                "loan_application_id": str(application.pk),
                "loan_appraisal_note_id": str(appraisal_note.pk),
                "appraisal_review_decision_id": str(prepared.latest_review.pk),
                "application_status": application.application_status,
                "appraisal_status": appraisal_note.appraisal_status,
                "submission_status": case.current_status,
                "exception_required_flag": prepared.exception_required_flag,
                "submitted_by_user_id": str(actor.pk),
                "submitted_at": timezone.localtime(now).isoformat(),
                "request_id": request_meta.get("request_id"),
            },
            ip_address=request_meta.get("ip_address", ""),
            user_agent=request_meta.get("user_agent", ""),
        )
        event = record_workflow_event(
            actor=actor,
            workflow_name="sanction_submission",
            entity_type="loan_application",
            entity_id=application.pk,
            from_state=prepared.previous_appraisal_status,
            to_state=appraisal_note.appraisal_status,
            trigger_reason=(
                f"Appraisal {appraisal_note.pk} submitted as approval case {case.pk} "
                f"from review decision {prepared.latest_review.pk}."
            ),
            action_code="appraisal.submitted_to_sanction",
            metadata={
                "approval_case_id": str(case.pk),
                "appraisal_review_decision_id": str(prepared.latest_review.pk),
            },
        )
        case.workflow_event = event
        case.save(update_fields=["workflow_event"])
        return SanctionHandoffResult(
            snapshot=self.serialize(case, prepared.latest_review)
        )

    def get_pending(self, *, actor, application_id, actor_permissions=None):
        application = LoanApplication.objects.filter(pk=application_id).first()
        if application is None:
            raise DomainNotFound("Loan application was not found.")
        object_access = application_services.evaluate_application_object_access(
            application,
            actor,
            SANCTION_SUBMIT_PERMISSION,
            actor_permissions,
        )
        if not object_access.allowed:
            raise DomainObjectAccessDenied(object_access)
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
            raise DomainNotFound("Pending sanction case was not found.")
        latest_review = case.loan_appraisal_note.review_decisions.order_by(
            "-decided_at", "-appraisal_review_decision_id"
        ).first()
        return SanctionHandoffResult(
            snapshot=self.serialize(case, latest_review)
        )

    @staticmethod
    def serialize(case, latest_review_decision):
        return {
            "approval_case_id": str(case.pk),
            "loan_application_id": str(case.loan_application_id),
            "loan_appraisal_note_id": str(case.loan_appraisal_note_id),
            "appraisal_review_decision_id": (
                str(latest_review_decision.pk) if latest_review_decision else None
            ),
            "workflow_event_id": str(case.workflow_event_id) if case.workflow_event_id else None,
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
