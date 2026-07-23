from django.views.decorators.http import require_http_methods

from sfpcl_credit.api import error_response, list_response
from sfpcl_credit.identity.modules import http_auth
from sfpcl_credit.reports.errors import ReportPermissionDenied, ReportValidation
from sfpcl_credit.reports.registry import run_report


@require_http_methods(["GET"])
def report(request, report_code):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        rows, pagination = run_report(
            report_code=report_code,
            actor=actor,
            query_params=request.GET,
        )
        return list_response(rows, pagination, request)
    except ReportValidation as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Report query failed validation.",
            exc.field_errors,
        )
    except ReportPermissionDenied:
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "Report permission and object scope are required.",
        )
