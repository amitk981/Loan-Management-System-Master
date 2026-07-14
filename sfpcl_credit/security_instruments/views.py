from django.core.exceptions import ValidationError
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from sfpcl_credit.api import error_response, parse_json_body, request_ip, request_user_agent, success_response
from sfpcl_credit.identity.modules import http_auth
from sfpcl_credit.processes import security_instrument_evidence
from sfpcl_credit.security_instruments.modules import power_of_attorney
from sfpcl_credit.security_instruments.modules import cdsl_share_pledge
from sfpcl_credit.security_instruments.modules import security_package as package_service
from sfpcl_credit.security_instruments.modules import sh4
from sfpcl_credit.security_instruments.request_contracts import (
    PowerOfAttorneyRequest,
    CDSLBOAccountRevealRequest,
    CDSLSharePledgeRequest,
    SH4ShareTransferFormRequest,
)


def _metadata(request):
    return power_of_attorney.RequestMetadata(
        request_id=request.headers.get("X-Request-ID"),
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )


def _validation_response(request, message, exc):
    return error_response(
        request, 400, "VALIDATION_ERROR", message,
        power_of_attorney.validation_field_errors(exc),
    )


@require_http_methods(["GET", "POST"])
def package_power_of_attorney(request, security_package_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        if request.method == "GET":
            data = security_instrument_evidence.read_poa(
                actor=user, security_package_id=security_package_id
            )
        else:
            power_of_attorney.require_manage_actor(user)
            parsed = PowerOfAttorneyRequest.parse(parse_json_body(request))
            data = security_instrument_evidence.create_poa(
                actor=user, security_package_id=security_package_id,
                values=parsed.as_values(), metadata=_metadata(request),
            )
    except power_of_attorney.AccessDenied as exc:
        return error_response(request, 403, exc.error_code, "You do not have access to this Power of Attorney.")
    except power_of_attorney.NotFound:
        return error_response(request, 404, "NOT_FOUND", "Power of Attorney was not found.")
    except power_of_attorney.Conflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))
    except ValidationError as exc:
        return _validation_response(request, "Power of Attorney failed validation.", exc)
    return success_response(data, request)


@require_http_methods(["PATCH"])
def power_of_attorney_detail(request, power_of_attorney_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        power_of_attorney.require_manage_actor(user)
        parsed = PowerOfAttorneyRequest.parse(parse_json_body(request))
        data = security_instrument_evidence.update_poa(
            actor=user, power_of_attorney_id=power_of_attorney_id,
            values=parsed.as_values(), metadata=_metadata(request),
        )
    except power_of_attorney.AccessDenied as exc:
        return error_response(request, 403, exc.error_code, "You do not have access to this Power of Attorney.")
    except power_of_attorney.NotFound:
        return error_response(request, 404, "NOT_FOUND", "Power of Attorney was not found.")
    except power_of_attorney.Conflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))
    except ValidationError as exc:
        return _validation_response(request, "Power of Attorney failed validation.", exc)
    return success_response(data, request)


@require_http_methods(["GET", "POST"])
def package_sh4(request, security_package_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        if request.method == "GET":
            data = security_instrument_evidence.read_sh4(
                actor=user, security_package_id=security_package_id
            )
        else:
            sh4.require_manage_actor(user)
            parsed = SH4ShareTransferFormRequest.parse(parse_json_body(request))
            data = security_instrument_evidence.create_sh4(
                actor=user, security_package_id=security_package_id,
                values=parsed.as_values(), metadata=_metadata(request),
            )
    except sh4.AccessDenied as exc:
        return error_response(request, 403, exc.error_code, "You do not have access to this SH-4.")
    except sh4.NotFound:
        return error_response(request, 404, "NOT_FOUND", "SH-4 was not found.")
    except sh4.Conflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))
    except ValidationError as exc:
        return error_response(
            request, 400, "VALIDATION_ERROR", "SH-4 failed validation.",
            sh4.validation_field_errors(exc),
        )
    return success_response(data, request)


@require_http_methods(["PATCH"])
def sh4_detail(request, sh4_share_transfer_form_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        sh4.require_manage_actor(user)
        parsed = SH4ShareTransferFormRequest.parse(parse_json_body(request))
        data = security_instrument_evidence.update_sh4(
            actor=user, sh4_share_transfer_form_id=sh4_share_transfer_form_id,
            values=parsed.as_values(), metadata=_metadata(request),
        )
    except sh4.AccessDenied as exc:
        return error_response(request, 403, exc.error_code, "You do not have access to this SH-4.")
    except sh4.NotFound:
        return error_response(request, 404, "NOT_FOUND", "SH-4 was not found.")
    except sh4.Conflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))
    except ValidationError as exc:
        return error_response(
            request, 400, "VALIDATION_ERROR", "SH-4 failed validation.",
            sh4.validation_field_errors(exc),
        )
    return success_response(data, request)


@require_http_methods(["GET", "POST"])
def package_cdsl_share_pledge(request, security_package_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        if request.method == "GET":
            data = security_instrument_evidence.read_pledge(
                actor=user, security_package_id=security_package_id
            )
        else:
            cdsl_share_pledge.require_manage_actor(user)
            parsed = CDSLSharePledgeRequest.parse(parse_json_body(request))
            data = security_instrument_evidence.create_pledge(
                actor=user, security_package_id=security_package_id,
                values=parsed.as_values(), metadata=_metadata(request),
            )
    except cdsl_share_pledge.AccessDenied as exc:
        return error_response(
            request, 403, exc.error_code, "You do not have access to this CDSL pledge."
        )
    except cdsl_share_pledge.NotFound:
        return error_response(request, 404, "NOT_FOUND", "CDSL pledge was not found.")
    except cdsl_share_pledge.Conflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))
    except ValidationError as exc:
        return error_response(
            request, 400, "VALIDATION_ERROR", "CDSL pledge failed validation.",
            cdsl_share_pledge.validation_field_errors(exc),
        )
    return success_response(data, request)


@require_http_methods(["PATCH"])
def cdsl_share_pledge_detail(request, cdsl_share_pledge_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        cdsl_share_pledge.require_manage_actor(user)
        parsed = CDSLSharePledgeRequest.parse(parse_json_body(request))
        data = security_instrument_evidence.update_pledge(
            actor=user, cdsl_share_pledge_id=cdsl_share_pledge_id,
            values=parsed.as_values(), metadata=_metadata(request),
        )
    except cdsl_share_pledge.AccessDenied as exc:
        return error_response(
            request, 403, exc.error_code, "You do not have access to this CDSL pledge."
        )
    except cdsl_share_pledge.NotFound:
        return error_response(request, 404, "NOT_FOUND", "CDSL pledge was not found.")
    except cdsl_share_pledge.Conflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))
    except ValidationError as exc:
        return error_response(
            request, 400, "VALIDATION_ERROR", "CDSL pledge failed validation.",
            cdsl_share_pledge.validation_field_errors(exc),
        )
    return success_response(data, request)


@require_POST
def cdsl_share_pledge_reveal(request, cdsl_share_pledge_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    metadata = _metadata(request)
    try:
        cdsl_share_pledge.require_reveal_actor(
            user, cdsl_share_pledge_id, metadata
        )
        parsed = CDSLBOAccountRevealRequest.parse(parse_json_body(request))
        data = security_instrument_evidence.reveal_bo_accounts(
            actor=user, cdsl_share_pledge_id=cdsl_share_pledge_id,
            reason=parsed.reason, metadata=metadata,
        )
    except cdsl_share_pledge.AccessDenied as exc:
        return error_response(
            request, 403, exc.error_code,
            "You do not have access to reveal these BO accounts.",
        )
    except cdsl_share_pledge.NotFound:
        return error_response(request, 404, "NOT_FOUND", "CDSL pledge was not found.")
    except cdsl_share_pledge.Conflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))
    except ValidationError as exc:
        return error_response(
            request, 400, "VALIDATION_ERROR", "BO-account reveal failed validation.",
            cdsl_share_pledge.validation_field_errors(exc),
        )
    return success_response(data, request)


@require_GET
def security_package(request, loan_application_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data = security_instrument_evidence.read_package(
            actor=user, application_id=loan_application_id
        )
    except package_service.AccessDenied as exc:
        return error_response(request, 403, exc.error_code, "You do not have access to this security package.")
    except package_service.NotFound:
        return error_response(request, 404, "NOT_FOUND", "Security package was not found.")
    return success_response(data, request)


@require_POST
def security_package_refresh(request, loan_application_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        package_service.require_create_actor(user)
        payload = parse_json_body(request)
        if payload != {}:
            raise ValidationError({field: "Unknown field." for field in sorted(payload)})
        data = security_instrument_evidence.refresh_package(
            actor=user, application_id=loan_application_id, metadata=_metadata(request),
        )
    except package_service.AccessDenied as exc:
        return error_response(request, 403, exc.error_code, "You do not have access to this security package.")
    except package_service.NotFound:
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    except package_service.Conflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))
    except ValidationError as exc:
        return _validation_response(request, "Security package refresh failed validation.", exc)
    return success_response(data, request)
