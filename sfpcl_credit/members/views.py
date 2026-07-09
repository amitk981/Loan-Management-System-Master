from django.core.exceptions import ValidationError
from django.views.decorators.http import require_GET, require_http_methods

from sfpcl_credit.api import (
    error_response,
    list_response,
    parse_json_body,
    request_ip,
    request_user_agent,
    success_response,
)
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


@require_http_methods(["GET", "POST"])
def member_nominees(request, member_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if request.method == "GET" and not services.user_can_read_nominees(user):
        return error_response(
            request,
            403,
            "PERMISSION_DENIED",
            "You do not have permission to read nominees.",
        )
    if request.method == "POST" and not services.user_can_create_nominees(user):
        return error_response(
            request,
            403,
            "PERMISSION_DENIED",
            "You do not have permission to create nominees.",
        )

    member = services.get_accessible_member(member_id)
    if member is None:
        return error_response(request, 404, "NOT_FOUND", "Member was not found.")

    if request.method == "GET":
        try:
            data, pagination = services.paginated_nominees(member, request.GET)
        except ValidationError as exc:
            return error_response(
                request,
                400,
                "VALIDATION_ERROR",
                "Nominee query failed validation.",
                services.validation_field_errors(exc),
            )
        return list_response(data, pagination, request)

    try:
        body = parse_json_body(request)
        nominee = services.create_nominee(
            member,
            body,
            user,
            request_ip(request),
            request_user_agent(request),
        )
    except services.NomineeValidationError as exc:
        return error_response(request, 400, exc.code, exc.message, exc.field_errors)
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Nominee payload failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(services.serialize_nominee(nominee), request)


@require_http_methods(["GET", "POST"])
def member_shareholdings(request, member_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if request.method == "GET" and not services.user_can_read_shareholdings(user):
        return error_response(
            request,
            403,
            "PERMISSION_DENIED",
            "You do not have permission to read shareholdings.",
        )
    if request.method == "POST" and not services.user_can_create_shareholdings(user):
        return error_response(
            request,
            403,
            "PERMISSION_DENIED",
            "You do not have permission to create shareholdings.",
        )

    member = services.get_accessible_member(member_id)
    if member is None:
        return error_response(request, 404, "NOT_FOUND", "Member was not found.")

    if request.method == "GET":
        try:
            data, pagination = services.paginated_shareholdings(member, request.GET)
        except ValidationError as exc:
            return error_response(
                request,
                400,
                "VALIDATION_ERROR",
                "Shareholding query failed validation.",
                services.validation_field_errors(exc),
            )
        return list_response(data, pagination, request)

    try:
        body = parse_json_body(request)
        shareholding = services.create_shareholding(
            member,
            body,
            user,
            request_ip(request),
            request_user_agent(request),
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Shareholding payload failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(services.serialize_shareholding(shareholding), request)


@require_http_methods(["GET", "POST"])
def member_land_holdings(request, member_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if request.method == "GET" and not services.user_can_read_land_crop(user):
        return error_response(
            request,
            403,
            "PERMISSION_DENIED",
            "You do not have permission to read member land and crop records.",
        )
    if request.method == "POST" and not services.user_can_create_land_crop(user):
        return error_response(
            request,
            403,
            "PERMISSION_DENIED",
            "You do not have permission to create member land and crop records.",
        )

    member = services.get_accessible_member(member_id)
    if member is None:
        return error_response(request, 404, "NOT_FOUND", "Member was not found.")

    if request.method == "GET":
        try:
            data, pagination = services.paginated_land_holdings(member, request.GET)
        except ValidationError as exc:
            return error_response(
                request,
                400,
                "VALIDATION_ERROR",
                "Land holding query failed validation.",
                services.validation_field_errors(exc),
            )
        return list_response(data, pagination, request)

    try:
        body = parse_json_body(request)
        land_holding = services.create_land_holding(
            member,
            body,
            user,
            request_ip(request),
            request_user_agent(request),
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Land holding payload failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(services.serialize_land_holding(land_holding), request)


@require_http_methods(["GET", "POST"])
def member_crop_plans(request, member_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if request.method == "GET" and not services.user_can_read_land_crop(user):
        return error_response(
            request,
            403,
            "PERMISSION_DENIED",
            "You do not have permission to read member land and crop records.",
        )
    if request.method == "POST" and not services.user_can_create_land_crop(user):
        return error_response(
            request,
            403,
            "PERMISSION_DENIED",
            "You do not have permission to create member land and crop records.",
        )

    member = services.get_accessible_member(member_id)
    if member is None:
        return error_response(request, 404, "NOT_FOUND", "Member was not found.")

    if request.method == "GET":
        try:
            data, pagination = services.paginated_crop_plans(member, request.GET)
        except ValidationError as exc:
            return error_response(
                request,
                400,
                "VALIDATION_ERROR",
                "Crop plan query failed validation.",
                services.validation_field_errors(exc),
            )
        return list_response(data, pagination, request)

    try:
        body = parse_json_body(request)
        crop_plan = services.create_crop_plan(
            member,
            body,
            user,
            request_ip(request),
            request_user_agent(request),
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Crop plan payload failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(services.serialize_crop_plan(crop_plan), request)
