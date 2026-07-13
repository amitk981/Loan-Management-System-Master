from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.views.decorators.http import require_http_methods

from sfpcl_credit.api import error_response, list_response, parse_json_body, success_response
from sfpcl_credit.approvals.modules import approval_matrix_configuration as services
from sfpcl_credit.identity.modules import http_auth


def _authorized(request, manage=False):
    user, response = http_auth.authenticated_user(request)
    if response is not None: return user, response
    allowed = services.can_manage(user) if manage else services.can_read(user)
    if not allowed: return user, error_response(request, 403, "FORBIDDEN", "You do not have approval matrix permission.")
    return user, None


def _failure(request, exc):
    if isinstance(exc, services.ConfigurationConflict):
        return error_response(request, 409, "CONFIGURATION_CONFLICT", str(exc))
    if isinstance(exc, ObjectDoesNotExist):
        return error_response(request, 404, "NOT_FOUND", "Configuration was not found.")
    details = exc.message_dict if hasattr(exc, "message_dict") else {"non_field_errors": [str(exc)]}
    return error_response(request, 400, "VALIDATION_ERROR", "Configuration failed validation.",
                          {key: value[0] if isinstance(value, list) else value for key, value in details.items()})


@require_http_methods(["GET", "POST"])
def rule_collection(request):
    user, response = _authorized(request, manage=request.method == "POST")
    if response is not None: return response
    if request.method == "GET":
        try:
            data, pagination = services.list_rules(request.GET)
            return list_response(data, pagination, request)
        except ValidationError as exc:
            return _failure(request, exc)
    try: return success_response(services.create_rule(user, request, parse_json_body(request)), request)
    except (ValidationError, services.ConfigurationConflict) as exc: return _failure(request, exc)


@require_http_methods(["PATCH"])
def rule_detail(request, approval_matrix_rule_id):
    user, response = _authorized(request, manage=True)
    if response is not None: return response
    try: return success_response(services.supersede_rule(user, request, approval_matrix_rule_id, parse_json_body(request)), request)
    except (ValidationError, services.ConfigurationConflict, ObjectDoesNotExist) as exc: return _failure(request, exc)


@require_http_methods(["GET", "POST"])
def committee_collection(request):
    user, response = _authorized(request, manage=request.method == "POST")
    if response is not None: return response
    if request.method == "GET":
        try:
            data, pagination = services.list_committees(request.GET)
            return list_response(data, pagination, request)
        except ValidationError as exc:
            return _failure(request, exc)
    try: return success_response(services.create_committee(user, request, parse_json_body(request)), request)
    except (ValidationError, services.ConfigurationConflict) as exc: return _failure(request, exc)


@require_http_methods(["PATCH"])
def committee_detail(request, sanction_committee_id):
    user, response = _authorized(request, manage=True)
    if response is not None: return response
    try: return success_response(services.supersede_committee(user, request, sanction_committee_id, parse_json_body(request)), request)
    except (ValidationError, services.ConfigurationConflict, ObjectDoesNotExist) as exc: return _failure(request, exc)
