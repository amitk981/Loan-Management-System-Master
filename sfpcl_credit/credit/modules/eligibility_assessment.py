from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from sfpcl_credit.applications.modules.nominee_validation import evaluate_nominee_selection
from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.applications.services import build_completeness_workbench
from sfpcl_credit.credit.models import EligibilityAssessment, LoanAppraisalNote
from sfpcl_credit.credit.modules.common import (
    APPLICATION_READ_PERMISSION,
    ELIGIBILITY_RUN_PERMISSION,
    CreditModuleInvalidStateError,
    CreditModuleNotFound,
    get_application_or_raise,
    normalize_request_meta,
    require_application_access,
    require_permission,
)
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.members.modules.active_member_status import ActiveMemberStatusModule
from sfpcl_credit.workflows.events import record_workflow_event


ELIGIBILITY_ASSESSED_AUDIT_ACTION = "eligibility.assessed"


@dataclass(frozen=True)
class EligibilityAssessmentResult:
    assessment: EligibilityAssessment
    snapshot: dict


@dataclass(frozen=True)
class EligibilityRunEvaluation:
    allowed: bool
    reason: str | None


class EligibilityAssessmentModule:
    def get(self, *, actor, application_id, actor_permissions=None):
        permissions = require_permission(
            actor,
            APPLICATION_READ_PERMISSION,
            "You do not have permission to read loan applications.",
            actor_permissions,
        )
        application = get_application_or_raise(application_id)
        require_application_access(
            application,
            actor,
            APPLICATION_READ_PERMISSION,
            permissions,
        )
        assessment = (
            EligibilityAssessment.objects.select_related("loan_application", "assessed_by_user")
            .filter(loan_application=application)
            .first()
        )
        if assessment is None:
            raise CreditModuleNotFound("Eligibility assessment was not found.")
        return EligibilityAssessmentResult(
            assessment=assessment,
            snapshot=_snapshot_with_actions(assessment, application, actor, permissions),
        )

    @transaction.atomic
    def run(self, *, actor, application_id, request_meta=None, actor_permissions=None):
        permissions = require_permission(
            actor,
            ELIGIBILITY_RUN_PERMISSION,
            "You do not have permission to run eligibility assessments.",
            actor_permissions,
        )
        request_meta = normalize_request_meta(request_meta)
        application = (
            LoanApplication.objects.select_for_update(of=("self",))
            .select_related("member", "nominee", "created_by_user", "received_by_user")
            .filter(loan_application_id=application_id)
            .first()
        )
        if application is None:
            raise CreditModuleNotFound("Loan application was not found.")
        require_application_access(
            application,
            actor,
            ELIGIBILITY_RUN_PERMISSION,
            permissions,
        )
        transition = evaluate_eligibility_run(application)
        if not transition.allowed:
            raise CreditModuleInvalidStateError(transition.reason)

        member_result = ActiveMemberStatusModule().calculate(member_id=application.member_id)
        active_result = {
            "member_active_check": member_result.member_active_check,
            "overall_result": member_result.overall_result,
            "assessment_notes": member_result.assessment_notes,
        }
        source_checks = _source_backed_eligibility_checks(application)
        assessment = (
            EligibilityAssessment.objects.select_for_update()
            .filter(loan_application=application)
            .first()
        )
        old_value_json = (
            eligibility_assessment_snapshot(assessment) if assessment is not None else None
        )
        if assessment is None:
            assessment = EligibilityAssessment(loan_application=application)
        assessment.member_active_check = active_result["member_active_check"]
        assessment.default_check = source_checks["default_check"]
        assessment.document_check = source_checks["document_check"]
        assessment.terms_acceptance_check = source_checks["terms_acceptance_check"]
        assessment.purpose_check = source_checks["purpose_check"]
        assessment.nominee_check = source_checks["nominee_check"]
        assessment.overall_result = _eligibility_overall_result(active_result, source_checks)
        assessment.assessment_notes = _eligibility_assessment_notes(
            active_result,
            source_checks,
            assessment.overall_result,
        )
        assessment.assessed_by_user = actor
        assessment.assessed_at = timezone.now()
        assessment.save()
        _audit_eligibility_assessment(assessment, actor, old_value_json, request_meta)
        record_workflow_event(
            actor=actor,
            workflow_name="eligibility_assessment",
            entity_type="loan_application",
            entity_id=application.loan_application_id,
            from_state=application.current_stage,
            to_state="eligibility_assessed",
            trigger_reason="Eligibility assessment active-member check completed.",
            action_code=ELIGIBILITY_ASSESSED_AUDIT_ACTION,
        )
        return EligibilityAssessmentResult(
            assessment=assessment,
            snapshot=_snapshot_with_actions(assessment, application, actor, permissions),
        )


def evaluate_eligibility_run(application):
    if LoanAppraisalNote.objects.filter(loan_application=application).exists():
        return EligibilityRunEvaluation(False, "Eligibility assessment cannot be rerun after appraisal has started.")
    if not (application.application_reference_number or "").startswith("LO"):
        return EligibilityRunEvaluation(False, "Eligibility assessment requires a formal LO application reference.")
    if application.application_status != LoanApplication.STATUS_REFERENCE_GENERATED:
        return EligibilityRunEvaluation(False, (
            "Invalid state transition for loan_application: eligibility_assessment.run "
            f"is not allowed from {application.application_status}."
        ))
    if application.completeness_status != LoanApplication.COMPLETENESS_COMPLETE:
        return EligibilityRunEvaluation(False, "Eligibility assessment requires complete application documentation.")
    if application.current_stage != LoanApplication.STAGE_CREDIT_ASSESSMENT:
        return EligibilityRunEvaluation(False, "Eligibility assessment is allowed only in credit assessment stage.")
    return EligibilityRunEvaluation(True, None)


def eligibility_run_invalid_state_message(application):
    """Compatibility wrapper; transition authority lives in evaluate_eligibility_run."""
    return evaluate_eligibility_run(application).reason


def _snapshot_with_actions(assessment, application, actor, permissions):
    from sfpcl_credit.credit.modules.loan_limit_calculator import loan_limit_calculate_action

    snapshot = eligibility_assessment_snapshot(assessment)
    snapshot["available_actions"] = [eligibility_run_action(
        application,
        actor,
        permissions,
    ), loan_limit_calculate_action(application, permissions, actor)]
    return snapshot


def eligibility_run_action(application, actor, permissions=None):
    from sfpcl_credit.credit.modules.common import project_application_object_access

    if permissions is None:
        permissions = auth_service.effective_permission_codes(actor)
    transition = evaluate_eligibility_run(application)
    enabled = transition.allowed and ELIGIBILITY_RUN_PERMISSION in permissions
    projected = {
        "action_code": ELIGIBILITY_RUN_PERMISSION,
        "label": "Run Eligibility Assessment",
        "enabled": enabled,
        "disabled_reason": None if enabled else transition.reason or "You do not have permission to run eligibility assessments.",
        "required_permission": ELIGIBILITY_RUN_PERMISSION,
        "required_role": None,
    }
    return project_application_object_access(
        projected,
        application=application,
        actor=actor,
        permission_code=ELIGIBILITY_RUN_PERMISSION,
        actor_permissions=permissions,
    )


def eligibility_assessment_snapshot(assessment):
    return {
        "eligibility_assessment_id": str(assessment.eligibility_assessment_id),
        "loan_application_id": str(assessment.loan_application_id),
        "member_active_check": assessment.member_active_check,
        "default_check": assessment.default_check,
        "document_check": assessment.document_check,
        "terms_acceptance_check": assessment.terms_acceptance_check,
        "purpose_check": assessment.purpose_check,
        "nominee_check": assessment.nominee_check,
        "overall_result": assessment.overall_result,
        "assessment_notes": assessment.assessment_notes,
        "assessed_by_user_id": str(assessment.assessed_by_user_id),
        "assessed_at": timezone.localtime(assessment.assessed_at).isoformat(),
    }


def _audit_eligibility_assessment(assessment, actor, old_value_json, request_meta):
    new_value_json = eligibility_assessment_snapshot(assessment)
    new_value_json["request_id"] = request_meta.request_id
    AuditLog.objects.create(
        actor_user=actor,
        action=ELIGIBILITY_ASSESSED_AUDIT_ACTION,
        entity_type="eligibility_assessment",
        entity_id=assessment.eligibility_assessment_id,
        old_value_json=old_value_json,
        new_value_json=new_value_json,
        ip_address=request_meta.ip_address,
        user_agent=request_meta.user_agent,
    )


def _source_backed_eligibility_checks(application):
    nominee_check = _nominee_check(application.nominee, application.member)
    return {
        "default_check": (
            "no_default" if application.member.default_status == "no_default" else "default_found"
        ),
        "document_check": _document_check(application),
        "terms_acceptance_check": (
            "accepted" if application.terms_acceptance_flag else "pending"
        ),
        "purpose_check": (
            "agriculture_aligned"
            if application.purpose_category in {"crop_production", "agriculture_activity"}
            else "non_agriculture"
        ),
        "nominee_check": nominee_check,
        "nominee_manual_evidence_required": nominee_check == EligibilityAssessment.CHECK_PENDING,
    }


def _document_check(application):
    workbench = build_completeness_workbench(application)
    return "incomplete" if workbench["blocking_document_types"] else "complete"


def _nominee_check(nominee, member=None):
    if member is None:
        return EligibilityAssessment.CHECK_PENDING
    return evaluate_nominee_selection(nominee, member).status


def _eligibility_overall_result(active_result, source_checks):
    if active_result["member_active_check"] == EligibilityAssessment.MEMBER_ACTIVE_FAIL:
        return EligibilityAssessment.OVERALL_INELIGIBLE
    if any(
        (
            source_checks["default_check"] == "default_found",
            source_checks["document_check"] == "incomplete",
            source_checks["terms_acceptance_check"] == "pending",
            source_checks["purpose_check"] == "non_agriculture",
            source_checks["nominee_check"] == "minor",
        )
    ):
        return EligibilityAssessment.OVERALL_INELIGIBLE
    if active_result["overall_result"] == EligibilityAssessment.OVERALL_PENDING_MANUAL_EVIDENCE:
        return EligibilityAssessment.OVERALL_PENDING_MANUAL_EVIDENCE
    if source_checks["nominee_manual_evidence_required"]:
        return EligibilityAssessment.OVERALL_PENDING_MANUAL_EVIDENCE
    return EligibilityAssessment.OVERALL_ELIGIBLE


def _eligibility_assessment_notes(active_result, source_checks, overall_result):
    blockers = []
    if active_result["member_active_check"] == EligibilityAssessment.MEMBER_ACTIVE_FAIL:
        blockers.append("BR-003 active-member evidence failed")
    if source_checks["default_check"] == "default_found":
        blockers.append("BR-008 default history blocks normal eligibility")
    if source_checks["document_check"] == "incomplete":
        blockers.append("BR-013/BR-014 required checklist evidence is incomplete")
    if source_checks["terms_acceptance_check"] == "pending":
        blockers.append("S15 terms acceptance is pending")
    if source_checks["purpose_check"] == "non_agriculture":
        blockers.append("BR-018 purpose is not agriculture-aligned")
    if source_checks["nominee_check"] == "minor":
        blockers.append("BR-009 nominee is a minor")
    if blockers:
        return "; ".join(blockers) + "."
    if overall_result == EligibilityAssessment.OVERALL_PENDING_MANUAL_EVIDENCE:
        if source_checks["nominee_manual_evidence_required"]:
            if active_result["member_active_check"] == EligibilityAssessment.MEMBER_ACTIVE_PASS:
                return (
                    "Source-backed default, document, terms, and purpose checks passed. "
                    "Application-specific nominee selection is pending."
                )
            return (
                active_result["assessment_notes"]
                + " Application-specific nominee selection is pending."
            )
        return active_result["assessment_notes"]
    return "All mandatory eligibility criteria passed."
