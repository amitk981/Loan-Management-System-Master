from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.identity.modules.object_permissions import evaluate_object_access


def evaluate_member_authority(*, actor_user, member, permission, globally_authorized=False):
    """Return the single member-owned object-authority result used by public member modules."""
    role_code = getattr(getattr(actor_user, "primary_role", None), "role_code", "")
    return evaluate_object_access(
        actor_user_id=actor_user.user_id,
        actor_team_codes=actor_user.team_codes(),
        actor_permission_codes=auth_service.effective_permission_codes(actor_user),
        required_permission=permission,
        object_owner_user_id=member.created_by_user_id,
        allow_global=(globally_authorized or
            member.created_by_user_id is None
            or role_code in {"system_admin", "credit_manager"}
        ),
    )
