from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.views.decorators.http import require_GET, require_http_methods

from sfpcl_credit.api import error_response, list_response, parse_json_body, success_response
from sfpcl_credit.configurations import services
from sfpcl_credit.identity.modules import http_auth


@require_http_methods(["GET", "POST"])
def loan_policy_collection(request):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if request.method == "GET":
        if not services.user_can_read_loan_policy(user):
            return error_response(
                request,
                403,
                "FORBIDDEN",
                "You do not have permission to read loan policy configuration.",
            )
        try:
            data, pagination = services.paginated_loan_policy_configs(request.GET)
        except ValidationError as exc:
            return error_response(
                request,
                400,
                "VALIDATION_ERROR",
                "Loan policy configuration query failed validation.",
                services.validation_field_errors(exc),
            )
        return list_response(data, pagination, request)

    if not services.user_can_manage_loan_policy(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to manage loan policy configuration.",
        )
    try:
        payload = parse_json_body(request)
        data = services.create_loan_policy_config(user, request, payload)
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Loan policy configuration failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(data, request)


@require_http_methods(["PATCH"])
def loan_policy_detail(request, loan_policy_config_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if not services.user_can_manage_loan_policy(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to manage loan policy configuration.",
        )
    try:
        payload = parse_json_body(request)
        data = services.update_loan_policy_config(
            user, request, loan_policy_config_id, payload
        )
    except ObjectDoesNotExist:
        return error_response(
            request, 404, "NOT_FOUND", "Requested loan policy config was not found."
        )
    except services.InvalidStateTransition as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Loan policy configuration failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(data, request)


@require_http_methods(["POST"])
def loan_policy_activate(request, loan_policy_config_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if not services.user_can_manage_loan_policy(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to manage loan policy configuration.",
        )
    try:
        data = services.activate_loan_policy_config(user, request, loan_policy_config_id)
    except ObjectDoesNotExist:
        return error_response(
            request, 404, "NOT_FOUND", "Requested loan policy config was not found."
        )
    except services.InvalidStateTransition as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Loan policy activation failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(data, request)


@require_GET
def version_history_list(request):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if not services.user_can_read_version_histories(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to read version history.",
        )
    try:
        data, pagination = services.paginated_version_histories(request.GET)
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Version history query failed validation.",
            services.validation_field_errors(exc),
        )
    return list_response(data, pagination, request)
