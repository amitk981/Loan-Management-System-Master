from sfpcl_credit.identity.modules import auth_service
from django.db.models import Q

from sfpcl_credit.identity.modules.object_permissions import ObjectAccessResult
from sfpcl_credit.members.models import MemberScopeAssignment


def member_scope_predicate(*, actor_user, permission):
    assignments = MemberScopeAssignment.objects.filter(
        user=actor_user, permission_code=permission
    )
    predicate = Q(pk__in=[])
    if assignments.filter(scope_type="global").exists():
        return Q()
    if assignments.filter(scope_type="created_by").exists():
        predicate |= Q(created_by_user=actor_user)
    assigned_ids = assignments.filter(scope_type="assigned").values("member_id")
    predicate |= Q(member_id__in=assigned_ids)
    team_ids = actor_user.team_memberships.filter(
        status="active", team__status="active"
    ).values("team_id")
    team_member_ids = assignments.filter(
        scope_type="team", team_id__in=team_ids
    ).values("member_id")
    predicate |= Q(member_id__in=team_member_ids)
    # Source §25.1 explicitly retains Field Officer-style creator ownership for registry reads and
    # ordinary updates. High-risk checker actions require an explicit assignment.
    if permission in {"members.member.read", "members.member.update"}:
        predicate |= Q(created_by_user=actor_user)
    return predicate


def evaluate_member_authority(*, actor_user, member, permission):
    """Return the single member-owned object-authority result used by public member modules."""
    if permission not in auth_service.effective_permission_codes(actor_user):
        return ObjectAccessResult(False, "missing_permission", "FORBIDDEN", permission)
    allowed = member.__class__.objects.filter(
        member_id=member.member_id
    ).filter(member_scope_predicate(actor_user=actor_user, permission=permission)).exists()
    return ObjectAccessResult(
        allowed,
        "member_scope_assignment" if allowed else "object_scope_denied",
        None if allowed else "OBJECT_ACCESS_DENIED",
        permission,
    )
