from django.core.exceptions import ValidationError

from sfpcl_credit.identity.modules import audit_log, auth_service
from sfpcl_credit.reports.errors import ReportPermissionDenied, ReportValidation


EXPORT_PERMISSION = "audit.export"


def select(*, actor, query_params):
    permissions = set(auth_service.effective_permission_codes(actor))
    if (
        not actor.can_authenticate()
        or not audit_log.user_can_read_audit_logs(actor)
        or EXPORT_PERMISSION not in permissions
    ):
        raise ReportPermissionDenied
    try:
        return audit_log.paginated_audit_logs(
            actor=actor,
            query_params=query_params,
        )
    except ValidationError as exc:
        raise ReportValidation(audit_log.validation_field_errors(exc)) from exc


__all__ = ["select"]
