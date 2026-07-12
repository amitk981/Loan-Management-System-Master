from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.identity.modules.object_permissions import evaluate_object_access

# Explicit high-risk permission scopes. Unlike role provenance or an unowned row, this
# projection is independently reviewable and applies identically to system/custom roles.
GLOBAL_MEMBER_AUTHORITY_PERMISSIONS = frozenset({
    "members.member.read",
    "members.active_status.verify",
    "members.member.identity_change.approve",
})


def evaluate_member_authority(*, actor_user, member, permission):
    """Return the single member-owned object-authority result used by public member modules."""
    # These high-risk permissions are the explicit, reviewable global scope grant.
    # Role provenance and absence of an owner never confer object authority.
    has_global_authority = permission in GLOBAL_MEMBER_AUTHORITY_PERMISSIONS
    return evaluate_object_access(
        actor_user_id=actor_user.user_id,
        actor_team_codes=actor_user.team_codes(),
        actor_permission_codes=auth_service.effective_permission_codes(actor_user),
        required_permission=permission,
        object_owner_user_id=member.created_by_user_id,
        allow_global=has_global_authority,
    )
