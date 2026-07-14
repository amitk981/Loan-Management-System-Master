"""Single retained audit/version/workflow recorder for security instruments."""

from django.utils import timezone

from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.workflows.events import record_workflow_event


_SENSITIVE_PARTS = (
    "aadhaar",
    "bank_account",
    "bo_account",
    "cheque_number",
    "pan_number",
)


def redact_security_evidence(value, key=""):
    if isinstance(value, dict):
        return {
            item_key: redact_security_evidence(item_value, item_key)
            for item_key, item_value in value.items()
        }
    if isinstance(value, list):
        return [redact_security_evidence(item, key) for item in value]
    if any(part in key.lower() for part in _SENSITIVE_PARTS):
        if isinstance(value, str) and "*" in value:
            return value
        return None if value is None else "[REDACTED]"
    return value


def security_context(*, actor, snapshot, metadata):
    return redact_security_evidence(
        {
            **snapshot,
            "actor_role_codes": auth_service.effective_role_codes(actor),
            "actor_team_codes": actor.team_codes(),
            "request_id": metadata.request_id,
            "ip_address": metadata.ip_address,
            "user_agent": metadata.user_agent,
        }
    )


def record_security_evidence(
    *, actor, entity_type, entity_id, action, old, snapshot, metadata,
    workflow_name, from_state, to_state, record_workflow=True, trigger_reason=None,
):
    context = security_context(actor=actor, snapshot=snapshot, metadata=metadata)
    redacted_old = redact_security_evidence(old)
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_value_json=redacted_old,
        new_value_json=context,
        ip_address=metadata.ip_address,
        user_agent=metadata.user_agent,
    )
    VersionHistory.objects.create(
        versioned_entity_type=entity_type,
        versioned_entity_id=entity_id,
        version_number=str(
            VersionHistory.objects.filter(
                versioned_entity_type=entity_type,
                versioned_entity_id=entity_id,
            ).count()
            + 1
        ),
        change_summary=action,
        author_user=actor,
        old_value_json=redacted_old,
        new_value_json=context,
        effective_from=timezone.localdate(),
    )
    if record_workflow:
        return record_workflow_event(
            actor=actor,
            workflow_name=workflow_name,
            entity_type=entity_type,
            entity_id=entity_id,
            from_state=from_state,
            to_state=to_state,
            trigger_reason=trigger_reason or action,
            action_code=action,
            metadata=context,
        )
    return None
