from math import ceil

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from django.utils import timezone

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.identity.models import AuditLog, Role, Team, User, UserSession, UserTeamMembership


MANAGE_USERS_PERMISSION_CODES = {
    "users.user.create",
    "users.user.update",
    "users.user.disable",
}
ADMIN_SETTABLE_STATUSES = {"active", "suspended"}


def has_manage_users_permission(user):
    return bool(MANAGE_USERS_PERMISSION_CODES.intersection(auth_service.effective_permission_codes(user)))


def admin_user_payload(user):
    return {
        "user_id": str(user.user_id),
        "full_name": user.full_name,
        "email": user.email,
        "mobile_number": user.mobile_number,
        "status": user.status,
        "roles": auth_service.role_payload(user),
        "teams": auth_service.team_payload(user),
    }


def paginated_users(page, page_size):
    page = _positive_int(page, 1)
    page_size = min(_positive_int(page_size, 20), 100)
    users = User.objects.select_related("primary_role").prefetch_related(
        "team_memberships__team"
    ).order_by("full_name", "email")
    total_count = users.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    return [admin_user_payload(user) for user in users[offset : offset + page_size]], {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def get_user(user_id):
    return User.objects.select_related("primary_role").prefetch_related(
        "team_memberships__team"
    ).get(user_id=user_id)


@transaction.atomic
def assign_role(actor, request, user_id, role_code):
    if not role_code:
        raise ValidationError({"role_code": "This field is required."})
    try:
        role = Role.objects.get(role_code=role_code, status="active")
    except Role.DoesNotExist as exc:
        raise ValidationError({"role_code": "Existing active role is required."}) from exc
    user = User.objects.select_for_update().select_related("primary_role").get(user_id=user_id)
    previous_role = user.primary_role
    if _would_remove_last_active_system_admin(user, new_role=role, new_status=user.status):
        raise ValidationError(
            {
                "role_code": (
                    "Cannot change the last active system_admin user's primary role."
                )
            }
        )
    user.primary_role = role
    user.updated_at = timezone.now()
    user.updated_by_user = actor
    user.save(update_fields=["primary_role", "updated_at", "updated_by_user"])
    _audit(
        actor,
        request,
        "admin.user.role_assigned",
        user,
        {"role_code": previous_role.role_code, "role_name": previous_role.role_name},
        {"role_code": role.role_code, "role_name": role.role_name},
    )
    return admin_user_payload(get_user(user.user_id))


@transaction.atomic
def add_team(actor, request, user_id, team_code):
    if not team_code:
        raise ValidationError({"team_code": "This field is required."})
    try:
        team = Team.objects.get(team_code=team_code, status="active")
    except Team.DoesNotExist as exc:
        raise ValidationError({"team_code": "Existing active team is required."}) from exc
    user = User.objects.select_for_update().get(user_id=user_id)
    membership, created = UserTeamMembership.objects.get_or_create(
        user=user,
        team=team,
        defaults={"status": "active"},
    )
    old_value = {"team_code": team.team_code, "status": "inactive"}
    if not created and membership.status != "active":
        old_value = {"team_code": team.team_code, "status": membership.status}
        membership.status = "active"
        membership.save(update_fields=["status"])
    if created or old_value["status"] != "active":
        _audit(
            actor,
            request,
            "admin.user.team_added",
            user,
            old_value if not created else None,
            {"team_code": team.team_code, "team_name": team.team_name, "status": "active"},
        )
    return admin_user_payload(get_user(user.user_id))


@transaction.atomic
def remove_team(actor, request, user_id, team_code):
    user = User.objects.select_for_update().get(user_id=user_id)
    try:
        membership = UserTeamMembership.objects.select_related("team").get(
            user=user,
            team__team_code=team_code,
            team__status="active",
        )
    except UserTeamMembership.DoesNotExist as exc:
        raise ValidationError({"team_code": "Active team membership is required."}) from exc
    old_value = {
        "team_code": membership.team.team_code,
        "team_name": membership.team.team_name,
        "status": membership.status,
    }
    membership.status = "inactive"
    membership.save(update_fields=["status"])
    _audit(
        actor,
        request,
        "admin.user.team_removed",
        user,
        old_value,
        {
            "team_code": membership.team.team_code,
            "team_name": membership.team.team_name,
            "status": "inactive",
        },
    )
    return admin_user_payload(get_user(user.user_id))


@transaction.atomic
def set_status(actor, request, user_id, status):
    if status not in ADMIN_SETTABLE_STATUSES:
        raise ValidationError({"status": "Status must be active or suspended."})
    user = User.objects.select_for_update().select_related("primary_role").get(user_id=user_id)
    if _would_remove_last_active_system_admin(
        user,
        new_role=user.primary_role,
        new_status=status,
    ):
        raise ValidationError(
            {"status": "Cannot suspend the last active system_admin user."}
        )
    previous_status = user.status
    user.status = status
    user.updated_at = timezone.now()
    user.updated_by_user = actor
    user.save(update_fields=["status", "updated_at", "updated_by_user"])
    revoked_sessions = 0
    if status == "suspended":
        for session in UserSession.objects.filter(user=user, session_status=UserSession.ACTIVE):
            session.revoke("admin_status_suspended")
            revoked_sessions += 1
    _audit(
        actor,
        request,
        "admin.user.status_changed",
        user,
        {"status": previous_status},
        {"status": status, "revoked_sessions": revoked_sessions},
    )
    return admin_user_payload(get_user(user.user_id))


def _would_remove_last_active_system_admin(user, new_role, new_status):
    was_active_system_admin = (
        user.primary_role.role_code == "system_admin" and user.status == "active"
    )
    will_be_active_system_admin = (
        new_role.role_code == "system_admin" and new_status == "active"
    )
    if not was_active_system_admin or will_be_active_system_admin:
        return False
    remaining = User.objects.filter(
        primary_role__role_code="system_admin",
        status="active",
    ).exclude(user_id=user.user_id)
    return not remaining.exists()


def _positive_int(value, default):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def _audit(actor, request, action, user, old_value, new_value):
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action=action,
        entity_type="user",
        entity_id=user.user_id,
        old_value_json=old_value,
        new_value_json=new_value,
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )


def validation_field_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": str(exc)}


__all__ = [
    "ObjectDoesNotExist",
    "ValidationError",
    "add_team",
    "admin_user_payload",
    "assign_role",
    "get_user",
    "has_manage_users_permission",
    "paginated_users",
    "remove_team",
    "set_status",
    "validation_field_errors",
]
