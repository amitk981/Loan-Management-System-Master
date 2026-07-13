from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.views.decorators.http import require_http_methods

from sfpcl_credit.api import error_response, list_response, parse_json_body, success_response
from sfpcl_credit.approvals.modules import approval_matrix_configuration as services
from sfpcl_credit.approvals.modules import approval_case_engine
from sfpcl_credit.domain_errors import DomainObjectAccessDenied
from sfpcl_credit.identity.modules import http_auth
from sfpcl_credit.identity.modules.auth_service import effective_permission_codes


def _authorized(request, manage=False):
    user, response = http_auth.authenticated_user(request)
    if response is not None: return user, response
    allowed = services.can_manage(user) if manage else services.can_read(user)
    if not allowed: return user, error_response(request, 403, "FORBIDDEN", "You do not have approval matrix permission.")
    return user, None


def _failure(request, exc):
    if isinstance(exc, services.ConfigurationConflict):
        status = 403 if exc.code in {
            "FORBIDDEN", "MAKER_CHECKER_VIOLATION", "APPROVAL_AUTHORITY_REQUIRED"
        } else 409
        return error_response(request, status, exc.code, str(exc))
    if isinstance(exc, ObjectDoesNotExist):
        return error_response(request, 404, "NOT_FOUND", "Configuration was not found.")
    details = exc.message_dict if hasattr(exc, "message_dict") else {"non_field_errors": [str(exc)]}
    return error_response(request, 400, "VALIDATION_ERROR", "Configuration failed validation.",
                          {key: value[0] if isinstance(value, list) else value for key, value in details.items()})


@require_http_methods(["GET"])
def approval_case_collection(request):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if "approvals.case.read" not in effective_permission_codes(user):
        return error_response(
            request, 403, "FORBIDDEN", "You do not have approval case read permission."
        )
    try:
        data, pagination = approval_case_engine.list_approval_cases(
            actor=user, query_params=request.GET
        )
        return list_response(data, pagination, request)
    except ValidationError as exc:
        details = exc.message_dict if hasattr(exc, "message_dict") else {}
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Approval case filters failed validation.",
            {key: value[0] if isinstance(value, list) else value for key, value in details.items()},
        )


@require_http_methods(["GET"])
def approval_case_detail(request, approval_case_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    permissions = effective_permission_codes(user)
    if "approvals.case.read" not in permissions:
        return error_response(
            request, 403, "FORBIDDEN", "You do not have approval case read permission."
        )
    try:
        data = approval_case_engine.get_approval_case(
            actor=user,
            case_id=approval_case_id,
            actor_permissions=permissions,
        )
        return success_response(data, request)
    except ObjectDoesNotExist:
        return error_response(request, 404, "NOT_FOUND", "Approval case was not found.")
    except DomainObjectAccessDenied:
        return error_response(
            request,
            403,
            "OBJECT_ACCESS_DENIED",
            "You cannot access this approval case.",
        )


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


@require_http_methods(["GET"])
def proposal_detail(request, approval_configuration_proposal_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None: return response
    try: return success_response(services.get_proposal(approval_configuration_proposal_id, user), request)
    except (services.ConfigurationConflict, ObjectDoesNotExist) as exc: return _failure(request, exc)


@require_http_methods(["POST"])
def proposal_approve(request, approval_configuration_proposal_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None: return response
    try:
        return success_response(services.decide_proposal(
            approval_configuration_proposal_id, user, request, parse_json_body(request), "approve"
        ), request)
    except (ValidationError, services.ConfigurationConflict, ObjectDoesNotExist) as exc: return _failure(request, exc)


@require_http_methods(["POST"])
def proposal_reject(request, approval_configuration_proposal_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None: return response
    try:
        return success_response(services.decide_proposal(
            approval_configuration_proposal_id, user, request, parse_json_body(request), "reject"
        ), request)
    except (ValidationError, services.ConfigurationConflict, ObjectDoesNotExist) as exc: return _failure(request, exc)
