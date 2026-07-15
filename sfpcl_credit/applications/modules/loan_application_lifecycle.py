"""Application-owned workflow transitions used by trusted entry-point coordinators."""

from django.db import transaction
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.workflows.events import record_workflow_event
from sfpcl_credit.workflows.guard import TransitionDefinition, evaluate_transition


PORTAL_RESUBMIT_CAPABILITY = "portal.application.resubmit_own"
_TRANSITIONS = (
    TransitionDefinition(
        entity_type="loan_application",
        action_code="resubmit",
        from_states=frozenset({LoanApplication.STATUS_INCOMPLETE_RETURNED}),
        to_state=LoanApplication.STATUS_SUBMITTED,
        required_permission=PORTAL_RESUBMIT_CAPABILITY,
        audit_action="applications.loan_application.resubmitted",
        workflow_name="loan_application",
        workflow_label="Borrower corrections resubmitted for completeness review.",
    ),
)


@transaction.atomic
def resubmit(*, application_id, actor, portal_scope, request_metadata):
    """Guard and retain the canonical returned-to-review application transition."""
    application = LoanApplication.objects.select_for_update().get(pk=application_id)
    transition = evaluate_transition(
        current_state=application.application_status,
        requested_action="resubmit",
        actor_permissions={PORTAL_RESUBMIT_CAPABILITY},
        transitions=_TRANSITIONS,
    )
    old_value = _snapshot(application)
    now = timezone.now()
    application.application_status = transition.next_state
    application.completeness_status = LoanApplication.COMPLETENESS_NOT_STARTED
    application.current_stage = LoanApplication.STAGE_INITIAL
    application.submitted_at = application.submitted_at or now
    application.updated_by_user = actor
    application.updated_at = now
    application.save()
    new_value = {
        **_snapshot(application),
        **portal_scope,
        "request_id": request_metadata.get("request_id"),
        "outcome": "accepted",
    }
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="portal_account",
        action=transition.definition.audit_action,
        entity_type=transition.definition.entity_type,
        entity_id=application.pk,
        old_value_json=old_value,
        new_value_json=new_value,
        ip_address=request_metadata.get("ip_address"),
        user_agent=request_metadata.get("user_agent", ""),
    )
    record_workflow_event(
        actor=actor,
        workflow_name=transition.definition.workflow_name,
        entity_type=transition.definition.entity_type,
        entity_id=application.pk,
        from_state=transition.previous_state,
        to_state=transition.next_state,
        trigger_reason=transition.definition.workflow_label,
        action_code=transition.definition.action_code,
    )
    return application


def _snapshot(application):
    return {
        "loan_application_id": str(application.pk),
        "application_status": application.application_status,
        "completeness_status": application.completeness_status,
        "current_stage": application.current_stage,
        "submitted_at": (
            application.submitted_at.isoformat().replace("+00:00", "Z")
            if application.submitted_at
            else None
        ),
    }
