"""Transactional public boundary for immutable approval-case actions."""

from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.approvals.models import ApprovalAction, ApprovalCase, SanctionDecision
from sfpcl_credit.approvals.modules import approval_case_engine
from sfpcl_credit.credit.modules.appraisal_workflow import AppraisalWorkflow
from sfpcl_credit.communications import services as communication_services
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.workflows.events import record_workflow_event
from sfpcl_credit.workflows.guard import TransitionDefinition, evaluate_transition


@dataclass(frozen=True)
class ApprovalActionConflict(Exception):
    message: str
    code: str = "TRANSITION_CONFLICT"
    status: int = 409
    field_errors: dict | None = None

    def __str__(self):
        return self.message


_ACTION_SPECS = {
    code: TransitionDefinition(
        entity_type="approval_case",
        action_code=code,
        from_states=frozenset({ApprovalCase.STATUS_PENDING}),
        to_state=to_state,
        required_permission=permission,
        audit_action=f"approval_case.{code}",
        workflow_name="sanction_approval",
    )
    for code, to_state, permission in (
        ("approve", ApprovalCase.STATUS_PENDING, "approvals.case.approve"),
        ("reject", ApprovalCase.STATUS_REJECTED, "approvals.case.reject"),
        ("return", ApprovalCase.STATUS_RETURNED, "approvals.case.return"),
    )
}


@transaction.atomic
def approve_case(*, actor, case_id, payload, actor_permissions, request_meta=None):
    return record_action(
        actor=actor, case_id=case_id, action_code="approve", payload=payload,
        actor_permissions=actor_permissions, request_meta=request_meta,
    )


def reject_case(*, actor, case_id, payload, actor_permissions, request_meta=None):
    return record_action(
        actor=actor, case_id=case_id, action_code="reject", payload=payload,
        actor_permissions=actor_permissions, request_meta=request_meta,
    )


def return_case(*, actor, case_id, payload, actor_permissions, request_meta=None):
    return record_action(
        actor=actor, case_id=case_id, action_code="return", payload=payload,
        actor_permissions=actor_permissions, request_meta=request_meta,
    )


@transaction.atomic
def record_action(*, actor, case_id, action_code, payload, actor_permissions, request_meta=None):
    version = _submitted_version(payload)
    comments = _comments(payload, required=action_code in {"reject", "return"})
    identifiers = ApprovalCase.objects.filter(pk=case_id).values(
        "loan_application_id", "loan_appraisal_note_id"
    ).first()
    if identifiers is None:
        raise ApprovalCase.DoesNotExist

    application = LoanApplication.objects.select_for_update().get(
        pk=identifiers["loan_application_id"]
    )
    note = AppraisalWorkflow.lock_submitted_appraisal(
        appraisal_id=identifiers["loan_appraisal_note_id"]
    )
    case = (
        ApprovalCase.objects.select_for_update()
        .select_related("loan_application", "loan_appraisal_note__risk_assessment")
        .prefetch_related("actions")
        .get(pk=case_id)
    )
    if not approval_case_engine.is_routable_approval_case(case):
        raise ApprovalCase.DoesNotExist
    if not approval_case_engine.can_read_approval_case(
        actor=actor, case=case, actor_permissions=actor_permissions
    ).allowed:
        raise ApprovalActionConflict(
            "You cannot access this approval case.",
            code="OBJECT_ACCESS_DENIED",
            status=403,
        )
    if case.version != version:
        raise ApprovalActionConflict("Approval case version is stale.", code="STALE_VERSION")
    availability = approval_case_engine.approval_case_action_availability(
        case=case,
        actor=actor,
        actor_permissions=actor_permissions,
        action_code=action_code,
    )
    if not availability["enabled"]:
        missing_permission = (
            availability["disabled_reason"] == "Required permission is not granted."
        )
        raise ApprovalActionConflict(
            availability["disabled_reason"],
            code="FORBIDDEN" if missing_permission else "TRANSITION_CONFLICT",
            status=403 if missing_permission else 409,
        )

    required_ids = {str(item["user_id"]) for item in case.required_approvers_json}
    approved_ids = {
        str(item.approver_user_id)
        for item in ApprovalAction.objects.filter(
            approval_case=case, decision="approved"
        )
    }
    completes_approval = action_code == "approve" and (
        approved_ids | {str(actor.pk)}
    ) == required_ids
    case_target = {
        "reject": ApprovalCase.STATUS_REJECTED,
        "return": ApprovalCase.STATUS_RETURNED,
    }.get(
        action_code,
        (
            ApprovalCase.STATUS_APPROVED
            if completes_approval
            else ApprovalCase.STATUS_PENDING
        ),
    )
    application_target = {
        "reject": LoanApplication.STATUS_REJECTED_BY_SANCTION,
        "return": LoanApplication.STATUS_APPRAISAL_REVIEWED,
    }.get(
        action_code,
        (
            LoanApplication.STATUS_APPROVED_BY_SANCTION
            if completes_approval
            else LoanApplication.STATUS_SUBMITTED_TO_SANCTION
        ),
    )
    appraisal_target = (
        note.STATUS_REVIEWED if action_code == "return"
        else note.STATUS_SUBMITTED_TO_SANCTION
    )
    case_transition = _guard_transition(
        current_state=case.current_status,
        expected_state=ApprovalCase.STATUS_PENDING,
        target_state=case_target,
        entity_type="approval_case",
        action_code=action_code,
        actor_permissions=actor_permissions,
    )
    application_transition = _guard_transition(
        current_state=application.application_status,
        expected_state=LoanApplication.STATUS_SUBMITTED_TO_SANCTION,
        target_state=application_target,
        entity_type="loan_application",
        action_code=action_code,
        actor_permissions=actor_permissions,
    )
    appraisal_transition = _guard_transition(
        current_state=note.appraisal_status,
        expected_state=note.STATUS_SUBMITTED_TO_SANCTION,
        target_state=appraisal_target,
        entity_type="loan_appraisal_note",
        action_code=action_code,
        actor_permissions=actor_permissions,
    )

    role_code = next(
        item["role_code"]
        for item in case.required_approvers_json
        if str(item["user_id"]) == str(actor.pk)
    )
    request_meta = request_meta or {}
    action = ApprovalAction.objects.create(
        approval_case=case,
        approver_user=actor,
        approver_role_code=role_code,
        decision={"approve": "approved", "reject": "rejected", "return": "returned"}[action_code],
        comments=comments,
        ip_address=request_meta.get("ip_address") or None,
        user_agent=request_meta.get("user_agent") or None,
    )
    previous_status = case.current_status
    decision = None
    if action_code == "reject":
        case.current_status = case_transition.next_state
        case.reason_for_rejection = comments
        case.closed_at = timezone.now()
        application.application_status = application_transition.next_state
        application.save(update_fields=["application_status"])
    elif action_code == "return":
        case.current_status = case_transition.next_state
        case.closed_at = timezone.now()
        application.application_status = application_transition.next_state
        application.save(update_fields=["application_status"])
        note.appraisal_status = appraisal_transition.next_state
        note.save(update_fields=["appraisal_status"])
    elif completes_approval:
        case.current_status = case_transition.next_state
        case.closed_at = timezone.now()
        application.application_status = application_transition.next_state
        application.save(update_fields=["application_status"])
        decision = SanctionDecision.objects.create(
            loan_application=application,
            approval_case=case,
            decision="sanctioned",
            sanctioned_amount=note.recommended_amount,
            sanctioned_tenure_months=note.recommended_tenure_months,
            interest_rate_type=note.recommended_interest_type,
            interest_rate_value=None,
            repayment_date=None,
            penal_interest_rate=None,
            charges_json={},
            security_required_summary=note.recommended_security_summary,
            conditions_precedent="",
            decision_reason=case.reason_for_approval,
        )
    case.version += 1
    case.save(update_fields=["current_status", "reason_for_rejection", "closed_at", "version"])
    AuditLog.objects.create(
        actor_user=actor,
        action="approval_case.action_recorded",
        entity_type="approval_case",
        entity_id=case.pk,
        old_value_json={"current_status": previous_status},
        new_value_json={
            "approval_action_id": str(action.pk),
            "loan_application_id": str(case.loan_application_id),
            "decision": action.decision,
            "comments": action.comments,
            "current_status": case.current_status,
            "sanction_decision_id": str(decision.pk) if decision else None,
            "request_id": request_meta.get("request_id"),
        },
        ip_address=request_meta.get("ip_address", ""),
        user_agent=request_meta.get("user_agent", ""),
    )
    record_workflow_event(
        actor=actor,
        workflow_name="sanction_approval",
        entity_type="approval_case",
        entity_id=case.pk,
        from_state=previous_status,
        to_state=case.current_status,
        trigger_reason=f"Approver {actor.pk} recorded {action.decision}.",
        action_code="approval_case.action_recorded",
    )
    if case.current_status != ApprovalCase.STATUS_PENDING:
        communication_services.create_internal_team_communication(
            sender=actor,
            team_code="credit_assessment",
            related_entity_type="approval_case",
            related_entity_id=case.pk,
            subject="Sanction approval completed",
            body=f"Approval case {case.pk} was {case.current_status}.",
            action_label="Open approval case",
            action_url=f"/sanctions/{case.pk}",
            request_meta=request_meta,
        )
    case = (
        ApprovalCase.objects.select_related(
            "loan_application", "loan_appraisal_note__risk_assessment"
        )
        .prefetch_related("actions")
        .get(pk=case.pk)
    )
    return {
        **approval_case_engine.serialize_case_detail(case, actor, set(actor_permissions)),
        "approval_action_id": str(action.pk),
        "decision": action.decision,
        "approval_case_status": case.current_status,
        "sanction_decision_created": decision is not None,
        "sanction_decision_id": str(decision.pk) if decision else None,
    }


def _guard_transition(
    *, current_state, expected_state, target_state, entity_type, action_code,
    actor_permissions,
):
    permission = _ACTION_SPECS[action_code].required_permission
    definition = TransitionDefinition(
        entity_type=entity_type,
        action_code=action_code,
        from_states=frozenset({expected_state}),
        to_state=target_state,
        required_permission=permission,
        audit_action=f"{entity_type}.{action_code}",
        workflow_name="sanction_approval",
    )
    try:
        return evaluate_transition(
            current_state=current_state,
            requested_action=action_code,
            actor_permissions=actor_permissions,
            transitions=(definition,),
        )
    except Exception as exc:
        from sfpcl_credit.workflows.guard import (
            InvalidStateTransition,
            MissingTransitionPermission,
        )

        if isinstance(exc, MissingTransitionPermission):
            raise ApprovalActionConflict(
                f"You do not have permission to {action_code} this case.",
                code="FORBIDDEN",
                status=403,
            ) from exc
        if isinstance(exc, InvalidStateTransition):
            raise ApprovalActionConflict(
                f"{entity_type.replace('_', ' ').title()} is not in the required state."
            ) from exc
        raise


def _submitted_version(payload):
    unknown = set(payload) - {"version", "comments"}
    errors = {field: "Unknown field." for field in sorted(unknown)}
    version = payload.get("version")
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        errors["version"] = "Must be a positive integer."
    if errors:
        raise ApprovalActionConflict(
            "Approval action failed validation.",
            code="VALIDATION_ERROR",
            status=400,
            field_errors=errors,
        )
    return version


def _comments(payload, *, required):
    comments = payload.get("comments")
    if comments is None and not required:
        return None
    if not isinstance(comments, str):
        raise ApprovalActionConflict(
            "Approval action failed validation.",
            code="VALIDATION_ERROR",
            status=400,
            field_errors={"comments": "Must be a string."},
        )
    cleaned = comments.strip()
    if required and not cleaned:
        raise ApprovalActionConflict(
            "Approval action failed validation.", code="VALIDATION_ERROR", status=400,
            field_errors={"comments": "This field must not be blank."},
        )
    return cleaned or None
