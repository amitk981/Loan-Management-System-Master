from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.identity.modules.object_permissions import evaluate_object_access

GLOBAL_MEMBER_AUTHORITY_PERMISSIONS = frozenset({
    "members.active_status.verify",
    "members.member.identity_change.approve",
})


def evaluate_member_authority(*, actor_user, member, permission):
    """Return the single member-owned object-authority result used by public member modules."""
    has_global_authority = bool(
        getattr(getattr(actor_user, "primary_role", None), "is_system_role", False)
        and permission in GLOBAL_MEMBER_AUTHORITY_PERMISSIONS
    )
    return evaluate_object_access(
        actor_user_id=actor_user.user_id,
        actor_team_codes=actor_user.team_codes(),
        actor_permission_codes=auth_service.effective_permission_codes(actor_user),
        required_permission=permission,
        object_owner_user_id=member.created_by_user_id,
        allow_global=(
            member.created_by_user_id is None
            or has_global_authority
        ),
    )
