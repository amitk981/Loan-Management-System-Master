from pathlib import PurePath

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from sfpcl_credit.api import (
    error_response,
    list_response,
    parse_json_body,
    success_response,
)
from sfpcl_credit.identity.modules import http_auth
from sfpcl_credit.reports.errors import ReportPermissionDenied, ReportValidation
from sfpcl_credit.reports.modules import report_export
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


@require_http_methods(["POST"])
def export_collection(request):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        payload = parse_json_body(request)
        job, replayed = report_export.request_export(
            actor=actor,
            payload=payload,
            idempotency_key=request.headers.get("Idempotency-Key"),
            request=request,
        )
    except ValidationError:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Request body must be valid JSON.",
            {"body": "Must be a JSON object."},
        )
    except ReportValidation as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Report export request failed validation.",
            exc.field_errors,
        )
    except ReportPermissionDenied:
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "Report read and export permissions are required.",
        )
    response = success_response(
        report_export.serialize_job(job, replayed=replayed),
        request,
    )
    response.status_code = 202
    return response


@require_http_methods(["GET"])
def export_detail(request, export_job_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data = report_export.status_for_actor(
            actor=actor,
            export_job_id=export_job_id,
            request=request,
        )
    except ObjectDoesNotExist:
        return error_response(
            request, 404, "NOT_FOUND", "Requested report export job was not found."
        )
    except ReportPermissionDenied:
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "Report read and export permissions are required.",
        )
    return success_response(data, request)


@require_http_methods(["GET"])
def export_download(request, export_job_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        job, content = report_export.read_download(
            actor=actor,
            export_job_id=export_job_id,
            token=request.GET.get("token", ""),
            request=request,
        )
    except ObjectDoesNotExist:
        return error_response(
            request, 404, "NOT_FOUND", "Requested report export job was not found."
        )
    except ReportValidation as exc:
        return error_response(
            request,
            410,
            "DOWNLOAD_EXPIRED",
            "Report export download is unavailable.",
            exc.field_errors,
        )
    except ReportPermissionDenied:
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "Report read and export permissions are required.",
        )
    response = HttpResponse(content, content_type=job.content_type)
    filename = PurePath(f"{job.report_code}.{job.export_format}").name
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response["X-Content-Type-Options"] = "nosniff"
    return response
