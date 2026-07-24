from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.members import services
from sfpcl_credit.members.models import Member, MemberChangeHistory, MemberIdentityChangeRequest
from sfpcl_credit.members.modules.member_authority import (
    MemberObjectAccessDenied,
    evaluate_member_authority,
)
from sfpcl_credit.members.protected_identity import (
    identity_hash,
    mask_protected_identity,
    protected_identity_token,
    reveal_protected_identity,
)


class MemberRegistry:
    APPROVE_PERMISSION = "members.member.identity_change.approve"

    @staticmethod
    def _member_access(*, actor_user, member, permission):
        return evaluate_member_authority(
            actor_user=actor_user, member=member, permission=permission,
        )

    @staticmethod
    def _require_member_access(*, actor_user, member, permission):
        access = MemberRegistry._member_access(
            actor_user=actor_user, member=member, permission=permission
        )
        if not access.allowed:
            if access.reason == "missing_permission":
                raise PermissionDenied(f"Missing required permission: {permission}.")
            raise MemberObjectAccessDenied("You cannot access this member.")

    @classmethod
    def get(cls, member_id, actor_user):
        member = services._get_member_profile(member_id)
        if member is None:
            return None
        cls._require_member_access(
            actor_user=actor_user, member=member, permission=services.MEMBER_READ_PERMISSION
        )
        return member

    @staticmethod
    def create(payload, actor_user, request_ip_value="", request_user_agent_value=""):
        if not services.user_can_create_members(actor_user):
            raise PermissionDenied("You do not have permission to create members.")
        try:
            return services._create_member(payload, actor_user, request_ip_value, request_user_agent_value)
        except IntegrityError:
            errors = {}
            pan, aadhaar = payload.get("pan"), payload.get("aadhaar")
            if pan and Member.objects.filter(pan_hash=identity_hash(pan), is_deleted=False).exists():
                errors["pan"] = "A member with this PAN already exists."
            if aadhaar and Member.objects.filter(aadhaar_hash=identity_hash(aadhaar), is_deleted=False).exists():
                errors["aadhaar"] = "A member with this Aadhaar already exists."
            raise ValidationError(errors or {"identity": "PAN or Aadhaar already belongs to a member."})

    @staticmethod
    def update(member_id, payload, actor_user, request_ip_value="", request_user_agent_value=""):
        member = services._get_member_profile(member_id)
        if member is None:
            return None
        MemberRegistry._require_member_access(
            actor_user=actor_user, member=member, permission=services.MEMBER_UPDATE_PERMISSION
        )
        return services._update_member(member_id, payload, actor_user, request_ip_value=request_ip_value, request_user_agent_value=request_user_agent_value)

    @classmethod
    @transaction.atomic
    def request_identity_change(cls, member_id, payload, actor_user):
        member = Member.objects.select_for_update().filter(member_id=member_id, is_deleted=False).first()
        if member is None:
            return None
        cls._require_member_access(
            actor_user=actor_user, member=member, permission=services.MEMBER_UPDATE_PERMISSION
        )
        version = payload.get("version")
        reason = payload.get("reason")
        pan, aadhaar = payload.get("pan"), payload.get("aadhaar")
        errors = {}
        if version != member.version: errors["version"] = "Version is stale."
        if member.kyc_status != "verified": errors["member"] = "Identity changes require verified KYC."
        if not isinstance(reason, str) or not reason.strip(): errors["reason"] = "A reason is required."
        if not pan and not aadhaar: errors["pan"] = "At least one identity field is required."
        if pan and (not isinstance(pan, str) or not services._PAN_RE.fullmatch(pan)): errors["pan"] = "Invalid PAN format."
        if aadhaar and (not isinstance(aadhaar, str) or not services._AADHAAR_RE.fullmatch(aadhaar)): errors["aadhaar"] = "Invalid Aadhaar format."
        if pan and Member.objects.filter(pan_hash=identity_hash(pan), is_deleted=False).exclude(member_id=member.member_id).exists():
            errors["pan"] = "A member with this PAN already exists."
        if aadhaar and Member.objects.filter(aadhaar_hash=identity_hash(aadhaar), is_deleted=False).exclude(member_id=member.member_id).exists():
            errors["aadhaar"] = "A member with this Aadhaar already exists."
        if errors: raise ValidationError(errors)
        return MemberIdentityChangeRequest.objects.create(
            member=member, requester_user=actor_user, reason=reason.strip(), member_version=member.version,
            proposed_pan_encrypted=protected_identity_token(pan, 10) if pan else "", proposed_pan_hash=identity_hash(pan) if pan else "",
            proposed_aadhaar_encrypted=protected_identity_token(aadhaar, 12) if aadhaar else "", proposed_aadhaar_hash=identity_hash(aadhaar) if aadhaar else "",
        )

    @classmethod
    @transaction.atomic
    def approve_identity_change(cls, request_id, actor_user):
        change = MemberIdentityChangeRequest.objects.select_for_update().select_related("member").filter(identity_change_request_id=request_id).first()
        if change is None: return None
        member = Member.objects.select_for_update().get(member_id=change.member_id)
        approval = cls.evaluate_identity_approval(member, change, actor_user)
        if not approval["enabled"]:
            if approval["code"] == "OBJECT_ACCESS_DENIED":
                raise MemberObjectAccessDenied(approval["disabled_reason"])
            if approval["status"] == 403: raise PermissionDenied(approval["disabled_reason"])
            raise services.MemberWriteConflict(approval["code"], approval["disabled_reason"])
        old_values, new_values, changed = {}, {}, []
        for field, length in (("pan", 10), ("aadhaar", 12)):
            token = getattr(change, f"proposed_{field}_encrypted")
            if token:
                changed.append(field); old_values[field] = mask_protected_identity(getattr(member, f"{field}_encrypted"), length)
                setattr(member, f"{field}_encrypted", token); setattr(member, f"{field}_hash", getattr(change, f"proposed_{field}_hash"))
                if field == "aadhaar":
                    member.aadhaar_last4 = reveal_protected_identity(token, length)[-4:]
                new_values[field] = mask_protected_identity(token, length)
        member.kyc_status = "pending"; member.rekyc_due_date = None; member.version += 1
        member.updated_by_user = actor_user; member.updated_at = timezone.now()
        try:
            with transaction.atomic():
                member.save()
        except IntegrityError:
            errors = {}
            if change.proposed_pan_hash and Member.objects.filter(pan_hash=change.proposed_pan_hash, is_deleted=False).exclude(member_id=member.member_id).exists(): errors["pan"] = "A member with this PAN already exists."
            if change.proposed_aadhaar_hash and Member.objects.filter(aadhaar_hash=change.proposed_aadhaar_hash, is_deleted=False).exclude(member_id=member.member_id).exists(): errors["aadhaar"] = "A member with this Aadhaar already exists."
            raise ValidationError(errors or {"identity": "PAN or Aadhaar already belongs to a member."})
        change.status = "approved"; change.approver_user = actor_user; change.approved_at = timezone.now(); change.save()
        MemberChangeHistory.objects.create(member=member, actor_user=actor_user, change_type="identity_change_approved", changed_fields=changed, old_value_json=old_values, new_value_json=new_values, reason=change.reason)
        AuditLog.objects.create(actor_user=actor_user, action="members.member.identity_change_approved", entity_type="member", entity_id=member.member_id, new_value_json={"request_id": str(change.identity_change_request_id), "changed_fields": changed})
        return member

    @classmethod
    def evaluate_identity_approval(cls, member, change, actor_user):
        access = cls._member_access(
            actor_user=actor_user, member=member, permission=cls.APPROVE_PERMISSION
        )
        if not access.allowed:
            reason = (
                "Missing identity change approval permission."
                if access.reason == "missing_permission"
                else "You cannot access this member."
            )
            code = "FORBIDDEN" if access.reason == "missing_permission" else "OBJECT_ACCESS_DENIED"
            return {"enabled": False, "disabled_reason": reason, "status": 403, "code": code}
        if change is None or change.status != "pending":
            return {"enabled": False, "disabled_reason": "Identity change request is not pending.", "status": 409, "code": "IDENTITY_CHANGE_NOT_PENDING"}
        if change.requester_user_id == actor_user.user_id:
            return {"enabled": False, "disabled_reason": "Requester cannot approve their own change.", "status": 403, "code": "FORBIDDEN"}
        if member.version != change.member_version or member.kyc_status != "verified":
            return {"enabled": False, "disabled_reason": "Member has changed; refresh and retry.", "status": 409, "code": "STALE_WRITE"}
        return {"enabled": True, "disabled_reason": None, "status": 200, "code": None}

    @classmethod
    def identity_approval_action(cls, member, change, actor_user):
        approval = cls.evaluate_identity_approval(member, change, actor_user)
        return {
            "action_code": cls.APPROVE_PERMISSION,
            "label": "Approve identity change",
            "enabled": approval["enabled"],
            "disabled_reason": approval["disabled_reason"],
            "required_permission": cls.APPROVE_PERMISSION,
            "required_role": None,
        }
