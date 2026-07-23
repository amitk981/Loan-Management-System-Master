from django.core.exceptions import ValidationError

from sfpcl_credit.approvals.modules import exception_register
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.reports.errors import ReportValidation
from sfpcl_credit.reports.selectors.catalogue_permissions import require_permission


PERMISSION = "approvals.exception_register.read"


def select(*, actor, query_params):
    require_permission(actor=actor, permission=PERMISSION)
    try:
        return exception_register.list_entries(
            actor=actor,
            query_params=query_params,
            actor_permissions=set(auth_service.effective_permission_codes(actor)),
        )
    except ValidationError as exc:
        raise ReportValidation(exc.message_dict) from exc
