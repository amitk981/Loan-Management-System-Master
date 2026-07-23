from sfpcl_credit.domain_errors import DomainPermissionDenied
from sfpcl_credit.reports.errors import ReportPermissionDenied, ReportValidation
from sfpcl_credit.reports.pagination import paginate
from sfpcl_credit.reports.query import reject_unknown
from sfpcl_credit.reports.selectors.catalogue_permissions import require_permission
from sfpcl_credit.sap_workflow.models import SapCustomerProfileRequest
from sfpcl_credit.sap_workflow.modules.sap_customer_profile import (
    assigned_workspace_rows,
)


PERMISSION = "finance.sap_code.read"
PENDING_STATUSES = {
    SapCustomerProfileRequest.STATUS_DRAFT,
    SapCustomerProfileRequest.STATUS_SENT,
}


def select(*, actor, query_params):
    reject_unknown(
        query_params,
        {"request_status", "page", "page_size"},
    )
    require_permission(actor=actor, permission=PERMISSION)
    status = query_params.get("request_status")
    if status and status not in PENDING_STATUSES:
        raise ReportValidation(
            {"request_status": "Use draft or sent for the pending report."}
        )
    try:
        owner_rows = assigned_workspace_rows(actor=actor)
    except DomainPermissionDenied as exc:
        raise ReportPermissionDenied from exc
    rows = [
        row
        for row in owner_rows
        if row["request_status"] in PENDING_STATUSES
        and (not status or row["request_status"] == status)
    ]
    page_rows, pagination = paginate(rows, query_params)
    return list(page_rows), pagination
