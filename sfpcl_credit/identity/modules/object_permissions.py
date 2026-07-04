from dataclasses import dataclass
from typing import Iterable


ACCESS_ALLOWED_OWNER = "allowed_owner"
ACCESS_ALLOWED_TEAM = "allowed_team"
ACCESS_ALLOWED_GLOBAL = "allowed_global"
ACCESS_MISSING_PERMISSION = "missing_permission"
ACCESS_OWNER_MISMATCH = "owner_mismatch"
ACCESS_TEAM_MISMATCH = "team_mismatch"
ACCESS_SCOPE_UNKNOWN = "scope_unknown"

PERMISSION_DENIED = "PERMISSION_DENIED"
OBJECT_ACCESS_DENIED = "OBJECT_ACCESS_DENIED"


@dataclass(frozen=True)
class ObjectAccessResult:
    allowed: bool
    reason: str
    error_code: str | None = None
    required_permission: str | None = None
    approval_required: bool = False


def evaluate_object_access(
    *,
    actor_user_id,
    actor_team_codes: Iterable[str],
    actor_permission_codes: Iterable[str],
    required_permission: str,
    object_owner_user_id=None,
    object_team_code: str | None = None,
    allow_global: bool = False,
) -> ObjectAccessResult:
    actor_permissions = set(actor_permission_codes)
    actor_teams = set(actor_team_codes)

    if required_permission not in actor_permissions:
        return _deny(ACCESS_MISSING_PERMISSION, PERMISSION_DENIED, required_permission)

    if allow_global:
        return ObjectAccessResult(
            True,
            ACCESS_ALLOWED_GLOBAL,
            required_permission=required_permission,
        )

    if object_owner_user_id is not None and str(object_owner_user_id) == str(actor_user_id):
        return ObjectAccessResult(
            True,
            ACCESS_ALLOWED_OWNER,
            required_permission=required_permission,
        )

    if object_team_code is not None and object_team_code in actor_teams:
        return ObjectAccessResult(
            True,
            ACCESS_ALLOWED_TEAM,
            required_permission=required_permission,
        )

    if object_owner_user_id is None and object_team_code is None:
        return _deny(
            ACCESS_SCOPE_UNKNOWN,
            OBJECT_ACCESS_DENIED,
            required_permission,
            approval_required=True,
        )

    if object_owner_user_id is not None:
        return _deny(ACCESS_OWNER_MISMATCH, OBJECT_ACCESS_DENIED, required_permission)

    return _deny(ACCESS_TEAM_MISMATCH, OBJECT_ACCESS_DENIED, required_permission)


def _deny(
    reason: str,
    error_code: str,
    required_permission: str,
    approval_required: bool = False,
) -> ObjectAccessResult:
    return ObjectAccessResult(
        allowed=False,
        reason=reason,
        error_code=error_code,
        required_permission=required_permission,
        approval_required=approval_required,
    )
