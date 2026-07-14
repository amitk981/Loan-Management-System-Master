"""Application-owned object authority shared by application subresources."""

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.identity.modules.object_permissions import (
    ACCESS_ALLOWED_GLOBAL,
    ObjectAccessResult,
    evaluate_object_access,
)


_DOCUMENTATION_ABSENT_PARENT_ROLES = frozenset({"compliance_team_member"})


def resolve_application_access(
    *, application_id, actor, required_permission, actor_permissions=None
):
    """Resolve a parent application without exposing whether a denied identifier exists."""
    permissions = actor_permissions or auth_service.effective_permission_codes(actor)
    application = LoanApplication.objects.select_related("created_by_user", "received_by_user").filter(
        loan_application_id=application_id
    ).first()
    if application is None:
        return None, evaluate_object_access(
            actor_user_id=actor.user_id,
            actor_team_codes=actor.team_codes(),
            actor_permission_codes=permissions,
            required_permission=required_permission,
        )
    return application, evaluate_application_object_access(
        application=application,
        actor=actor,
        required_permission=required_permission,
        actor_permissions=permissions,
    )


def resolve_documentation_application_access(
    *, application_id, actor, required_permission, actor_permissions=None
):
    """Resolve documentation scope and its source-defined absent-parent disclosure."""
    permissions = actor_permissions or auth_service.effective_permission_codes(actor)
    application, access = resolve_application_access(
        application_id=application_id,
        actor=actor,
        required_permission=required_permission,
        actor_permissions=permissions,
    )
    if (
        application is None
        and required_permission in permissions
        and _DOCUMENTATION_ABSENT_PARENT_ROLES.intersection(actor.role_codes())
    ):
        access = ObjectAccessResult(
            allowed=True,
            reason=ACCESS_ALLOWED_GLOBAL,
            required_permission=required_permission,
        )
    return application, access


def evaluate_application_object_access(
    *, application, actor, required_permission, actor_permissions=None
):
    permissions = actor_permissions or auth_service.effective_permission_codes(actor)
    allow_global = (
        "credit_manager" in actor.role_codes()
        and application.current_stage == LoanApplication.STAGE_CREDIT_ASSESSMENT
    )
    result = evaluate_object_access(
        actor_user_id=actor.user_id,
        actor_team_codes=actor.team_codes(),
        actor_permission_codes=permissions,
        required_permission=required_permission,
        object_owner_user_id=application.created_by_user_id,
        allow_global=allow_global,
    )
    if result.allowed or result.error_code != "OBJECT_ACCESS_DENIED":
        return result
    if (
        application.received_by_user_id
        and application.received_by_user_id != application.created_by_user_id
    ):
        return evaluate_object_access(
            actor_user_id=actor.user_id,
            actor_team_codes=actor.team_codes(),
            actor_permission_codes=permissions,
            required_permission=required_permission,
            object_owner_user_id=application.received_by_user_id,
            allow_global=allow_global,
        )
    return result
