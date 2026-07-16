from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods

from sfpcl_credit.api import error_response, parse_json_body, success_response
from sfpcl_credit.domain_errors import (
    DomainInvalidStateError,
    DomainObjectAccessDenied,
    DomainPermissionDenied,
)
from sfpcl_credit.finance.modules.sap_customer_request import (
    SapRequestConflict,
    create_request,
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
        return error_response(request, 409, "INVALID_STATE", str(exc))
    except SapRequestConflict as exc:
        return error_response(request, 409, "SAP_REQUEST_CONFLICT", str(exc))
