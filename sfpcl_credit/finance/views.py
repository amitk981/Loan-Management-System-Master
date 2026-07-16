from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from sfpcl_credit.api import error_response, parse_json_body, success_response
from sfpcl_credit.domain_errors import (
    DomainInvalidStateError,
    DomainObjectAccessDenied,
    DomainPermissionDenied,
)
from sfpcl_credit.sap_workflow.modules.sap_customer_profile import (
    SapRequestConflict,
    complete_request,
    create_request,
    issue_delivery_capability,
    read_delivered_annexure,
    read_member_code,
    record_delivery_denial,
    send_request,
)
from sfpcl_credit.identity.modules import http_auth


@require_http_methods(["POST"])
def sap_customer_profile_request(request, loan_application_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data = create_request(
            actor=actor,
            application_id=loan_application_id,
            payload=parse_json_body(request),
            request=request,
        )
        return success_response(data, request)
    except ValidationError as exc:
        errors = exc.message_dict if hasattr(exc, "message_dict") else {"body": exc.messages}
        return error_response(
            request, 400, "VALIDATION_ERROR", "SAP request failed validation.",
            {key: value[0] if isinstance(value, list) else value for key, value in errors.items()},
        )
    except DomainPermissionDenied as exc:
        return error_response(request, 403, "FORBIDDEN", exc.message)
    except DomainObjectAccessDenied:
        return error_response(
            request, 403, "OBJECT_ACCESS_DENIED",
            "You do not have access to this loan application.",
        )
    except DomainInvalidStateError as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    except SapRequestConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["POST"])
def sap_customer_profile_request_send(request, sap_customer_profile_request_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data = send_request(
            actor=actor,
            request_id=sap_customer_profile_request_id,
            payload=parse_json_body(request),
            request=request,
        )
        return success_response(data, request)
    except ValidationError as exc:
        return _validation_error(request, exc, "SAP request send failed validation.")
    except DomainPermissionDenied as exc:
        return error_response(request, 403, "FORBIDDEN", exc.message)
    except DomainObjectAccessDenied:
        return error_response(
            request, 403, "OBJECT_ACCESS_DENIED",
            "The SAP request was not found or is inaccessible.",
        )
    except DomainInvalidStateError as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    except SapRequestConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["POST"])
def sap_customer_profile_request_complete(request, sap_customer_profile_request_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data = complete_request(
            actor=actor,
            request_id=sap_customer_profile_request_id,
            payload=parse_json_body(request),
            request=request,
        )
        return success_response(data, request)
    except ValidationError as exc:
        return _validation_error(request, exc, "SAP request completion failed validation.")
    except DomainPermissionDenied as exc:
        return error_response(request, 403, "FORBIDDEN", exc.message)
    except DomainObjectAccessDenied:
        return error_response(
            request, 403, "OBJECT_ACCESS_DENIED",
            "The SAP request was not found or is inaccessible.",
        )
    except DomainInvalidStateError as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    except SapRequestConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["POST"])
def sap_annexure_delivery_capability(request, sap_customer_profile_request_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        payload = parse_json_body(request)
        if payload:
            raise ValidationError({field: "Unknown field." for field in payload})
        return success_response(
            issue_delivery_capability(
                actor=actor,
                request_id=sap_customer_profile_request_id,
                request=request,
            ),
            request,
        )
    except ValidationError as exc:
        return _validation_error(request, exc, "SAP delivery failed validation.")
    except DomainPermissionDenied as exc:
        return error_response(request, 403, "FORBIDDEN", exc.message)
    except DomainObjectAccessDenied:
        return error_response(
            request, 403, "OBJECT_ACCESS_DENIED",
            "The SAP request was not found or is inaccessible.",
        )
    except DomainInvalidStateError as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))


@require_http_methods(["GET"])
def sap_annexure_download(request, sap_customer_profile_request_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        if set(request.GET) != {"capability"} or not request.GET.get("capability"):
            raise ValidationError({"capability": "This query parameter is required."})
        workbook, document = read_delivered_annexure(
            actor=actor,
            request_id=sap_customer_profile_request_id,
            capability=request.GET["capability"],
            request=request,
        )
        response = HttpResponse(workbook, content_type=document.mime_type)
        response["Content-Disposition"] = f'attachment; filename="{document.file_name}"'
        response["X-Content-Type-Options"] = "nosniff"
        return response
    except ValidationError as exc:
        return _validation_error(request, exc, "SAP delivery failed validation.")
    except DomainPermissionDenied as exc:
        record_delivery_denial(
            actor=actor, request_id=sap_customer_profile_request_id,
            request=request, reason="permission_denied",
        )
        return error_response(request, 403, "FORBIDDEN", exc.message)
    except DomainObjectAccessDenied:
        record_delivery_denial(
            actor=actor, request_id=sap_customer_profile_request_id,
            request=request, reason="object_access_denied",
        )
        return error_response(
            request, 403, "OBJECT_ACCESS_DENIED",
            "The SAP request was not found or is inaccessible.",
        )
    except DomainInvalidStateError as exc:
        record_delivery_denial(
            actor=actor, request_id=sap_customer_profile_request_id,
            request=request, reason="invalid_delivery_state",
        )
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    except SapRequestConflict as exc:
        record_delivery_denial(
            actor=actor, request_id=sap_customer_profile_request_id,
            request=request, reason="invalid_or_expired_capability",
        )
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["GET"])
def member_sap_customer_code(request, member_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            read_member_code(actor=actor, member_id=member_id, request=request), request
        )
    except DomainPermissionDenied as exc:
        return error_response(request, 403, "FORBIDDEN", exc.message)
    except DomainObjectAccessDenied:
        return error_response(
            request, 403, "OBJECT_ACCESS_DENIED",
            "The member SAP code was not found or is inaccessible.",
        )
    except DomainInvalidStateError as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))


def _validation_error(request, exc, message):
    errors = exc.message_dict if hasattr(exc, "message_dict") else {"body": exc.messages}
    return error_response(
        request, 400, "VALIDATION_ERROR", message,
        {key: value[0] if isinstance(value, list) else value for key, value in errors.items()},
    )
