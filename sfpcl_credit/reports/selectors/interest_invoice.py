from sfpcl_credit.interest.modules.interest_engine import (
    InterestInvoicePermissionDenied,
    InterestInvoiceValidation,
    list_invoices,
)
from sfpcl_credit.reports.errors import ReportPermissionDenied, ReportValidation
from sfpcl_credit.reports.selectors.catalogue_permissions import require_permission


PERMISSION = "finance.loan_account.read"


def select(*, actor, query_params):
    require_permission(actor=actor, permission=PERMISSION)
    try:
        return list_invoices(
            actor=actor,
            loan_account_id=None,
            query_params=query_params,
        )
    except InterestInvoiceValidation as exc:
        raise ReportValidation(exc.field_errors) from exc
    except InterestInvoicePermissionDenied as exc:
        raise ReportPermissionDenied from exc
