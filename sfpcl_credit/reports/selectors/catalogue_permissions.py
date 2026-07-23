from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.reports.errors import ReportPermissionDenied


def require_permission(*, actor, permission):
    if (
        not actor.can_authenticate()
        or permission not in auth_service.effective_permission_codes(actor)
    ):
        raise ReportPermissionDenied
