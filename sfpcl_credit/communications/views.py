from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.views.decorators.http import require_http_methods

from sfpcl_credit.api import error_response, list_response, parse_json_body, success_response
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
                "PERMISSION_DENIED",
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
            "PERMISSION_DENIED",
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
            "PERMISSION_DENIED",
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
