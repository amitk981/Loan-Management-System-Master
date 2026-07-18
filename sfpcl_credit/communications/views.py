from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.views.decorators.http import require_http_methods

from sfpcl_credit.api import error_response, list_response, parse_json_body, success_response
from sfpcl_credit.communications.modules.communication_dispatcher import (
    CommunicationDispatcher,
    CommunicationDispatchConflict,
)
from sfpcl_credit.communications import services
from sfpcl_credit.identity.modules import http_auth


@require_http_methods(["GET", "POST"])
def content_template_collection(request):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if request.method == "GET":
        if not services.user_can_read_content_templates(user):
            return error_response(
                request,
                403,
                "FORBIDDEN",
                "You do not have permission to read content templates.",
            )
        try:
            data, pagination = services.paginated_content_templates(request.GET)
        except ValidationError as exc:
            return error_response(
                request,
                400,
                "VALIDATION_ERROR",
                "Content template query failed validation.",
                services.validation_field_errors(exc),
            )
        return list_response(data, pagination, request)

    if not services.user_can_manage_content_templates(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to manage content templates.",
        )
    try:
        payload = parse_json_body(request)
        data = services.create_content_template(user, request, payload)
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Content template failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(data, request)


@require_http_methods(["PATCH"])
def content_template_detail(request, content_template_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if not services.user_can_manage_content_templates(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to manage content templates.",
        )
    try:
        payload = parse_json_body(request)
        data = services.update_content_template(
            user, request, content_template_id, payload
        )
    except ObjectDoesNotExist:
        return error_response(
            request, 404, "NOT_FOUND", "Requested content template was not found."
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Content template failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(data, request)


@require_http_methods(["GET"])
def communication_collection(request):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if not services.user_can_read_communications(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to read communications.",
        )
    try:
        data, pagination = services.paginated_communications(request.GET)
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Communication query failed validation.",
            services.validation_field_errors(exc),
        )
    return list_response(data, pagination, request)


@require_http_methods(["POST"])
def communication_send(request):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if not services.user_can_send_communications(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to send communications.",
        )
    try:
        payload = parse_json_body(request)
        data = services.send_communication(user, request, payload)
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Communication failed validation.",
            services.validation_field_errors(exc),
        )
    except CommunicationDispatchConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))
    return success_response(data, request)


@require_http_methods(["GET"])
def communication_exception_collection(request):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if not services.user_can_manage_communication_exceptions(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to review communication exceptions.",
        )
    data = CommunicationDispatcher.exception_evidence(actor=user)
    pagination = {
        "page": 1,
        "page_size": 100,
        "total_count": len(data),
        "total_pages": 1,
        "has_next": False,
        "has_previous": False,
    }
    return list_response(data, pagination, request)


@require_http_methods(["GET"])
def communication_exception_detail(request, communication_exception_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if not services.user_can_manage_communication_exceptions(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to review communication exceptions.",
        )
    data = CommunicationDispatcher.exception_evidence(
        actor=user, exception_id=communication_exception_id, limit=1
    )
    if not data:
        return error_response(
            request, 404, "NOT_FOUND", "Requested communication exception was not found."
        )
    return success_response(data[0], request)


@require_http_methods(["POST"])
def communication_exception_resolve(request, communication_exception_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if not services.user_can_manage_communication_exceptions(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to resolve communication exceptions.",
        )
    try:
        payload = parse_json_body(request)
        unknown = set(payload) - {"resolution_action", "resolution_version"}
        if unknown:
            raise ValidationError(
                {field: "Unknown field." for field in sorted(unknown)}
            )
        action = payload.get("resolution_action")
        version = payload.get("resolution_version")
        if not isinstance(action, str) or not action.strip():
            raise ValidationError(
                {"resolution_action": "This field is required."}
            )
        if not isinstance(version, int) or isinstance(version, bool) or version < 1:
            raise ValidationError(
                {"resolution_version": "Must be a positive integer."}
            )
        data = CommunicationDispatcher.resolve_exception(
            actor=user,
            exception_id=communication_exception_id,
            expected_version=version,
            resolution_action=action.strip(),
            request=request,
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Communication exception resolution failed validation.",
            services.validation_field_errors(exc),
        )
    except CommunicationDispatchConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))
    return success_response(data, request)


@require_http_methods(["GET"])
def notification_collection(request):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if not services.user_can_read_notifications(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to read notifications.",
        )
    try:
        data, pagination = services.paginated_notifications(user, request.GET)
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Notification query failed validation.",
            services.validation_field_errors(exc),
        )
    return list_response(data, pagination, request)


@require_http_methods(["POST"])
def notification_mark_read(request, notification_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if not services.user_can_read_notifications(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to read notifications.",
        )
    try:
        payload = parse_json_body(request)
        data = services.mark_notification_read(user, request, notification_id, payload)
    except services.StaleWriteError:
        return error_response(
            request,
            409,
            "STALE_WRITE",
            "Notification read state changed. Refresh and try again.",
        )
    except ObjectDoesNotExist:
        return error_response(
            request, 404, "NOT_FOUND", "Requested notification was not found."
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Notification read update failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(data, request)
