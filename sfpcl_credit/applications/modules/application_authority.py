"""Application-owned object authority shared by application subresources."""

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.identity.modules.object_permissions import evaluate_object_access


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
            allow_global="credit_manager" in actor.role_codes(),
        )
    return application, evaluate_application_object_access(
        application=application,
        actor=actor,
        required_permission=required_permission,
        actor_permissions=permissions,
    )


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
