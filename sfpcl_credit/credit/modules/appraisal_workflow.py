"""Deep module for appraisal-note preparation and review transitions."""

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone

from sfpcl_credit.applications.modules.rejection_notes import (
    RejectionNoteInvalidStateError,
    RejectionNoteModule,
    RejectionNoteValidationError,
)
from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.credit.models import (
    AppraisalReviewDecision,
    LoanAppraisalNote,
    RiskAssessment,
)
from sfpcl_credit.credit.modules.common import (
    APPLICATION_READ_PERMISSION,
    CreditModuleInvalidStateError,
    CreditModuleNotFound,
    CreditModulePermissionDenied,
    CreditModuleValidationError,
    normalize_request_meta,
    project_application_object_access,
    require_application_access,
    require_permission,
)
from sfpcl_credit.credit.modules.eligibility_assessment import EligibilityAssessmentModule
from sfpcl_credit.credit.modules.loan_limit_calculator import LoanLimitCalculator
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.workflows.events import record_workflow_event


APPRAISAL_CREATE_PERMISSION = "credit.appraisal.create"
APPRAISAL_UPDATE_PERMISSION = "credit.appraisal.update"
APPRAISAL_SUBMIT_PERMISSION = "credit.appraisal.submit_review"
APPRAISAL_REVIEW_PERMISSION = "credit.appraisal.review"
APPRAISAL_SANCTION_SUBMIT_PERMISSION = "credit.appraisal.submit_sanction"
RISK_MANAGE_PERMISSION = "credit.risk_assessment.manage"
APPRAISAL_READ_PERMISSIONS = {
    APPRAISAL_CREATE_PERMISSION,
    APPRAISAL_UPDATE_PERMISSION,
    APPRAISAL_SUBMIT_PERMISSION,
    APPRAISAL_REVIEW_PERMISSION,
    APPRAISAL_SANCTION_SUBMIT_PERMISSION,
}


@dataclass(frozen=True)
class AppraisalNoteResult:
    snapshot: dict


@dataclass(frozen=True)
class AppraisalTransitionEvaluation:
    allowed: bool
    reason: str | None


def evaluate_appraisal_update(note, permissions):
    if note.appraisal_status != LoanAppraisalNote.STATUS_DRAFT:
        return AppraisalTransitionEvaluation(False, "Only draft appraisal notes can be updated.")
    return AppraisalTransitionEvaluation(True, None)


def evaluate_appraisal_revalidation(note, permissions):
    if RISK_MANAGE_PERMISSION not in permissions:
        return AppraisalTransitionEvaluation(False, "Risk changes require risk-assessment authority.")
    if note.appraisal_status not in {LoanAppraisalNote.STATUS_DRAFT, LoanAppraisalNote.STATUS_REVIEW_PENDING, LoanAppraisalNote.STATUS_REVIEWED}:
        return AppraisalTransitionEvaluation(False, "Rejected or sanction-submitted appraisal notes require governed manual repair.")
    if note.prerequisite_provenance != "legacy_unverified":
        return AppraisalTransitionEvaluation(False, "Only legacy-unverified appraisal prerequisites can be revalidated.")
    return AppraisalTransitionEvaluation(True, None)


def evaluate_appraisal_submission(note):
    if note.appraisal_status != LoanAppraisalNote.STATUS_DRAFT:
        return AppraisalTransitionEvaluation(False, "Only a draft appraisal note can be submitted for review.")
    if note.prerequisite_provenance != "verified":
        return AppraisalTransitionEvaluation(False, "Appraisal prerequisites must be explicitly revalidated before review.")
    if _submission_errors(note):
        return AppraisalTransitionEvaluation(False, "Appraisal and risk assessment must be complete before review.")
    return AppraisalTransitionEvaluation(True, None)


def evaluate_appraisal_review(note, actor):
    if note.appraisal_status != LoanAppraisalNote.STATUS_REVIEW_PENDING:
        return AppraisalTransitionEvaluation(False, "Only a review-pending appraisal note can be reviewed.")
    if note.prerequisite_provenance != "verified":
        return AppraisalTransitionEvaluation(False, "Appraisal review requires verified prerequisite snapshots.")
    if note.prepared_by_user_id == actor.pk:
        return AppraisalTransitionEvaluation(False, "The appraisal preparer cannot review their own appraisal note.")
    return AppraisalTransitionEvaluation(True, None)


def evaluate_sanction_submission(note, *, latest_review=None, history_locked=False):
    if note.appraisal_status != LoanAppraisalNote.STATUS_REVIEWED:
        return AppraisalTransitionEvaluation(False, "Only a reviewed appraisal note can be submitted for sanction.")
    if note.prerequisite_provenance != "verified":
        return AppraisalTransitionEvaluation(False, "Sanction submission requires verified prerequisite snapshots.")
    if _submission_errors(note):
        return AppraisalTransitionEvaluation(False, "Sanction submission requires a complete appraisal and risk assessment.")
    if not _frozen_prerequisites_complete(note):
        return AppraisalTransitionEvaluation(False, "Sanction submission requires complete frozen eligibility and loan-limit snapshots.")
    if not history_locked:
        latest_review = note.review_decisions.order_by("decided_at", "appraisal_review_decision_id").last()
    if latest_review is None or not _latest_review_matches_note(note, latest_review):
        return AppraisalTransitionEvaluation(False, "The latest immutable review decision does not match the reviewed appraisal.")
    return AppraisalTransitionEvaluation(True, None)


def appraisal_available_actions(note, actor, permissions):
    """Project the actions governed by this module's public transition predicates."""
    permissions = set(permissions)
    roles = set(actor.role_codes())

    def action(
        code,
        label,
        permission,
        allowed,
        role=None,
        reason=None,
        permission_reason=None,
        role_reason=None,
    ):
        enabled = allowed and permission in permissions and (role is None or role in roles)
        disabled_reason = reason or "Unavailable for this appraisal state or authority."
        if permission not in permissions:
            disabled_reason = permission_reason or f"Required permission {permission} is missing."
        elif role is not None and role not in roles:
            disabled_reason = role_reason or f"Required role {role} is missing."
        return {
            "action_code": code,
            "label": label,
            "enabled": enabled,
            "disabled_reason": None if enabled else disabled_reason,
            "required_permission": permission,
            "required_role": role,
        }

    evaluations = {
        APPRAISAL_UPDATE_PERMISSION: evaluate_appraisal_update(note, permissions),
        "revalidate_appraisal_prerequisites": evaluate_appraisal_revalidation(note, permissions),
        APPRAISAL_SUBMIT_PERMISSION: evaluate_appraisal_submission(note),
        APPRAISAL_REVIEW_PERMISSION: evaluate_appraisal_review(note, actor),
        APPRAISAL_SANCTION_SUBMIT_PERMISSION: evaluate_sanction_submission(note),
    }
    actions = [
        action(APPRAISAL_UPDATE_PERMISSION, "Update Appraisal Draft", APPRAISAL_UPDATE_PERMISSION, evaluations[APPRAISAL_UPDATE_PERMISSION].allowed, reason=evaluations[APPRAISAL_UPDATE_PERMISSION].reason, permission_reason="You do not have permission to update appraisal notes."),
        action("revalidate_appraisal_prerequisites", "Revalidate Prerequisites", APPRAISAL_UPDATE_PERMISSION, evaluations["revalidate_appraisal_prerequisites"].allowed, reason=evaluations["revalidate_appraisal_prerequisites"].reason, permission_reason="You do not have permission to revalidate appraisal prerequisites."),
        action(APPRAISAL_SUBMIT_PERMISSION, "Submit for Credit Review", APPRAISAL_SUBMIT_PERMISSION, evaluations[APPRAISAL_SUBMIT_PERMISSION].allowed, reason=evaluations[APPRAISAL_SUBMIT_PERMISSION].reason, permission_reason="You do not have permission to submit appraisal notes for review."),
        action(APPRAISAL_REVIEW_PERMISSION, "Record Credit Review", APPRAISAL_REVIEW_PERMISSION, evaluations[APPRAISAL_REVIEW_PERMISSION].allowed, role="credit_manager", reason=evaluations[APPRAISAL_REVIEW_PERMISSION].reason, permission_reason="You do not have permission to review appraisal notes.", role_reason="Only an active Credit Manager may review appraisal notes."),
        action(APPRAISAL_SANCTION_SUBMIT_PERMISSION, "Submit to Sanction Committee", APPRAISAL_SANCTION_SUBMIT_PERMISSION, evaluations[APPRAISAL_SANCTION_SUBMIT_PERMISSION].allowed, role="credit_manager", reason=evaluations[APPRAISAL_SANCTION_SUBMIT_PERMISSION].reason, permission_reason="You do not have permission to submit appraisals for sanction.", role_reason="Only an active Credit Manager may submit appraisals for sanction."),
    ]
    return [
        project_application_object_access(
            projected,
            application=note.loan_application,
            actor=actor,
            permission_code=projected["required_permission"],
            actor_permissions=permissions,
        )
        for projected in actions
    ]


def _result_with_actions(note, actor, permissions, snapshot=None):
    projected = dict(snapshot or appraisal_note_snapshot(note))
    projected["available_actions"] = appraisal_available_actions(note, actor, permissions)
    return AppraisalNoteResult(snapshot=projected)


@dataclass(frozen=True)
class ReviewedAppraisalHandoff:
    application: LoanApplication
    appraisal_note: LoanAppraisalNote
    latest_review: AppraisalReviewDecision
    previous_application_status: str
    previous_appraisal_status: str
    exception_required_flag: bool


@dataclass(frozen=True)
class ApprovalCaseEnrichmentFacts:
    application: LoanApplication
    appraisal_note: LoanAppraisalNote
    latest_review: AppraisalReviewDecision
    decision_date: date
    recommended_amount: Decimal
    exception_required_flag: bool
    loan_limit_provenance: dict
    review_facts: dict


def project_approval_case_review_facts(*, application, appraisal_note, review):
    """Project the credit-owned immutable review package consumed by approvals."""
    eligibility = appraisal_note.eligibility_snapshot_json
    loan_limit = appraisal_note.loan_limit_snapshot_json
    risk = appraisal_note.risk_assessment
    witness = application.witnesses.filter(
        verification_status="verified", shareholder_verified_flag=True
    ).order_by("created_at", "witness_id").first()
    application_id = str(application.pk)
    return {
        "snapshot_schema_version": "approval-review-v3",
        "snapshot_provenance": {
            "owner": "credit",
            "review_decision_id": str(review.pk),
        },
        "maker_checker": {
            "application_created_by_user_id": (
                str(application.created_by_user_id)
                if application.created_by_user_id else None
            ),
            "application_received_by_user_id": str(application.received_by_user_id),
            "application_submitted_by_user_id": (
                str(application.submitted_by_user_id)
                if application.submitted_by_user_id else None
            ),
            "appraisal_prepared_by_user_id": str(appraisal_note.prepared_by_user_id),
            "appraisal_reviewed_by_user_id": str(review.reviewer_user_id),
        },
        "borrower": {
            "member_id": str(application.member_id),
            "application_reference_number": application.application_reference_number,
            "name": application.member.display_name or application.member.legal_name,
            "member_type": application.borrower_type,
            "folio_number": application.member.folio_number,
            "loan_type": application.loan_type_requested or "",
        },
        "nominee": (
            {
                "nominee_id": str(application.nominee_id),
                "name": application.nominee.nominee_name,
            }
            if application.nominee_id
            else None
        ),
        "witness": (
            {
                "witness_id": str(witness.pk),
                "name": witness.witness_name,
                "version": witness.version,
            }
            if witness
            else None
        ),
        "shareholding": {
            "shareholding_id": loan_limit.get("shareholding_id"),
            "number_of_shares": loan_limit.get("number_of_shares"),
        },
        "eligibility": eligibility,
        "loan_amounts": {
            "requested_amount": (
                f"{application.required_loan_amount:.2f}"
                if application.required_loan_amount is not None else None
            ),
            "eligible_amount": loan_limit.get("final_eligible_loan_amount"),
            "recommended_amount": f"{appraisal_note.recommended_amount:.2f}",
        },
        "sanction_terms": {
            "recommended_tenure_months": appraisal_note.recommended_tenure_months,
            "recommended_interest_type": appraisal_note.recommended_interest_type,
            "recommended_security_summary": (
                appraisal_note.recommended_security_summary
            ),
        },
        "purpose": {
            "category": application.purpose_category or None,
            "description": application.declared_purpose or None,
        },
        "compliance_checks": {
            key: eligibility.get(key)
            for key in (
                "member_active_check",
                "default_check",
                "terms_acceptance_check",
                "purpose_check",
            )
        },
        "borrowing_history": appraisal_note.borrower_summary,
        "risk": {
            "risk_assessment_id": str(risk.pk),
            "market_risk_rating": risk.market_risk_rating,
            "operational_risk_rating": risk.operational_risk_rating,
            "borrower_risk_rating": risk.borrower_risk_rating,
            "overall_risk_rating": risk.overall_risk_rating,
            "risk_mitigation_notes": risk.risk_mitigation_notes,
        },
        "documentation_completeness": {
            "status": application.completeness_status,
            "document_check": eligibility.get("document_check"),
        },
        "source_references": {
            "application": f"/api/v1/loan-applications/{application_id}/",
            "appraisal": f"/api/v1/loan-applications/{application_id}/appraisal-note/",
            "eligibility": f"/api/v1/loan-applications/{application_id}/eligibility-assessment/",
            "loan_limit": f"/api/v1/loan-applications/{application_id}/loan-limit-assessment/",
        },
    }


class AppraisalWorkflow:
    @staticmethod
    def lock_submitted_appraisal(*, appraisal_id):
        """Lock and return an appraisal for the approval-owned transaction."""
        return LoanAppraisalNote.objects.select_for_update().get(pk=appraisal_id)

    @staticmethod
    def restore_reviewed_state(appraisal_note):
        appraisal_note.appraisal_status = LoanAppraisalNote.STATUS_REVIEWED
        appraisal_note.save(update_fields=["appraisal_status"])

    @transaction.atomic
    def create_or_update(
        self,
        *,
        actor,
        application_id,
        payload,
        partial=False,
        request_meta=None,
        actor_permissions=None,
    ):
        permission = APPRAISAL_UPDATE_PERMISSION if partial else APPRAISAL_CREATE_PERMISSION
        permissions = require_permission(
            actor,
            permission,
            "You do not have permission to update appraisal notes."
            if partial
            else "You do not have permission to create appraisal notes.",
            actor_permissions,
        )
        if not partial or "risk_assessment" in payload:
            require_permission(
                actor,
                RISK_MANAGE_PERMISSION,
                "You do not have permission to manage risk assessments.",
                permissions,
            )
        application = (
            LoanApplication.objects.select_for_update(of=("self",))
            .select_related("created_by_user", "received_by_user")
            .filter(loan_application_id=application_id)
            .first()
        )
        if application is None:
            raise CreditModuleNotFound("Loan application was not found.")
        require_application_access(application, actor, permission, permissions)
        payload = _clean_payload(payload, partial=partial)
        current = (
            LoanAppraisalNote.objects.select_for_update(of=("self",))
            .select_related("risk_assessment", "prepared_by_user", "reviewed_by_user")
            .filter(loan_application=application)
            .first()
        )
        if partial:
            loan_limit = current.loan_limit_snapshot_json if current is not None else {}
        else:
            projection_permissions = set(permissions) | {APPLICATION_READ_PERMISSION}
            try:
                eligibility = EligibilityAssessmentModule().get(
                    actor=actor,
                    application_id=application_id,
                    actor_permissions=projection_permissions,
                ).snapshot
                eligibility = {key: value for key, value in eligibility.items() if key != "available_actions"}
            except CreditModuleNotFound as exc:
                raise CreditModuleInvalidStateError(
                    "A stored eligible eligibility assessment is required before appraisal."
                ) from exc
            if eligibility["overall_result"] != "eligible":
                raise CreditModuleInvalidStateError(
                    "Appraisal creation requires eligibility overall_result eligible."
                )
            try:
                loan_limit = LoanLimitCalculator().get_assessment(
                    actor=actor,
                    application_id=application_id,
                    actor_permissions=projection_permissions,
                ).snapshot
                loan_limit = {key: value for key, value in loan_limit.items() if key != "available_actions"}
            except CreditModuleNotFound as exc:
                raise CreditModuleInvalidStateError(
                    "A stored loan-limit assessment is required before appraisal."
                ) from exc
        if (
            "recommended_amount" in payload
            and loan_limit
            and payload["recommended_amount"]
            > Decimal(loan_limit["final_eligible_loan_amount"])
            and not loan_limit["exception_required_flag"]
        ):
            raise CreditModuleValidationError(
                {
                    "recommended_amount": (
                        "Cannot exceed the frozen final eligible amount unless the frozen "
                        "loan-limit projection already requires an exception."
                    )
                }
            )
        if partial:
            if current is None:
                raise CreditModuleNotFound("Appraisal note was not found.")
            transition = evaluate_appraisal_update(current, permissions)
            if not transition.allowed:
                raise CreditModuleInvalidStateError(transition.reason)
            changed_fields = []
            for field in (
                "borrower_summary",
                "eligibility_summary",
                "loan_limit_summary",
                "recommended_amount",
                "recommended_tenure_months",
                "recommended_interest_type",
                "recommended_security_summary",
                "repayment_capacity_notes",
                "recommendation",
            ):
                if field in payload:
                    value = payload[field]
                    if field == "recommended_amount":
                        value = Decimal(str(value))
                    if getattr(current, field) != value:
                        setattr(current, field, value)
                        changed_fields.append(field)
            risk_payload = payload.get("risk_assessment", {})
            for field in (
                "market_risk_rating",
                "operational_risk_rating",
                "borrower_risk_rating",
                "overall_risk_rating",
                "risk_mitigation_notes",
            ):
                if field in risk_payload:
                    value = risk_payload[field]
                    if getattr(current.risk_assessment, field) != value:
                        setattr(current.risk_assessment, field, value)
                        changed_fields.append(f"risk_assessment.{field}")
            risk_changed = any(
                field.startswith("risk_assessment.") for field in changed_fields
            )
            if risk_changed:
                current.risk_assessment.assessed_by_user = actor
                current.risk_assessment.assessed_at = timezone.now()
                current.risk_assessment.save()
            current.save()
            request_meta = normalize_request_meta(request_meta)
            AuditLog.objects.create(
                actor_user=actor,
                action="appraisal.updated",
                entity_type="loan_appraisal_note",
                entity_id=current.pk,
                old_value_json={"appraisal_status": current.appraisal_status},
                new_value_json={
                    "appraisal_status": current.appraisal_status,
                    "changed_fields": sorted(changed_fields),
                    "request_id": request_meta.request_id,
                },
                ip_address=request_meta.ip_address,
                user_agent=request_meta.user_agent,
            )
            record_workflow_event(
                actor=actor,
                workflow_name="appraisal_note",
                entity_type="loan_appraisal_note",
                entity_id=current.pk,
                from_state=current.appraisal_status,
                to_state=current.appraisal_status,
                trigger_reason="Appraisal note draft updated.",
                action_code="appraisal.updated",
            )
            return _result_with_actions(current, actor, permissions)
        if current is not None:
            raise CreditModuleInvalidStateError(
                "An appraisal note already exists for this loan application."
            )

        now = timezone.now()
        risk_payload = payload["risk_assessment"]
        risk = RiskAssessment.objects.create(
            loan_application=application,
            market_risk_rating=risk_payload["market_risk_rating"],
            operational_risk_rating=risk_payload["operational_risk_rating"],
            borrower_risk_rating=risk_payload["borrower_risk_rating"],
            overall_risk_rating=risk_payload["overall_risk_rating"],
            risk_mitigation_notes=risk_payload.get("risk_mitigation_notes", ""),
            assessed_by_user=actor,
            assessed_at=now,
        )
        due_at = application.created_at + timedelta(days=2)
        note = LoanAppraisalNote.objects.create(
            loan_application=application,
            prepared_by_user=actor,
            prepared_at=now,
            tat_due_at=due_at,
            tat_status=_tat_status(now, due_at),
            eligibility_assessment_id_snapshot=eligibility["eligibility_assessment_id"],
            loan_limit_assessment_id_snapshot=loan_limit["loan_limit_assessment_id"],
            eligibility_snapshot_json=eligibility,
            loan_limit_snapshot_json=loan_limit,
            prerequisite_provenance="verified",
            borrower_summary=payload["borrower_summary"],
            eligibility_summary=payload["eligibility_summary"],
            loan_limit_summary=payload["loan_limit_summary"],
            recommended_amount=payload["recommended_amount"],
            recommended_tenure_months=payload.get("recommended_tenure_months"),
            recommended_interest_type=payload.get("recommended_interest_type", ""),
            recommended_security_summary=payload["recommended_security_summary"],
            repayment_capacity_notes=payload["repayment_capacity_notes"],
            risk_assessment=risk,
            recommendation=payload["recommendation"],
            appraisal_status=LoanAppraisalNote.STATUS_DRAFT,
        )
        request_meta = normalize_request_meta(request_meta)
        AuditLog.objects.create(
            actor_user=actor,
            action="appraisal.created",
            entity_type="loan_appraisal_note",
            entity_id=note.loan_appraisal_note_id,
            old_value_json=None,
            new_value_json={
                "loan_appraisal_note_id": str(note.pk),
                "loan_application_id": str(application.pk),
                "risk_assessment_id": str(risk.pk),
                "eligibility_assessment_id": str(note.eligibility_assessment_id_snapshot),
                "loan_limit_assessment_id": str(note.loan_limit_assessment_id_snapshot),
                "appraisal_status": note.appraisal_status,
                "request_id": request_meta.request_id,
            },
            ip_address=request_meta.ip_address,
            user_agent=request_meta.user_agent,
        )
        record_workflow_event(
            actor=actor,
            workflow_name="appraisal_note",
            entity_type="loan_appraisal_note",
            entity_id=note.pk,
            from_state="not_started",
            to_state=note.appraisal_status,
            trigger_reason="Appraisal note draft created.",
            action_code="appraisal.created",
        )
        return _result_with_actions(note, actor, permissions)

    def get(self, *, actor, application_id, actor_permissions=None):
        permissions = actor_permissions or auth_service.effective_permission_codes(actor)
        permission = next(
            (code for code in APPRAISAL_READ_PERMISSIONS if code in permissions),
            None,
        )
        if permission is None:
            require_permission(
                actor,
                APPRAISAL_CREATE_PERMISSION,
                "You do not have permission to read appraisal notes.",
                permissions,
            )
        application = (
            LoanApplication.objects.select_related("created_by_user", "received_by_user")
            .filter(loan_application_id=application_id)
            .first()
        )
        if application is None:
            raise CreditModuleNotFound("Loan application was not found.")
        require_application_access(application, actor, permission, permissions)
        note = (
            LoanAppraisalNote.objects.select_related(
                "risk_assessment",
                "prepared_by_user",
                "reviewed_by_user",
            )
            .filter(loan_application=application)
            .first()
        )
        if note is None:
            raise CreditModuleNotFound("Appraisal note was not found.")
        return _result_with_actions(note, actor, permissions)

    @transaction.atomic
    def submit_for_review(
        self,
        *,
        actor,
        appraisal_id,
        payload,
        request_meta=None,
        actor_permissions=None,
    ):
        permissions = require_permission(
            actor,
            APPRAISAL_SUBMIT_PERMISSION,
            "You do not have permission to submit appraisal notes for review.",
            actor_permissions,
        )
        unknown = sorted(set(payload) - {"remarks"})
        errors = {field: "Unknown field." for field in unknown}
        if not isinstance(payload.get("remarks"), str) or not payload["remarks"].strip():
            errors["remarks"] = "This field must not be blank."
        if errors:
            raise CreditModuleValidationError(errors)
        note = _lock_appraisal_after_application(appraisal_id)
        require_application_access(
            note.loan_application,
            actor,
            APPRAISAL_SUBMIT_PERMISSION,
            permissions,
        )
        transition = evaluate_appraisal_submission(note)
        if not transition.allowed and (
            note.appraisal_status != LoanAppraisalNote.STATUS_DRAFT
            or note.prerequisite_provenance != "verified"
        ):
            raise CreditModuleInvalidStateError(transition.reason)
        submission_errors = _submission_errors(note)
        if submission_errors:
            raise CreditModuleValidationError(submission_errors)
        now = timezone.now()
        note.appraisal_status = LoanAppraisalNote.STATUS_REVIEW_PENDING
        note.tat_status = _tat_status(now, note.tat_due_at)
        note.submission_remarks = payload["remarks"].strip()
        note.save(
            update_fields=["appraisal_status", "tat_status", "submission_remarks"]
        )
        request_meta = normalize_request_meta(request_meta)
        AuditLog.objects.create(
            actor_user=actor,
            action="appraisal.submitted_for_review",
            entity_type="loan_appraisal_note",
            entity_id=note.pk,
            old_value_json={"appraisal_status": LoanAppraisalNote.STATUS_DRAFT},
            new_value_json={
                "appraisal_status": note.appraisal_status,
                "tat_status": note.tat_status,
                "submission_reason_exists": True,
                "submission_reason_owner_id": str(note.pk),
                "request_id": request_meta.request_id,
            },
            ip_address=request_meta.ip_address,
            user_agent=request_meta.user_agent,
        )
        record_workflow_event(
            actor=actor,
            workflow_name="appraisal_note",
            entity_type="loan_appraisal_note",
            entity_id=note.pk,
            from_state=LoanAppraisalNote.STATUS_DRAFT,
            to_state=note.appraisal_status,
            trigger_reason="Appraisal note submitted for Credit Manager review.",
            action_code="appraisal.submitted_for_review",
        )
        return _result_with_actions(note, actor, permissions)

    @transaction.atomic
    def revalidate_prerequisites(
        self,
        *,
        actor,
        appraisal_id,
        payload,
        request_meta=None,
        actor_permissions=None,
    ):
        permissions = require_permission(
            actor,
            APPRAISAL_UPDATE_PERMISSION,
            "You do not have permission to revalidate appraisal prerequisites.",
            actor_permissions,
        )
        require_permission(
            actor,
            RISK_MANAGE_PERMISSION,
            "You do not have permission to manage risk assessments.",
            permissions,
        )
        if payload:
            raise CreditModuleValidationError(
                {field: "Unknown field." for field in sorted(payload)}
            )
        note = _lock_appraisal_after_application(appraisal_id)
        require_application_access(
            note.loan_application,
            actor,
            APPRAISAL_UPDATE_PERMISSION,
            permissions,
        )
        transition = evaluate_appraisal_revalidation(note, permissions)
        if not transition.allowed:
            raise CreditModuleInvalidStateError(transition.reason)
        projection_permissions = set(permissions) | {APPLICATION_READ_PERMISSION}
        eligibility = EligibilityAssessmentModule().get(
            actor=actor,
            application_id=note.loan_application_id,
            actor_permissions=projection_permissions,
        ).snapshot
        eligibility = {key: value for key, value in eligibility.items() if key != "available_actions"}
        if eligibility["overall_result"] != "eligible":
            raise CreditModuleInvalidStateError(
                "Revalidation requires eligibility overall_result eligible."
            )
        loan_limit = LoanLimitCalculator().get_assessment(
            actor=actor,
            application_id=note.loan_application_id,
            actor_permissions=projection_permissions,
        ).snapshot
        loan_limit = {key: value for key, value in loan_limit.items() if key != "available_actions"}
        prior_state = note.appraisal_status
        note.eligibility_assessment_id_snapshot = eligibility[
            "eligibility_assessment_id"
        ]
        note.loan_limit_assessment_id_snapshot = loan_limit[
            "loan_limit_assessment_id"
        ]
        note.eligibility_snapshot_json = eligibility
        note.loan_limit_snapshot_json = loan_limit
        note.prerequisite_provenance = "verified"
        review_authority_invalidated = prior_state == LoanAppraisalNote.STATUS_REVIEWED
        if review_authority_invalidated:
            note.appraisal_status = LoanAppraisalNote.STATUS_DRAFT
            note.reviewed_by_user = None
            note.reviewed_at = None
            note.review_comments = ""
            note.last_review_decision = ""
        update_fields = [
            "eligibility_assessment_id_snapshot",
            "loan_limit_assessment_id_snapshot",
            "eligibility_snapshot_json",
            "loan_limit_snapshot_json",
            "prerequisite_provenance",
        ]
        if review_authority_invalidated:
            update_fields.extend(
                [
                    "appraisal_status",
                    "reviewed_by_user",
                    "reviewed_at",
                    "review_comments",
                    "last_review_decision",
                ]
            )
        note.save(update_fields=update_fields)
        request_meta = normalize_request_meta(request_meta)
        AuditLog.objects.create(
            actor_user=actor,
            action="appraisal.prerequisites_revalidated",
            entity_type="loan_appraisal_note",
            entity_id=note.pk,
            old_value_json={
                "prerequisite_provenance": "legacy_unverified",
                "appraisal_status": prior_state,
            },
            new_value_json={
                "prerequisite_provenance": "verified",
                "appraisal_status": note.appraisal_status,
                "review_authority_invalidated": review_authority_invalidated,
                "eligibility_assessment_id": str(
                    note.eligibility_assessment_id_snapshot
                ),
                "loan_limit_assessment_id": str(
                    note.loan_limit_assessment_id_snapshot
                ),
                "request_id": request_meta.request_id,
            },
            ip_address=request_meta.ip_address,
            user_agent=request_meta.user_agent,
        )
        record_workflow_event(
            actor=actor,
            workflow_name="appraisal_note",
            entity_type="loan_appraisal_note",
            entity_id=note.pk,
            from_state=prior_state,
            to_state=note.appraisal_status,
            trigger_reason="Appraisal prerequisite projections revalidated.",
            action_code="appraisal.prerequisites_revalidated",
        )
        return _result_with_actions(note, actor, permissions)

    @transaction.atomic
    def review(
        self,
        *,
        actor,
        appraisal_id,
        decision,
        comments,
        request_meta=None,
        actor_permissions=None,
        payload_fields=None,
    ):
        permissions = require_permission(
            actor,
            APPRAISAL_REVIEW_PERMISSION,
            "You do not have permission to review appraisal notes.",
            actor_permissions,
        )
        if "credit_manager" not in actor.role_codes():
            raise CreditModulePermissionDenied(
                "Only an active Credit Manager may review appraisal notes."
            )
        errors = {}
        payload = payload_fields or {}
        allowed_fields = {"decision", "review_comments"}
        if decision == "rejected":
            allowed_fields.update(
                {
                    "rejection_reason_category",
                    "detailed_reason",
                    "reapply_allowed_flag",
                    "communication_mode",
                }
            )
        unknown = sorted(set(payload) - allowed_fields)
        errors.update({field: "Unknown field." for field in unknown})
        if decision not in {"reviewed", "returned", "rejected"}:
            errors["decision"] = "Must be reviewed, returned, or rejected."
        if not isinstance(comments, str) or not comments.strip():
            errors["review_comments"] = "This field must not be blank."
        if errors:
            raise CreditModuleValidationError(errors)
        note = _lock_appraisal_after_application(appraisal_id)
        require_application_access(
            note.loan_application,
            actor,
            APPRAISAL_REVIEW_PERMISSION,
            permissions,
        )
        transition = evaluate_appraisal_review(note, actor)
        if not transition.allowed:
            if note.prepared_by_user_id == actor.pk:
                raise CreditModulePermissionDenied(transition.reason)
            raise CreditModuleInvalidStateError(transition.reason)
        # Existing immutable history is locked only after its owning application and
        # appraisal. The appraisal lock serializes an empty history as well.
        list(note.review_decisions.select_for_update().only("pk"))

        from_state = note.appraisal_status
        now = timezone.now()
        rejection_note = None
        if decision == "rejected":
            rejection_payload = {
                field: payload.get(field)
                for field in (
                    "rejection_reason_category",
                    "detailed_reason",
                    "reapply_allowed_flag",
                    "communication_mode",
                )
                if field in payload
            }
            request_meta = normalize_request_meta(request_meta)
            try:
                rejection_note = RejectionNoteModule().create_credit_draft(
                    application=note.loan_application,
                    payload=rejection_payload,
                    actor=actor,
                    request_ip=request_meta.ip_address,
                    request_user_agent=request_meta.user_agent,
                    request_id=request_meta.request_id,
                )
            except RejectionNoteValidationError as exc:
                raise CreditModuleValidationError(exc.field_errors) from exc
            except RejectionNoteInvalidStateError as exc:
                raise CreditModuleInvalidStateError(str(exc)) from exc
            note.appraisal_status = LoanAppraisalNote.STATUS_REJECTED
        elif decision == "reviewed":
            note.appraisal_status = LoanAppraisalNote.STATUS_REVIEWED
        else:
            note.appraisal_status = LoanAppraisalNote.STATUS_DRAFT
        note.reviewed_by_user = actor
        note.reviewed_at = now
        note.review_comments = comments.strip()
        note.last_review_decision = decision
        note.save(
            update_fields=(
                "appraisal_status",
                "reviewed_by_user",
                "reviewed_at",
                "review_comments",
                "last_review_decision",
            )
        )
        review_decision = AppraisalReviewDecision.objects.create(
            loan_appraisal_note=note,
            decision=decision,
            review_comments=comments.strip(),
            reviewer_user=actor,
            decided_at=now,
            from_state=from_state,
            to_state=note.appraisal_status,
        )
        request_meta = normalize_request_meta(request_meta)
        action = f"appraisal.{decision}"
        AuditLog.objects.create(
            actor_user=actor,
            action=action,
            entity_type="loan_appraisal_note",
            entity_id=note.pk,
            old_value_json={"appraisal_status": from_state},
            new_value_json={
                "loan_appraisal_note_id": str(note.pk),
                "loan_application_id": str(note.loan_application_id),
                "appraisal_status": note.appraisal_status,
                "decision": decision,
                "appraisal_review_decision_id": str(review_decision.pk),
                "reviewed_by_user_id": str(actor.pk),
                "reviewed_at": timezone.localtime(now).isoformat(),
                "request_id": request_meta.request_id,
                **(
                    {
                        "rejection_note_id": rejection_note.snapshot[
                            "rejection_note_id"
                        ],
                        "rejection_reason_category": (
                            rejection_note.snapshot["rejection_reason_category"]
                        ),
                        "rejection_note_status": rejection_note.snapshot["note_status"],
                    }
                    if rejection_note is not None
                    else {}
                ),
            },
            ip_address=request_meta.ip_address,
            user_agent=request_meta.user_agent,
        )
        record_workflow_event(
            actor=actor,
            workflow_name="appraisal_note",
            entity_type="loan_appraisal_note",
            entity_id=note.pk,
            from_state=from_state,
            to_state=note.appraisal_status,
            trigger_reason=(
                f"Appraisal review decision {review_decision.pk} recorded as {decision}."
            ),
            action_code=action,
            metadata={"appraisal_review_decision_id": str(review_decision.pk)},
        )
        snapshot = appraisal_note_snapshot(note)
        if rejection_note is not None:
            snapshot["rejection_note"] = rejection_note.snapshot
        return _result_with_actions(note, actor, permissions, snapshot)

    def prepare_sanction_handoff(
        self,
        *,
        actor,
        application_id,
        payload,
        actor_permissions=None,
    ):
        permissions = require_permission(
            actor,
            APPRAISAL_SANCTION_SUBMIT_PERMISSION,
            "You do not have permission to submit appraisals for sanction.",
            actor_permissions,
        )
        if "credit_manager" not in actor.role_codes():
            raise CreditModulePermissionDenied(
                "Only an active Credit Manager may submit appraisals for sanction."
            )
        unknown = sorted(set(payload) - {"remarks"})
        errors = {field: "Unknown field." for field in unknown}
        if not isinstance(payload.get("remarks"), str) or not payload["remarks"].strip():
            errors["remarks"] = "This field must not be blank."
        if errors:
            raise CreditModuleValidationError(errors)

        application = (
            LoanApplication.objects.select_for_update(of=("self",))
            .select_related("created_by_user", "received_by_user")
            .filter(loan_application_id=application_id)
            .first()
        )
        if application is None:
            raise CreditModuleNotFound("Loan application was not found.")
        require_application_access(
            application,
            actor,
            APPRAISAL_SANCTION_SUBMIT_PERMISSION,
            permissions,
        )
        note = (
            LoanAppraisalNote.objects.select_for_update(
                of=("self", "risk_assessment")
            ).select_related(
                "risk_assessment",
                "prepared_by_user",
                "reviewed_by_user",
            )
            .filter(loan_application=application)
            .first()
        )
        if note is None:
            raise CreditModuleInvalidStateError(
                "A reviewed appraisal note is required for sanction submission."
            )
        history = list(
            note.review_decisions.select_for_update(of=("self",))
            .select_related("reviewer_user")
            .order_by("decided_at", "appraisal_review_decision_id")
        )
        transition = evaluate_sanction_submission(
            note,
            latest_review=history[-1] if history else None,
            history_locked=True,
        )
        if not transition.allowed:
            raise CreditModuleInvalidStateError(transition.reason)
        latest_review = history[-1]

        exception_required = (
            note.loan_limit_snapshot_json.get("exception_required_flag") is True
        )
        previous_application_status = application.application_status
        previous_appraisal_status = note.appraisal_status
        return ReviewedAppraisalHandoff(
            application=application,
            appraisal_note=note,
            latest_review=latest_review,
            previous_application_status=previous_application_status,
            previous_appraisal_status=previous_appraisal_status,
            exception_required_flag=exception_required,
        )

    def prepare_approval_case_enrichment(self, *, application_id):
        """Lock and project the reviewed credit facts consumed by approvals."""
        application = (
            LoanApplication.objects.select_for_update(of=("self",))
            .filter(loan_application_id=application_id)
            .first()
        )
        if application is None:
            raise CreditModuleNotFound("Loan application was not found.")
        note = (
            LoanAppraisalNote.objects.select_for_update(of=("self",))
            .filter(loan_application=application)
            .first()
        )
        if note is None:
            raise CreditModuleInvalidStateError(
                "A submitted reviewed appraisal is required for approval routing."
            )
        history = list(
            note.review_decisions.select_for_update(of=("self",)).order_by(
                "decided_at", "appraisal_review_decision_id"
            )
        )
        latest_review = history[-1] if history else None
        if (
            application.application_status
            != LoanApplication.STATUS_SUBMITTED_TO_SANCTION
            or note.appraisal_status != LoanAppraisalNote.STATUS_SUBMITTED_TO_SANCTION
            or latest_review is None
            or latest_review.decision != "reviewed"
            or note.last_review_decision != "reviewed"
            or note.reviewed_at != latest_review.decided_at
            or note.reviewed_by_user_id != latest_review.reviewer_user_id
        ):
            raise CreditModuleInvalidStateError(
                "The submitted appraisal no longer matches its reviewed decision."
            )
        snapshot = note.loan_limit_snapshot_json
        required = (
            "loan_limit_assessment_id",
            "loan_application_id",
            "final_eligible_loan_amount",
            "exception_required_flag",
            "calculation_rule_version",
            "policy_config_id",
            "policy_name",
            "calculated_at",
        )
        valid = (
            note.prerequisite_provenance == "verified"
            and all(snapshot.get(key) not in (None, "") for key in required)
            and str(snapshot.get("loan_limit_assessment_id"))
            == str(note.loan_limit_assessment_id_snapshot)
            and str(snapshot.get("loan_application_id")) == str(application.pk)
            and isinstance(snapshot.get("exception_required_flag"), bool)
        )
        try:
            calculated_at = timezone.datetime.fromisoformat(
                str(snapshot.get("calculated_at", "")).replace("Z", "+00:00")
            )
            final_eligible_amount = Decimal(
                str(snapshot.get("final_eligible_loan_amount", ""))
            )
            valid = (
                valid
                and calculated_at <= latest_review.decided_at
                and final_eligible_amount >= Decimal("0.00")
            )
        except (InvalidOperation, TypeError, ValueError):
            valid = False
        if not valid:
            raise CreditModuleInvalidStateError(
                "The stored loan-limit assessment is missing, stale, or lacks policy provenance."
            )
        if snapshot["exception_required_flag"] != (
            note.recommended_amount > final_eligible_amount
        ):
            raise CreditModuleInvalidStateError(
                "The frozen loan-limit exception flag contradicts the reviewed amount."
            )
        return ApprovalCaseEnrichmentFacts(
            application=application,
            appraisal_note=note,
            latest_review=latest_review,
            decision_date=timezone.localdate(latest_review.decided_at),
            recommended_amount=note.recommended_amount,
            exception_required_flag=snapshot["exception_required_flag"],
            loan_limit_provenance={key: snapshot[key] for key in required},
            review_facts=project_approval_case_review_facts(
                application=application,
                appraisal_note=note,
                review=latest_review,
            ),
        )


def _lock_appraisal_after_application(appraisal_id):
    application_id = (
        LoanAppraisalNote.objects.filter(loan_appraisal_note_id=appraisal_id)
        .values_list("loan_application_id", flat=True)
        .first()
    )
    if application_id is None:
        raise CreditModuleNotFound("Appraisal note was not found.")
    application = (
        LoanApplication.objects.select_for_update(of=("self",))
        .select_related("created_by_user", "received_by_user")
        .filter(loan_application_id=application_id)
        .first()
    )
    if application is None:
        raise CreditModuleNotFound("Appraisal note was not found.")
    note = (
        LoanAppraisalNote.objects.select_for_update(of=("self",))
        .select_related(
            "loan_application__created_by_user",
            "loan_application__received_by_user",
            "risk_assessment",
            "prepared_by_user",
            "reviewed_by_user",
        )
        .filter(
            loan_appraisal_note_id=appraisal_id,
            loan_application=application,
        )
        .first()
    )
    if note is None:
        raise CreditModuleNotFound("Appraisal note was not found.")
    return note


def appraisal_note_snapshot(note):
    risk = note.risk_assessment
    review_history = [
        {
            "appraisal_review_decision_id": str(item.pk),
            "decision": item.decision,
            "review_comments": item.review_comments,
            "reviewer": {
                "user_id": str(item.reviewer_user_id),
                "full_name": item.reviewer_user.full_name,
            },
            "decided_at": timezone.localtime(item.decided_at).isoformat(),
            "from_state": item.from_state,
            "to_state": item.to_state,
            "history_provenance": item.history_provenance,
        }
        for item in note.review_decisions.select_related("reviewer_user").all()
    ]
    return {
        "loan_appraisal_note_id": str(note.pk),
        "loan_application_id": str(note.loan_application_id),
        "eligibility_assessment_id": str(note.eligibility_assessment_id_snapshot),
        "loan_limit_assessment_id": str(note.loan_limit_assessment_id_snapshot),
        "eligibility_snapshot": note.eligibility_snapshot_json,
        "loan_limit_snapshot": note.loan_limit_snapshot_json,
        "prerequisite_provenance": note.prerequisite_provenance,
        "prepared_by": {
            "user_id": str(note.prepared_by_user_id),
            "full_name": note.prepared_by_user.full_name,
        },
        "prepared_at": timezone.localtime(note.prepared_at).isoformat(),
        "reviewed_by": (
            {
                "user_id": str(note.reviewed_by_user_id),
                "full_name": note.reviewed_by_user.full_name,
            }
            if note.reviewed_by_user_id
            else None
        ),
        "reviewed_at": (
            timezone.localtime(note.reviewed_at).isoformat()
            if note.reviewed_at
            else None
        ),
        "decision": note.last_review_decision or None,
        "review_comments": note.review_comments or None,
        "review_history": review_history,
        "tat_due_at": timezone.localtime(note.tat_due_at).isoformat(),
        "tat_status": note.tat_status,
        "borrower_summary": note.borrower_summary,
        "eligibility_summary": note.eligibility_summary,
        "loan_limit_summary": note.loan_limit_summary,
        "recommended_amount": f"{note.recommended_amount:.2f}",
        "recommended_tenure_months": note.recommended_tenure_months,
        "recommended_interest_type": note.recommended_interest_type or None,
        "recommended_security_summary": note.recommended_security_summary,
        "repayment_capacity_notes": note.repayment_capacity_notes,
        "risk_assessment": {
            "risk_assessment_id": str(risk.pk),
            "market_risk_rating": risk.market_risk_rating,
            "operational_risk_rating": risk.operational_risk_rating,
            "borrower_risk_rating": risk.borrower_risk_rating,
            "overall_risk_rating": risk.overall_risk_rating,
            "risk_mitigation_notes": risk.risk_mitigation_notes,
            "assessed_by_user_id": str(risk.assessed_by_user_id),
            "assessed_at": timezone.localtime(risk.assessed_at).isoformat(),
        },
        "recommendation": note.recommendation,
        "appraisal_status": note.appraisal_status,
    }


def _tat_status(at, due_at):
    return LoanAppraisalNote.TAT_WITHIN if at <= due_at else LoanAppraisalNote.TAT_BREACHED


def _require_complete_frozen_prerequisites(note):
    if not _frozen_prerequisites_complete(note):
        raise CreditModuleInvalidStateError(
            "Sanction submission requires complete frozen eligibility and loan-limit snapshots."
        )


def _frozen_prerequisites_complete(note):
    eligibility = note.eligibility_snapshot_json
    loan_limit = note.loan_limit_snapshot_json
    consistent = (
        isinstance(eligibility, dict)
        and isinstance(loan_limit, dict)
        and eligibility.get("eligibility_assessment_id")
        == str(note.eligibility_assessment_id_snapshot)
        and eligibility.get("loan_application_id") == str(note.loan_application_id)
        and eligibility.get("overall_result") == "eligible"
        and loan_limit.get("loan_limit_assessment_id")
        == str(note.loan_limit_assessment_id_snapshot)
        and loan_limit.get("loan_application_id") == str(note.loan_application_id)
        and isinstance(loan_limit.get("exception_required_flag"), bool)
    )
    return consistent


def _latest_review_matches_note(note, latest_review):
    return (
        note.last_review_decision == "reviewed"
        and note.reviewed_by_user_id is not None
        and note.reviewed_at is not None
        and bool(note.review_comments.strip())
        and latest_review.decision == note.last_review_decision
        and latest_review.reviewer_user_id == note.reviewed_by_user_id
        and latest_review.decided_at == note.reviewed_at
        and latest_review.review_comments == note.review_comments
        and latest_review.to_state == LoanAppraisalNote.STATUS_REVIEWED
        and latest_review.history_provenance
        in {
            AppraisalReviewDecision.PROVENANCE_NATIVE,
            AppraisalReviewDecision.PROVENANCE_LEGACY_LATEST_ONLY,
        }
    )


def _submission_errors(note):
    errors = {}
    for field in (
        "borrower_summary",
        "eligibility_summary",
        "loan_limit_summary",
        "recommended_security_summary",
        "repayment_capacity_notes",
    ):
        if not getattr(note, field).strip():
            errors[field] = "This field must not be blank."
    if note.recommended_amount <= 0:
        errors["recommended_amount"] = "Must be greater than zero."
    if note.recommended_tenure_months is not None and note.recommended_tenure_months <= 0:
        errors["recommended_tenure_months"] = "Must be a positive integer."
    if note.recommended_interest_type and note.recommended_interest_type != "floating":
        errors["recommended_interest_type"] = "Must be floating when supplied."
    if note.recommendation not in {"approve", "reject", "conditions"}:
        errors["recommendation"] = "Must be approve, reject, or conditions."
    for field in (
        "market_risk_rating",
        "operational_risk_rating",
        "borrower_risk_rating",
        "overall_risk_rating",
    ):
        if getattr(note.risk_assessment, field) not in {"low", "medium", "high"}:
            errors[f"risk_assessment.{field}"] = "Must be low, medium, or high."
    return errors


def _clean_payload(payload, *, partial):
    payload = dict(payload)
    allowed = {
        "borrower_summary",
        "eligibility_summary",
        "loan_limit_summary",
        "recommended_amount",
        "recommended_tenure_months",
        "recommended_interest_type",
        "recommended_security_summary",
        "repayment_capacity_notes",
        "risk_assessment",
        "recommendation",
    }
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise CreditModuleValidationError(
            {field: "Unknown field." for field in unknown}
        )
    required_summaries = {
        "borrower_summary",
        "eligibility_summary",
        "loan_limit_summary",
        "recommended_security_summary",
        "repayment_capacity_notes",
    }
    errors = {}
    for field in required_summaries:
        if field not in payload:
            if not partial:
                errors[field] = "This field is required."
        elif not isinstance(payload[field], str) or not payload[field].strip():
            errors[field] = "This field must not be blank."
    if "recommendation" not in payload:
        if not partial:
            errors["recommendation"] = "This field is required."
    elif payload["recommendation"] not in {"approve", "reject", "conditions"}:
        errors["recommendation"] = "Must be approve, reject, or conditions."
    if "recommended_amount" not in payload:
        if not partial:
            errors["recommended_amount"] = "This field is required."
    else:
        try:
            amount = Decimal(str(payload["recommended_amount"]))
        except (InvalidOperation, TypeError, ValueError):
            errors["recommended_amount"] = "Must be a valid amount."
        else:
            if not amount.is_finite() or amount <= 0:
                errors["recommended_amount"] = "Must be greater than zero."
            else:
                payload["recommended_amount"] = amount
    if "recommended_tenure_months" in payload:
        tenure = payload["recommended_tenure_months"]
        if isinstance(tenure, bool) or not isinstance(tenure, int) or tenure <= 0:
            errors["recommended_tenure_months"] = "Must be a positive integer."
    if "recommended_interest_type" in payload and payload["recommended_interest_type"] != "floating":
        errors["recommended_interest_type"] = "Must be floating when supplied."
    if "risk_assessment" not in payload:
        if not partial:
            errors["risk_assessment"] = "This field is required."
    elif not isinstance(payload["risk_assessment"], dict):
        errors["risk_assessment"] = "Must be an object."
    else:
        risk = payload["risk_assessment"]
        allowed_risk = {
            "market_risk_rating",
            "operational_risk_rating",
            "borrower_risk_rating",
            "overall_risk_rating",
            "risk_mitigation_notes",
        }
        for field in sorted(set(risk) - allowed_risk):
            errors[f"risk_assessment.{field}"] = "Unknown field."
        for field in (
            "market_risk_rating",
            "operational_risk_rating",
            "borrower_risk_rating",
            "overall_risk_rating",
        ):
            if field not in risk:
                if not partial:
                    errors[f"risk_assessment.{field}"] = "This field is required."
            elif risk[field] not in {"low", "medium", "high"}:
                errors[f"risk_assessment.{field}"] = "Must be low, medium, or high."
        if "risk_mitigation_notes" in risk and not isinstance(
            risk["risk_mitigation_notes"], str
        ):
            errors["risk_assessment.risk_mitigation_notes"] = "Must be text."
    if errors:
        raise CreditModuleValidationError(errors)
    return payload
