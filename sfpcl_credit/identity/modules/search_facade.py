"""Audit-owned global-search projection."""

from sfpcl_credit.identity.models import AuditLog


READ_PERMISSION = "audit.audit_log.read"


def matching_audit_logs(*, permissions, entity_ids, limit):
    if READ_PERMISSION not in permissions:
        return []
    return list(
        AuditLog.objects.select_related("actor_user")
        .filter(entity_id__in=entity_ids)
        .order_by("-created_at", "-audit_log_id")[:limit]
    )


__all__ = ["matching_audit_logs"]
