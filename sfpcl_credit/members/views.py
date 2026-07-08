from django.core.exceptions import ValidationError
from django.views.decorators.http import require_GET

from sfpcl_credit.api import error_response, list_response, success_response
from sfpcl_credit.identity.modules import http_auth
from sfpcl_credit.members import services


@require_GET
def member_collection(request):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if not services.user_can_read_members(user):
        return error_response(
            request,
            403,
            "PERMISSION_DENIED",
            "You do not have permission to read members.",
        )
    try:
        data, pagination = services.paginated_members(request.GET)
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Member directory query failed validation.",
            services.validation_field_errors(exc),
        )
    return list_response(data, pagination, request)


@require_GET
def member_detail(request, member_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if not services.user_can_read_members(user):
        return error_response(
            request,
            403,
            "PERMISSION_DENIED",
            "You do not have permission to read members.",
        )
    member = services.get_member_profile(member_id)
    if member is None:
        return error_response(request, 404, "NOT_FOUND", "Member was not found.")
    return success_response(services.serialize_member_profile(member, user), request)
