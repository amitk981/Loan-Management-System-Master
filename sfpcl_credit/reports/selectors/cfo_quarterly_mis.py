from sfpcl_credit.monitoring.modules.quarterly_mis import (
    QuarterlyMisPermissionDenied,
    QuarterlyMisValidation,
    list_reports,
)
from sfpcl_credit.reports.errors import ReportPermissionDenied, ReportValidation
from sfpcl_credit.reports.selectors.catalogue_permissions import require_permission


PERMISSION = "finance.loan_account.read"


def select(*, actor, query_params):
    require_permission(actor=actor, permission=PERMISSION)
    try:
        rows, pagination = list_reports(
            actor=actor,
            query_params=query_params,
        )
    except QuarterlyMisValidation as exc:
        raise ReportValidation(exc.field_errors) from exc
    except QuarterlyMisPermissionDenied as exc:
        raise ReportPermissionDenied from exc
    pagination["total_pages"] = max(1, pagination["total_pages"])
    pagination["has_next"] = pagination["page"] < pagination["total_pages"]
    pagination["has_previous"] = pagination["page"] > 1
    return rows, pagination
