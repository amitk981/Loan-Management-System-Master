from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods

from sfpcl_credit.api import error_response, list_response, parse_json_body, success_response
from sfpcl_credit.identity.modules import http_auth
from sfpcl_credit.monitoring.modules.dpd_monitoring import (
    DpdConflict,
    DpdNotFound,
    DpdPermissionDenied,
    DpdValidation,
    calculate_for_loan,
    calculate_portfolio,
    current_portfolio_projection,
    get_current_for_loan,
)
from sfpcl_credit.monitoring.modules.reminder_engine import (
    ReminderConflict,
    ReminderEngine,
    ReminderNotFound,
    ReminderPermissionDenied,
    ReminderValidation,
)
from sfpcl_credit.monitoring.modules.quarterly_mis import (
    QuarterlyMisConflict,
    QuarterlyMisNotFound,
    QuarterlyMisPermissionDenied,
    QuarterlyMisValidation,
    generate as generate_quarterly_mis,
    get_report as get_quarterly_mis,
    drill_down as quarterly_mis_drill_down_rows,
    submit_to_cfo,
    mark_reviewed,
    export_report,
    list_reports,
)


@require_http_methods(["POST"])
def quarterly_mis_generate(request):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            generate_quarterly_mis(
                actor=actor,
                payload=parse_json_body(request),
                idempotency_key=request.headers.get("Idempotency-Key", ""),
                request=request,
            ),
            request,
        )
    except (QuarterlyMisValidation, ValidationError) as exc:
        fields = exc.field_errors if isinstance(exc, QuarterlyMisValidation) else {"body": exc.messages[0]}
        return error_response(
            request, 400, "VALIDATION_ERROR", "Quarterly MIS generation failed validation.", fields
        )
    except QuarterlyMisPermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "MIS generation permission and portfolio scope are required."
        )
    except QuarterlyMisConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["GET"])
def quarterly_mis_detail(request, report_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(get_quarterly_mis(actor=actor, report_id=report_id), request)
    except QuarterlyMisPermissionDenied:
        return error_response(request, 403, "FORBIDDEN", "Portfolio read permission is required.")
    except QuarterlyMisNotFound:
        return error_response(request, 404, "NOT_FOUND", "The report was not found or is inaccessible.")


@require_http_methods(["GET"])
def quarterly_mis_drill_down(request, report_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        rows, pagination = quarterly_mis_drill_down_rows(
            actor=actor, report_id=report_id, query_params=request.GET
        )
        return list_response(rows, pagination, request)
    except QuarterlyMisValidation as exc:
        return error_response(request, 400, "VALIDATION_ERROR", "Invalid drill-down query.", exc.field_errors)
    except QuarterlyMisPermissionDenied:
        return error_response(request, 403, "FORBIDDEN", "Portfolio read permission is required.")
    except QuarterlyMisNotFound:
        return error_response(request, 404, "NOT_FOUND", "The report was not found or is inaccessible.")


def _quarterly_mis_transition(request, report_id, operation):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            operation(
                actor=actor,
                report_id=report_id,
                payload=parse_json_body(request),
                idempotency_key=request.headers.get("Idempotency-Key", ""),
                request=request,
            ),
            request,
        )
    except (QuarterlyMisValidation, ValidationError) as exc:
        fields = exc.field_errors if isinstance(exc, QuarterlyMisValidation) else {"body": exc.messages[0]}
        return error_response(request, 400, "VALIDATION_ERROR", "MIS transition failed validation.", fields)
    except QuarterlyMisPermissionDenied:
        return error_response(request, 403, "FORBIDDEN", "The exact MIS transition permission and scope are required.")
    except QuarterlyMisNotFound:
        return error_response(request, 404, "NOT_FOUND", "The report was not found or is inaccessible.")
    except QuarterlyMisConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["POST"])
def quarterly_mis_submit(request, report_id):
    return _quarterly_mis_transition(request, report_id, submit_to_cfo)


@require_http_methods(["POST"])
def quarterly_mis_review(request, report_id):
    return _quarterly_mis_transition(request, report_id, mark_reviewed)


@require_http_methods(["GET"])
def quarterly_mis_export(request, report_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            export_report(
                actor=actor,
                report_id=report_id,
                query_params=request.GET,
                request=request,
            ),
            request,
        )
    except QuarterlyMisValidation as exc:
        return error_response(request, 400, "VALIDATION_ERROR", "Invalid export query.", exc.field_errors)
    except QuarterlyMisPermissionDenied:
        return error_response(request, 403, "FORBIDDEN", "Report export permission and scope are required.")
    except QuarterlyMisNotFound:
        return error_response(request, 404, "NOT_FOUND", "The report was not found or is inaccessible.")
    except QuarterlyMisConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["GET"])
def quarterly_mis_collection(request):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        rows, pagination = list_reports(actor=actor, query_params=request.GET)
        return list_response(rows, pagination, request)
    except QuarterlyMisValidation as exc:
        return error_response(request, 400, "VALIDATION_ERROR", "Invalid MIS report query.", exc.field_errors)
    except QuarterlyMisPermissionDenied:
        return error_response(request, 403, "FORBIDDEN", "Portfolio read permission is required.")


@require_http_methods(["GET"])
def dpd_status(request, loan_account_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            get_current_for_loan(actor=actor, loan_account_id=loan_account_id), request
        )
    except DpdPermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "DPD read permission and loan scope are required."
        )
    except DpdNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "The DPD status was not found or is inaccessible."
        )


@require_http_methods(["GET"])
def dpd_portfolio(request):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(current_portfolio_projection(actor=actor), request)
    except DpdPermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "DPD read permission and loan scope are required."
        )


@require_http_methods(["POST"])
def dpd_calculate(request, loan_account_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            calculate_for_loan(
                actor=actor,
                loan_account_id=loan_account_id,
                payload=parse_json_body(request),
                request=request,
            ),
            request,
        )
    except (DpdValidation, ValidationError) as exc:
        fields = exc.field_errors if isinstance(exc, DpdValidation) else {"body": exc.messages[0]}
        return error_response(
            request, 400, "VALIDATION_ERROR", "DPD calculation failed validation.", fields
        )
    except DpdPermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "DPD calculation permission and loan scope are required."
        )
    except DpdNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "The loan account was not found or is inaccessible."
        )
    except DpdConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["POST"])
def dpd_bulk_calculate(request):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            calculate_portfolio(
                actor=actor,
                payload=parse_json_body(request),
                request=request,
            ),
            request,
        )
    except (DpdValidation, ValidationError) as exc:
        fields = exc.field_errors if isinstance(exc, DpdValidation) else {"body": exc.messages[0]}
        return error_response(
            request, 400, "VALIDATION_ERROR", "Bulk DPD calculation failed validation.", fields
        )
    except DpdPermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "DPD calculation permission and loan scope are required."
        )


@require_http_methods(["POST"])
def reminder_quarter_end_run(request):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            ReminderEngine.run_quarter_end(
                actor=actor, payload=parse_json_body(request), request=request
            ),
            request,
        )
    except (ReminderValidation, ValidationError) as exc:
        fields = (
            exc.field_errors
            if isinstance(exc, ReminderValidation)
            else getattr(exc, "message_dict", {"body": exc.messages[0]})
        )
        return error_response(
            request, 400, "VALIDATION_ERROR", "Reminder run failed validation.", fields
        )
    except ReminderPermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "Reminder permission and loan scope are required."
        )
    except ReminderNotFound:
        return error_response(request, 404, "NOT_FOUND", "The loan is inaccessible.")
    except ReminderConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["GET", "POST"])
def reminder_collection(request, loan_account_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        if request.method == "GET":
            rows, pagination = ReminderEngine.list_for_loan(actor=actor, loan_account_id=loan_account_id, query_params=request.GET)
            return list_response(rows, pagination, request)
        return success_response(
            ReminderEngine.create_reminder(
                actor=actor,
                loan_account_id=loan_account_id,
                payload=parse_json_body(request),
                request=request,
            ),
            request,
        )
    except (ReminderValidation, ValidationError) as exc:
        fields = (
            exc.field_errors
            if isinstance(exc, ReminderValidation)
            else getattr(exc, "message_dict", {"body": exc.messages[0]})
        )
        return error_response(
            request, 400, "VALIDATION_ERROR", "Reminder failed validation.", fields
        )
    except ReminderPermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "Reminder read/create permission and loan scope are required."
        )
    except ReminderNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "The loan account was not found or is inaccessible."
        )
    except ReminderConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["GET"])
def reminder_list(request):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        rows, pagination = ReminderEngine.list_scoped(actor=actor, query_params=request.GET)
        return list_response(rows, pagination, request)
    except ReminderValidation as exc:
        return error_response(request, 400, "VALIDATION_ERROR", "Reminder list failed validation.", exc.field_errors)
    except ReminderPermissionDenied:
        return error_response(request, 403, "FORBIDDEN", "Reminder read permission and loan scope are required.")


@require_http_methods(["POST"])
def reminder_send(request, reminder_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        payload = parse_json_body(request)
        if payload:
            raise ReminderValidation({"body": "The send body must be empty."})
        return success_response(
            ReminderEngine.send_reminder(
                actor=actor,
                reminder_id=reminder_id,
                idempotency_key=request.headers.get("Idempotency-Key", ""),
                request=request,
            ),
            request,
        )
    except (ReminderValidation, ValidationError) as exc:
        fields = (
            exc.field_errors
            if isinstance(exc, ReminderValidation)
            else getattr(exc, "message_dict", {"body": exc.messages[0]})
        )
        return error_response(
            request, 400, "VALIDATION_ERROR", "Reminder send failed validation.", fields
        )
    except ReminderPermissionDenied:
        return error_response(request, 403, "FORBIDDEN", "Reminder permission is required.")
    except ReminderNotFound:
        return error_response(request, 404, "NOT_FOUND", "The reminder was not found or is inaccessible.")
    except ReminderConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))
