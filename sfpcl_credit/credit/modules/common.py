from dataclasses import dataclass

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.domain_errors import (
    DomainInvalidStateError,
    DomainNotFound,
    DomainObjectAccessDenied,
    DomainPermissionDenied,
    DomainValidationError,
)
from sfpcl_credit.identity.modules import auth_service


APPLICATION_READ_PERMISSION = "applications.loan_application.read"
ELIGIBILITY_RUN_PERMISSION = "credit.eligibility.run"
LOAN_LIMIT_CALCULATE_PERMISSION = "credit.loan_limit.calculate"


@dataclass(frozen=True)
class RequestMeta:
    request_id: str | None = None
    ip_address: str = ""
    user_agent: str = ""


CreditModuleValidationError = DomainValidationError
CreditModuleInvalidStateError = DomainInvalidStateError
CreditModulePermissionDenied = DomainPermissionDenied
CreditModuleObjectAccessDenied = DomainObjectAccessDenied
CreditModuleNotFound = DomainNotFound


def normalize_request_meta(request_meta=None):
    if isinstance(request_meta, RequestMeta):
        return request_meta
    request_meta = request_meta or {}
    return RequestMeta(
        request_id=request_meta.get("request_id"),
        ip_address=request_meta.get("ip_address", ""),
        user_agent=request_meta.get("user_agent", ""),
    )


def require_permission(actor, permission_code, message, actor_permissions=None):
    permissions = actor_permissions or auth_service.effective_permission_codes(actor)
    if permission_code not in permissions:
        raise CreditModulePermissionDenied(message)
    return permissions


def require_application_access(application, actor, permission_code, actor_permissions=None):
    from sfpcl_credit.applications.services import evaluate_application_object_access

    object_access = evaluate_application_object_access(
        application,
        actor,
        permission_code,
        actor_permissions,
    )
    if not object_access.allowed:
        raise CreditModuleObjectAccessDenied(object_access)


def project_application_object_access(
    action,
    *,
    application,
    actor,
    permission_code,
    actor_permissions=None,
):
    """Overlay object authority on a six-field action without serializing the resource."""
    from sfpcl_credit.applications.services import evaluate_application_object_access

    object_access = evaluate_application_object_access(
        application,
        actor,
        permission_code,
        actor_permissions,
    )
    if object_access.allowed or object_access.error_code != "OBJECT_ACCESS_DENIED":
        return action
    return {
        **action,
        "enabled": False,
        "disabled_reason": "You do not have access to this loan application.",
    }


def get_application_or_raise(application_id):
    application = (
        LoanApplication.objects.select_related(
            "member",
            "nominee",
            "created_by_user",
            "received_by_user",
        )
        .filter(loan_application_id=application_id)
        .first()
    )
    if application is None:
        raise CreditModuleNotFound("Loan application was not found.")
    return application
