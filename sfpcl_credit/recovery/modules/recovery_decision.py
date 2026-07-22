import uuid

from django.db import transaction
from django.utils import timezone

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.approvals.models import ApprovalAction, ApprovalCase
from sfpcl_credit.approvals.modules.conflict_of_interest import ConflictOfInterestModule
from sfpcl_credit.defaults.models import DefaultCase, NonPaymentNote
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.recovery.models import RecoveryDecision
from sfpcl_credit.workflows.events import record_workflow_event


CREATE_PERMISSION = "recovery.decision.create"
EXECUTABLE_ACTIONS = {"invoke_sh4", "invoke_cdsl", "present_blank_dated_cheque"}


class RecoveryDecisionValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


class RecoveryDecisionPermissionDenied(Exception):
    pass


class RecoveryDecisionNotFound(Exception):
    pass


class RecoveryDecisionConflict(Exception):
    pass


def create_recovery_decision(*, actor, default_case_id, payload, request=None):
    _require_permission(actor)
    cleaned = _validate_payload(payload)
    with transaction.atomic():
        default_case = (
            DefaultCase.objects.select_for_update(of=("self",))
            .filter(pk=default_case_id)
            .first()
        )
        if default_case is None:
            raise RecoveryDecisionNotFound
        existing = RecoveryDecision.objects.filter(default_case=default_case).first()
        if existing is not None:
            if _replay_matches(existing, cleaned):
                return existing
            raise RecoveryDecisionConflict(
                "The default case already has a different frozen recovery decision."
            )
        note = (
            NonPaymentNote.objects.select_for_update(of=("self",))
            .filter(default_case=default_case)
            .first()
        )
        case = (
            ApprovalCase.objects.select_for_update(of=("self",))
            .select_related("approval_matrix_rule")
            .prefetch_related("actions")
            .filter(pk=cleaned["approval_case_id"])
            .first()
        )
        if note is None or case is None:
            raise RecoveryDecisionNotFound
        authority_action, evidence = _validated_approval_evidence(
            actor=actor,
            default_case=default_case,
            note=note,
            case=case,
            decision=cleaned["decision"],
        )
        decided_at = timezone.now()
        decision = RecoveryDecision(
            default_case=default_case,
            non_payment_note=note,
            approval_case=case,
            decision=cleaned["decision"],
            decision_reason=cleaned["decision_reason"],
            status=RecoveryDecision.STATUS_APPROVED,
            approval_evidence_json=evidence,
            decided_by_user=actor,
            decided_by_role_code=authority_action.approver_role_code,
            decided_at=decided_at,
        )
        event = record_workflow_event(
            actor=actor,
            workflow_name="recovery_decision",
            entity_type="recovery_decision",
            entity_id=decision.pk,
            from_state="recovery_decision_pending",
            to_state="recovery_approved",
            trigger_reason=cleaned["decision_reason"],
            action_code="recovery_decision.created",
            metadata={"approval_case_id": str(case.pk)},
        )
        decision.workflow_event = event
        decision.save(force_insert=True)
        old_status = default_case.default_case_status
        default_case.default_case_status = "recovery_approved"
        default_case.save(update_fields=["default_case_status"])
        AuditLog.objects.create(
            actor_user=actor,
            action="recovery_decision.created",
            entity_type="recovery_decision",
            entity_id=decision.pk,
            old_value_json={
                "default_case_status": old_status,
                "approval_case_id": str(case.pk),
            },
            new_value_json={
                **serialize_recovery_decision(decision),
                "workflow_event_id": str(event.pk),
            },
            ip_address=request_ip(request) if request is not None else "",
            user_agent=request_user_agent(request) if request is not None else "",
        )
        return decision


def serialize_recovery_decision(decision, *, actor=None):
    available_actions = []
    if (
        decision.status == RecoveryDecision.STATUS_APPROVED
        and decision.decision in EXECUTABLE_ACTIONS
        and actor is not None
        and "recovery.action.initiate"
        in auth_service.effective_permission_codes(actor)
        and "company_secretary" in auth_service.effective_role_codes(actor)
    ):
        available_actions.append(
            {
                "action_code": "execute_recovery",
                "action_type": decision.decision,
                "required_permission": "recovery.action.initiate",
            }
        )
    return {
        "recovery_decision_id": str(decision.pk),
        "default_case_id": str(decision.default_case_id),
        "non_payment_note_id": str(decision.non_payment_note_id),
        "approval_case_id": str(decision.approval_case_id),
        "decision": decision.decision,
        "decision_reason": decision.decision_reason,
        "status": decision.status,
        "approval_evidence": dict(decision.approval_evidence_json),
        "decided_by_user_id": str(decision.decided_by_user_id),
        "decided_by_role_code": decision.decided_by_role_code,
        "decided_at": decision.decided_at.isoformat().replace("+00:00", "Z"),
        "available_actions": available_actions,
    }


def api_create_recovery_decision(*, actor, default_case_id, payload, request=None):
    return serialize_recovery_decision(
        create_recovery_decision(
            actor=actor,
            default_case_id=default_case_id,
            payload=payload,
            request=request,
        ),
        actor=actor,
    )


def _require_permission(actor):
    if (
        not actor.can_authenticate()
        or CREATE_PERMISSION not in auth_service.effective_permission_codes(actor)
    ):
        raise RecoveryDecisionPermissionDenied


def _validate_payload(payload):
    allowed = {"approval_case_id", "decision", "decision_reason"}
    errors = {
        field: "Unknown request field." for field in sorted(set(payload) - allowed)
    }
    cleaned = {}
    try:
        cleaned["approval_case_id"] = uuid.UUID(str(payload.get("approval_case_id")))
    except (TypeError, ValueError, AttributeError):
        errors["approval_case_id"] = "Must be a valid UUID."
    for field, maximum in (("decision", 100), ("decision_reason", 5000)):
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            errors[field] = "This field is required."
        elif len(value.strip()) > maximum:
            errors[field] = f"Must be at most {maximum} characters."
        else:
            cleaned[field] = value.strip()
    if errors:
        raise RecoveryDecisionValidation(errors)
    return cleaned


def _validated_approval_evidence(*, actor, default_case, note, case, decision):
    matrix = (
        case.matrix_projection_json
        if isinstance(case.matrix_projection_json, dict)
        else {}
    )
    if (
        default_case.default_case_status != "recovery_decision_pending"
        or note.status != NonPaymentNote.STATUS_SUBMITTED
        or note.approval_case_id != case.pk
        or case.approval_type != ApprovalCase.TYPE_RECOVERY
        or case.related_entity_type != "non_payment_note"
        or case.related_entity_id != note.pk
        or case.current_status != ApprovalCase.STATUS_APPROVED
        or case.closed_at is None
        or case.decision_date is None
        or case.approval_matrix_rule_id is None
        or case.approval_matrix_rule_version != case.approval_matrix_rule.version_number
        or case.approval_matrix_rule.decision_type != ApprovalCase.TYPE_RECOVERY
        or case.approval_matrix_rule.condition_code != decision
        or matrix.get("approval_matrix_rule_id") != str(case.approval_matrix_rule_id)
        or matrix.get("version_number") != case.approval_matrix_rule_version
        or matrix.get("decision_type") != ApprovalCase.TYPE_RECOVERY
        or matrix.get("condition_code") != decision
        or matrix.get("decision_date") != case.decision_date.isoformat()
        or matrix.get("joint_approval_required") is not True
        or case.reason_for_approval != decision
        or note.recommended_recovery_action != decision
    ):
        raise RecoveryDecisionConflict(
            "The approval case is not a matching terminal approval for this recovery action."
        )
    effective = ConflictOfInterestModule.effective_approvers(case)
    required_ids = [str(item["user_id"]) for item in effective]
    if not required_ids or len(required_ids) != len(set(required_ids)):
        raise RecoveryDecisionConflict(
            "The approval case does not retain distinct required authority."
        )
    actions = list(case.actions.all())
    approved = [action for action in actions if action.decision == "approved"]
    approved_ids = {str(action.approver_user_id) for action in approved}
    required_roles = {
        str(item["user_id"]): item["role_code"] for item in effective
    }
    if (
        len(effective) != len(case.required_approvers_json)
        or approved_ids != set(required_ids)
        or len(approved) != len(required_ids)
        or any(action.decision != "approved" for action in actions)
        or any(
            action.approver_role_code
            != required_roles.get(str(action.approver_user_id))
            for action in approved
        )
        or any(
            action.acted_at < case.submitted_at or action.acted_at > case.closed_at
            for action in approved
        )
    ):
        raise RecoveryDecisionConflict(
            "The approval case lacks complete, conflict-free authority evidence."
        )
    authority_action = next(
        (action for action in approved if action.approver_user_id == actor.pk), None
    )
    if authority_action is None:
        raise RecoveryDecisionPermissionDenied
    return authority_action, {
        "approval_case_id": str(case.pk),
        "approval_case_status": case.current_status,
        "approval_matrix_rule_id": str(case.approval_matrix_rule_id),
        "approval_matrix_rule_version": case.approval_matrix_rule_version,
        "approved_action": decision,
        "required_approvers": list(case.required_approvers_json),
        "approval_actions": [
            {
                "approval_action_id": str(action.pk),
                "approver_user_id": str(action.approver_user_id),
                "approver_role_code": action.approver_role_code,
                "approver_display_name": action.approver_display_name,
                "decision": action.decision,
                "acted_at": action.acted_at.isoformat().replace("+00:00", "Z"),
            }
            for action in approved
        ],
        "closed_at": case.closed_at.isoformat().replace("+00:00", "Z"),
    }


def _replay_matches(existing, cleaned):
    return (
        existing.approval_case_id == cleaned["approval_case_id"]
        and existing.decision == cleaned["decision"]
        and existing.decision_reason == cleaned["decision_reason"]
    )
