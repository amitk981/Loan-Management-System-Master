import re
import uuid
from datetime import date
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from math import ceil
from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, Sum
from django.utils import timezone
from django.utils.dateparse import parse_date

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.documents.storage import LocalDocumentStorage
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.members.models import (
    BankAccount,
    CancelledCheque,
    CropPlan,
    KycDocument,
    KycProfile,
    IndividualMemberProfile,
    LandHolding,
    Member,
    MemberChangeHistory,
    Nominee,
    ProducerInstitutionProfile,
    ProduceSupplyRecord,
    Shareholding,
)
from sfpcl_credit.members.protected_identity import (
    identity_hash,
    mask_protected_identity,
    protected_identity_token,
)


MEMBER_READ_PERMISSION = "members.member.read"
MEMBER_CREATE_PERMISSION = "members.member.create"
MEMBER_UPDATE_PERMISSION = "members.member.update"
NOMINEE_READ_PERMISSION = "members.nominee.read"
NOMINEE_CREATE_PERMISSION = "members.nominee.create"
SHAREHOLDING_READ_PERMISSION = "members.shareholding.read"
SHAREHOLDING_CREATE_PERMISSION = "members.shareholding.create"
LAND_CROP_READ_PERMISSION = MEMBER_READ_PERMISSION
LAND_CROP_CREATE_PERMISSION = "members.member.update"
BANK_METADATA_READ_PERMISSION = MEMBER_READ_PERMISSION
BANK_METADATA_CREATE_PERMISSION = "members.member.update"
KYC_PROFILE_READ_PERMISSION = "kyc.profile.read"
KYC_PROFILE_CREATE_PERMISSION = "kyc.profile.create"
KYC_PROFILE_UPDATE_PERMISSION = "kyc.profile.update"
KYC_DOCUMENT_UPLOAD_PERMISSION = "kyc.document.upload"
KYC_DOCUMENT_VERIFY_PERMISSION = "kyc.document.verify"
PRODUCE_SUPPLY_CAPTURE_PERMISSION = "members.active_status.calculate"
PRODUCE_SUPPLY_VERIFY_PERMISSION = "members.active_status.verify"
REVEAL_FIELD_PERMISSIONS = {
    "pan": "members.sensitive.reveal_pan",
    "aadhaar": "members.sensitive.reveal_aadhaar",
}
_SENSITIVE_REVEAL_TTL_MINUTES = 5
_DEFAULT_PAGE_SIZE = 20
_MAX_PAGE_SIZE = 100
_LEGAL_MAJORITY_AGE = 18
_PAN_RE = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
_AADHAAR_RE = re.compile(r"^[0-9]{12}$")
_ALLOWED_PARAMS = {
    "search",
    "member_type",
    "membership_status",
    "kyc_status",
    "default_status",
    "page",
    "page_size",
}


def user_can_read_members(user):
    return MEMBER_READ_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_capture_produce_supply(user):
    return PRODUCE_SUPPLY_CAPTURE_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_verify_produce_supply(user):
    return PRODUCE_SUPPLY_VERIFY_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_create_members(user):
    return MEMBER_CREATE_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_update_members(user):
    return MEMBER_UPDATE_PERMISSION in auth_service.effective_permission_codes(user)


def _required(payload, field, errors):
    value = payload.get(field)
    if value is None or value == "":
        errors[field] = "This field is required."
    return value


def _masked_change(field, value):
    if field in {"pan", "aadhaar", "authorised_signatory_pan", "authorised_signatory_aadhaar"}:
        return mask_protected_identity(protected_identity_token(value, len(value)), len(value))
    return value


def _masked_payload(value, key=""):
    if isinstance(value, dict):
        return {child: _masked_payload(item, child) for child, item in value.items()}
    return _masked_change(key, value)


@transaction.atomic
def create_member(payload, actor_user, request_ip_value="", request_user_agent_value=""):
    allowed = {
        "member_type", "legal_name", "display_name", "folio_number",
        "membership_start_date", "pan", "aadhaar", "registered_address",
        "mobile_number", "email", "individual_profile", "producer_institution_profile",
    }
    errors = {key: "Unknown field." for key in payload if key not in allowed}
    member_type = _required(payload, "member_type", errors)
    legal_name = _required(payload, "legal_name", errors)
    display_name = _required(payload, "display_name", errors)
    folio = _required(payload, "folio_number", errors)
    pan = _required(payload, "pan", errors)
    aadhaar = payload.get("aadhaar", "")
    address = payload.get("registered_address")
    if not isinstance(address, dict):
        errors["registered_address"] = "This field must be an object."
        address = {}
    if member_type not in Member.MEMBER_TYPES:
        errors["member_type"] = "Unsupported member type."
    if pan and not _PAN_RE.fullmatch(pan):
        errors["pan"] = "Invalid PAN format."
    if member_type == "individual_farmer" and not aadhaar:
        errors["aadhaar"] = "This field is required for an individual farmer."
    if aadhaar and not _AADHAAR_RE.fullmatch(aadhaar):
        errors["aadhaar"] = "Invalid Aadhaar format."
    if pan and Member.objects.filter(pan_hash=identity_hash(pan), is_deleted=False).exists():
        errors["pan"] = "A member with this PAN already exists."
    if aadhaar and Member.objects.filter(aadhaar_hash=identity_hash(aadhaar), is_deleted=False).exists():
        errors["aadhaar"] = "A member with this Aadhaar already exists."
    profile_payload = (
        payload.get("individual_profile") if member_type == "individual_farmer"
        else payload.get("producer_institution_profile")
    )
    if not isinstance(profile_payload, dict):
        errors[
            "individual_profile" if member_type == "individual_farmer"
            else "producer_institution_profile"
        ] = "This field must be an object."
        profile_payload = {}
    if errors:
        raise ValidationError(errors)
    member = Member.objects.create(
        member_type=member_type, legal_name=legal_name, display_name=display_name,
        folio_number=folio,
        membership_start_date=(
            parse_date(payload["membership_start_date"])
            if payload.get("membership_start_date") else None
        ),
        membership_status="pending_verification",
        pan_encrypted=protected_identity_token(pan, 10), pan_hash=identity_hash(pan),
        aadhaar_encrypted=protected_identity_token(aadhaar, 12) if aadhaar else "",
        aadhaar_hash=identity_hash(aadhaar) if aadhaar else "",
        registered_address_line1=address.get("line1", ""),
        registered_address_line2=address.get("line2", ""),
        registered_village_city=address.get("village_city", ""),
        registered_district=address.get("district", ""),
        registered_state=address.get("state", ""),
        registered_pincode=address.get("pincode", ""),
        mobile_number=payload.get("mobile_number", ""), email=payload.get("email", ""),
        kyc_status="pending", default_status="no_default", created_by_user=actor_user,
    )
    if member_type == "individual_farmer":
        IndividualMemberProfile.objects.create(member=member, **profile_payload)
    else:
        signatory_pan = profile_payload.get("authorised_signatory_pan", "")
        signatory_aadhaar = profile_payload.get("authorised_signatory_aadhaar", "")
        clean_profile = {k: v for k, v in profile_payload.items() if k not in {
            "authorised_signatory_pan", "authorised_signatory_aadhaar"
        }}
        clean_profile.update({
            "authorised_signatory_pan_encrypted": protected_identity_token(signatory_pan, 10) if signatory_pan else "",
            "authorised_signatory_pan_hash": identity_hash(signatory_pan) if signatory_pan else "",
            "authorised_signatory_aadhaar_encrypted": protected_identity_token(signatory_aadhaar, 12) if signatory_aadhaar else "",
            "authorised_signatory_aadhaar_hash": identity_hash(signatory_aadhaar) if signatory_aadhaar else "",
        })
        ProducerInstitutionProfile.objects.create(member=member, **clean_profile)
    changed = sorted(payload.keys())
    safe_new = {key: _masked_payload(value, key) for key, value in payload.items()}
    safe_new["pan"] = _masked_change("pan", pan)
    if aadhaar:
        safe_new["aadhaar"] = _masked_change("aadhaar", aadhaar)
    MemberChangeHistory.objects.create(
        member=member, actor_user=actor_user, change_type="create",
        changed_fields=changed, new_value_json=safe_new,
    )
    AuditLog.objects.create(
        actor_user=actor_user, action="members.member.created", entity_type="member",
        entity_id=member.member_id,
        new_value_json={"member_id": str(member.member_id), "changed_fields": changed},
        ip_address=request_ip_value, user_agent=request_user_agent_value,
    )
    return member


class MemberWriteConflict(Exception):
    def __init__(self, code, message, field_errors=None, audit_rejection=False):
        self.code = code
        self.message = message
        self.field_errors = field_errors or {}
        self.audit_rejection = audit_rejection


_PATCH_FIELDS = {"legal_name", "display_name", "membership_start_date", "registered_address", "mobile_number", "email", "version"}
_IDENTITY_FIELDS = {"pan", "aadhaar"}


def _safe_member_values(member, fields):
    result = {}
    for field in fields:
        if field in _IDENTITY_FIELDS:
            result[field] = mask_protected_identity(getattr(member, f"{field}_encrypted"), 10 if field == "pan" else 12)
        elif field == "registered_address":
            result[field] = {
                "line1": member.registered_address_line1, "line2": member.registered_address_line2,
                "village_city": member.registered_village_city, "district": member.registered_district,
                "state": member.registered_state, "pincode": member.registered_pincode,
            }
        elif field == "membership_start_date":
            value = member.membership_start_date
            result[field] = value.isoformat() if value else None
        else:
            result[field] = getattr(member, field, None)
    return result


@transaction.atomic
def update_member(member_id, payload, actor_user, *, reverification=False, request_ip_value="", request_user_agent_value=""):
    member = Member.objects.select_for_update().filter(member_id=member_id, is_deleted=False).first()
    if member is None:
        return None
    version = payload.get("version")
    if not isinstance(version, int):
        raise ValidationError({"version": "Current integer version is required."})
    if version != member.version:
        raise MemberWriteConflict("STALE_WRITE", "Member has changed; refresh and retry.", {"version": "Version is stale."})
    allowed = (_PATCH_FIELDS | _IDENTITY_FIELDS | {"reason"}) if reverification else (_PATCH_FIELDS | _IDENTITY_FIELDS)
    errors = {key: "Unknown field." for key in payload if key not in allowed}
    identity_changes = sorted(field for field in _IDENTITY_FIELDS if field in payload)
    if identity_changes and member.kyc_status == "verified" and not reverification:
        raise MemberWriteConflict(
            "VERIFIED_IDENTITY_LOCKED", "Verified identity fields require reverification.",
            {field: "Verified identity field is locked." for field in identity_changes}, True,
        )
    reason = payload.get("reason", "")
    if reverification and (not identity_changes or not isinstance(reason, str) or not reason.strip()):
        errors["reason" if identity_changes else "pan"] = "A reason and at least one identity field are required."
    for field in identity_changes:
        value = payload[field]
        regex = _PAN_RE if field == "pan" else _AADHAAR_RE
        if not isinstance(value, str) or not regex.fullmatch(value):
            errors[field] = f"Invalid {field.upper()} format."
    if errors:
        raise ValidationError(errors)
    changed = sorted(key for key in payload if key not in {"version", "reason"})
    old_values = _safe_member_values(member, changed)
    address = payload.get("registered_address")
    if address is not None:
        if not isinstance(address, dict):
            raise ValidationError({"registered_address": "This field must be an object."})
        for key, model_field in {
            "line1": "registered_address_line1", "line2": "registered_address_line2",
            "village_city": "registered_village_city", "district": "registered_district",
            "state": "registered_state", "pincode": "registered_pincode",
        }.items():
            if key in address:
                setattr(member, model_field, address[key])
    for field in changed:
        if field == "registered_address":
            continue
        if field in _IDENTITY_FIELDS:
            setattr(member, f"{field}_encrypted", protected_identity_token(payload[field], 10 if field == "pan" else 12))
            setattr(member, f"{field}_hash", identity_hash(payload[field]))
        elif field == "membership_start_date":
            member.membership_start_date = parse_date(payload[field]) if payload[field] else None
        else:
            setattr(member, field, payload[field])
    if reverification:
        member.kyc_status = "pending"
        member.rekyc_due_date = None
    member.version += 1
    member.updated_by_user = actor_user
    member.updated_at = timezone.now()
    member.save()
    new_values = _safe_member_values(member, changed)
    change_type = "reverification" if reverification else "update"
    MemberChangeHistory.objects.create(
        member=member, actor_user=actor_user, change_type=change_type,
        changed_fields=changed, old_value_json=old_values, new_value_json=new_values,
        reason=reason.strip() if reverification else "",
    )
    AuditLog.objects.create(
        actor_user=actor_user,
        action="members.member.reverification_triggered" if reverification else "members.member.updated",
        entity_type="member", entity_id=member.member_id,
        old_value_json={"changed_fields": changed},
        new_value_json={"member_id": str(member.member_id), "changed_fields": changed, "kyc_status": member.kyc_status},
        ip_address=request_ip_value, user_agent=request_user_agent_value,
    )
    return member


def audit_identity_change_rejected(actor_user, member_id, fields, request_ip_value="", request_user_agent_value=""):
    AuditLog.objects.create(
        actor_user=actor_user, action="members.member.identity_change_rejected",
        entity_type="member", entity_id=member_id,
        new_value_json={"member_id": str(member_id), "fields": fields, "reason": "verified_identity_locked"},
        ip_address=request_ip_value, user_agent=request_user_agent_value,
    )


def user_can_read_nominees(user):
    return NOMINEE_READ_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_create_nominees(user):
    return NOMINEE_CREATE_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_read_shareholdings(user):
    return SHAREHOLDING_READ_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_create_shareholdings(user):
    return SHAREHOLDING_CREATE_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_read_land_crop(user):
    return LAND_CROP_READ_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_create_land_crop(user):
    return LAND_CROP_CREATE_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_read_bank_metadata(user):
    return BANK_METADATA_READ_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_create_bank_metadata(user):
    return BANK_METADATA_CREATE_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_read_kyc_profiles(user):
    return KYC_PROFILE_READ_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_create_kyc_profiles(user):
    return KYC_PROFILE_CREATE_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_update_kyc_profiles(user):
    return KYC_PROFILE_UPDATE_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_upload_kyc_documents(user):
    return KYC_DOCUMENT_UPLOAD_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_verify_kyc_documents(user):
    return KYC_DOCUMENT_VERIFY_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_reveal_sensitive_field(user, field_name):
    permission = REVEAL_FIELD_PERMISSIONS.get(field_name)
    return bool(permission and permission in auth_service.effective_permission_codes(user))


def validate_sensitive_reveal_payload(payload):
    field_name = payload.get("field_name")
    reason = payload.get("reason")
    errors = {}
    if field_name not in REVEAL_FIELD_PERMISSIONS:
        errors["field_name"] = "field_name must be pan or aadhaar."
    if not isinstance(reason, str) or not reason.strip():
        errors["reason"] = "Reason is required."
    if errors:
        raise ValidationError(errors)
    return field_name, reason.strip()


def paginated_members(query_params):
    filters = _validate_query(query_params)
    queryset = Member.objects.filter(is_deleted=False).order_by("display_name", "member_id")
    if filters["search"]:
        search = filters["search"]
        queryset = queryset.filter(
            Q(legal_name__icontains=search)
            | Q(display_name__icontains=search)
            | Q(folio_number__icontains=search)
            | Q(member_number__icontains=search)
        )
    for field in ("member_type", "membership_status", "kyc_status", "default_status"):
        if filters[field]:
            queryset = queryset.filter(**{field: filters[field]})

    page = _positive_int(query_params.get("page"), 1, "page")
    page_size = min(
        _positive_int(query_params.get("page_size"), _DEFAULT_PAGE_SIZE, "page_size"),
        _MAX_PAGE_SIZE,
    )
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    items = [serialize_member(row) for row in queryset[offset : offset + page_size]]
    return items, {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def serialize_member(member):
    return {
        "member_id": str(member.member_id),
        "member_number": member.member_number,
        "member_type": member.member_type,
        "legal_name": member.legal_name,
        "display_name": member.display_name,
        "folio_number": member.folio_number,
        "membership_status": member.membership_status,
        "kyc_status": member.kyc_status,
        "rekyc_due_date": member.rekyc_due_date.isoformat() if member.rekyc_due_date else None,
        "default_status": member.default_status,
        "mobile_number": _mask_mobile(member.mobile_number),
        "email": member.email or None,
        "share_summary": {
            "number_of_shares": member.number_of_shares,
            "holding_mode": member.holding_mode or None,
            "available_share_count": member.available_share_count,
        },
        "active_member_status": {
            "status": member.active_member_status or None,
            "verified_at": (
                member.active_member_verified_at.isoformat().replace("+00:00", "Z")
                if member.active_member_verified_at
                else None
            ),
        },
    }


def get_member_profile(member_id):
    try:
        return (
            Member.objects.select_related("individual_profile", "producer_institution_profile")
            .filter(is_deleted=False)
            .get(member_id=member_id)
        )
    except Member.DoesNotExist:
        return None


def get_accessible_member(member_id):
    return Member.objects.filter(is_deleted=False, member_id=member_id).first()


def sensitive_field_value(member, field_name):
    value = getattr(member, f"{field_name}_encrypted")
    if not value:
        raise ValidationError({"field_name": f"{field_name} is not available for this member."})
    return value


def audit_sensitive_reveal_denied(
    actor_user,
    member_id,
    field_name,
    reason,
    denial_reason,
    request_ip="",
    request_user_agent="",
    request_id=None,
):
    AuditLog.objects.create(
        actor_user=actor_user,
        action="members.sensitive_field.reveal_denied",
        entity_type="member",
        entity_id=member_id,
        new_value_json={
            "member_id": str(member_id) if member_id else None,
            "field_name": field_name,
            "reason": reason,
            "outcome": "denied",
            "denial_reason": denial_reason,
            "request_id": request_id,
        },
        ip_address=request_ip,
        user_agent=request_user_agent,
    )


def reveal_member_sensitive_field(
    member,
    field_name,
    reason,
    actor_user,
    request_ip="",
    request_user_agent="",
    request_id=None,
):
    expires_at = timezone.now() + timedelta(minutes=_SENSITIVE_REVEAL_TTL_MINUTES)
    value = sensitive_field_value(member, field_name)
    expires_at_value = expires_at.isoformat().replace("+00:00", "Z")
    AuditLog.objects.create(
        actor_user=actor_user,
        action="members.sensitive_field.revealed",
        entity_type="member",
        entity_id=member.member_id,
        new_value_json={
            "member_id": str(member.member_id),
            "field_name": field_name,
            "reason": reason,
            "outcome": "success",
            "request_id": request_id,
            "expires_at": expires_at_value,
        },
        ip_address=request_ip,
        user_agent=request_user_agent,
    )
    return {
        "field_name": field_name,
        "value": value,
        "expires_at": expires_at_value,
    }


def serialize_member_profile(member, user):
    pending_change = member.identity_change_requests.filter(status="pending").order_by("created_at").first()
    return {
        **serialize_member(member),
        "membership_start_date": (
            member.membership_start_date.isoformat()
            if member.membership_start_date
            else None
        ),
        "pan": {
            "masked": _mask_last_four(member.pan_encrypted),
            "can_view_full": user_can_reveal_sensitive_field(user, "pan"),
        },
        "aadhaar": {
            "masked": _mask_last_four(member.aadhaar_encrypted),
            "can_view_full": user_can_reveal_sensitive_field(user, "aadhaar"),
        },
        "registered_address": {
            "line1": member.registered_address_line1 or None,
            "line2": member.registered_address_line2 or None,
            "village_city": member.registered_village_city or None,
            "district": member.registered_district or None,
            "state": member.registered_state or None,
            "pincode": member.registered_pincode or None,
        },
        "individual_profile": _individual_profile(member),
        "producer_institution_profile": _producer_profile(member),
        "produce_supply_records": [
            serialize_produce_supply_record(row, user)
            for row in member.produce_supply_records.all()
        ],
        "available_actions": _available_actions(member, user),
        "pending_identity_change": ({"identity_change_request_id": str(pending_change.identity_change_request_id), "status": pending_change.status} if pending_change else None),
        "version": member.version,
    }


def validation_field_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": str(exc)}


class NomineeValidationError(Exception):
    def __init__(self, code, message, field_errors=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.field_errors = field_errors or {}


class ProduceSupplyConflict(Exception):
    def __init__(self, code, message, field_errors=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.field_errors = field_errors or {}


def paginated_nominees(member, query_params):
    page = _positive_int(query_params.get("page"), 1, "page")
    page_size = min(
        _positive_int(query_params.get("page_size"), _DEFAULT_PAGE_SIZE, "page_size"),
        _MAX_PAGE_SIZE,
    )
    queryset = member.nominees.order_by("created_at", "nominee_id")
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    items = [serialize_nominee(row) for row in queryset[offset : offset + page_size]]
    return items, {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def create_nominee(member, payload, actor_user, request_ip="", request_user_agent=""):
    values = _validated_nominee_payload(payload)
    nominee = Nominee.objects.create(
        member=member,
        nominee_name=values["nominee_name"],
        date_of_birth=values["date_of_birth"],
        age_at_application=values["age_at_application"],
        gender=values["gender"],
        relationship_to_borrower=values["relationship_to_borrower"],
        pan_encrypted=protected_identity_token(values["pan"], 10),
        pan_hash=identity_hash(values["pan"]),
        aadhaar_encrypted=protected_identity_token(values["aadhaar"], 12),
        aadhaar_hash=identity_hash(values["aadhaar"]),
        kyc_status="pending",
        minor_flag=False,
        signature_required_flag=values["signature_required_flag"],
    )
    AuditLog.objects.create(
        actor_user=actor_user,
        action="members.nominee.created",
        entity_type="nominee",
        entity_id=nominee.nominee_id,
        new_value_json={
            "member_id": str(member.member_id),
            "nominee_id": str(nominee.nominee_id),
            "nominee_name": nominee.nominee_name,
            "age_at_application": nominee.age_at_application,
            "minor_flag": nominee.minor_flag,
            "kyc_status": nominee.kyc_status,
            "signature_required_flag": nominee.signature_required_flag,
        },
        ip_address=request_ip,
        user_agent=request_user_agent,
    )
    return nominee


def serialize_nominee(nominee):
    return {
        "nominee_id": str(nominee.nominee_id),
        "nominee_name": nominee.nominee_name,
        "date_of_birth": nominee.date_of_birth.isoformat() if nominee.date_of_birth else None,
        "age_at_application": nominee.age_at_application,
        "gender": nominee.gender,
        "relationship_to_borrower": nominee.relationship_to_borrower or None,
        "pan": {
            "masked": mask_protected_identity(nominee.pan_encrypted, 10),
            "can_view_full": False,
        },
        "aadhaar": {
            "masked": mask_protected_identity(nominee.aadhaar_encrypted, 12),
            "can_view_full": False,
        },
        "kyc_status": nominee.kyc_status,
        "minor_flag": nominee.minor_flag,
        "signature_required_flag": nominee.signature_required_flag,
        "created_at": nominee.created_at.isoformat().replace("+00:00", "Z"),
    }


def paginated_shareholdings(member, query_params):
    page = _positive_int(query_params.get("page"), 1, "page")
    page_size = min(
        _positive_int(query_params.get("page_size"), _DEFAULT_PAGE_SIZE, "page_size"),
        _MAX_PAGE_SIZE,
    )
    queryset = member.shareholdings.order_by("created_at", "shareholding_id")
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    items = [serialize_shareholding(row) for row in queryset[offset : offset + page_size]]
    return items, {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def create_shareholding(member, payload, actor_user, request_ip="", request_user_agent=""):
    values = _validated_shareholding_payload(payload)
    shareholding = Shareholding.objects.create(
        member=member,
        folio_number=values["folio_number"],
        number_of_shares=values["number_of_shares"],
        holding_mode=values["holding_mode"],
        demat_account_id=values["demat_account_id"],
        latest_share_valuation_id=values["latest_share_valuation_id"],
        valuation_per_share=values["valuation_per_share"],
        valuation_effective_date=values["valuation_effective_date"],
        pledged_share_count=values["pledged_share_count"],
        available_share_count=values["available_share_count"],
        future_shares_pledge_flag=values["future_shares_pledge_flag"],
        status="active",
    )
    _refresh_member_share_summary(member)
    AuditLog.objects.create(
        actor_user=actor_user,
        action="members.shareholding.created",
        entity_type="shareholding",
        entity_id=shareholding.shareholding_id,
        new_value_json={
            "member_id": str(member.member_id),
            "shareholding_id": str(shareholding.shareholding_id),
            "folio_number": shareholding.folio_number,
            "number_of_shares": shareholding.number_of_shares,
            "holding_mode": shareholding.holding_mode,
            "pledged_share_count": shareholding.pledged_share_count,
            "available_share_count": shareholding.available_share_count,
            "future_shares_pledge_flag": shareholding.future_shares_pledge_flag,
            "status": shareholding.status,
        },
        ip_address=request_ip,
        user_agent=request_user_agent,
    )
    return shareholding


def create_produce_supply_record(member, payload, actor_user, request_ip="", request_user_agent=""):
    required = ("financial_year", "supplied_to_entity_type", "supply_route")
    errors = {field: "This field is required." for field in required if not payload.get(field)}
    if errors:
        raise ValidationError(errors)
    record = ProduceSupplyRecord.objects.create(
        member=member,
        financial_year=payload["financial_year"],
        supplied_to_entity_type=payload["supplied_to_entity_type"],
        supplied_to_entity_id=payload.get("supplied_to_entity_id") or None,
        supply_route=payload["supply_route"],
        producer_institution_member_id=payload.get("producer_institution_member_id") or None,
        crop_type=payload.get("crop_type", ""),
        quantity=payload.get("quantity") or None,
        value_amount=payload.get("value_amount") or None,
        evidence_reference=payload.get("evidence_reference", ""),
        captured_by_user=actor_user,
    )
    record.refresh_from_db()
    projection = {
        "member_id": str(member.member_id),
        "financial_year": record.financial_year,
        "verification_status": "pending",
        "captured_by_user_id": str(actor_user.user_id),
        "verified_by_user_id": None,
    }
    MemberChangeHistory.objects.create(
        member=member, actor_user=actor_user, change_type="produce_supply_captured",
        changed_fields=["produce_supply"], new_value_json=projection,
    )
    AuditLog.objects.create(
        actor_user=actor_user, action="members.produce_supply.created",
        entity_type="produce_supply_record", entity_id=record.produce_supply_record_id,
        new_value_json=projection, ip_address=request_ip, user_agent=request_user_agent,
    )
    return record


def serialize_produce_supply_record(record, user=None, portal=False):
    can_verify = bool(user and user_can_verify_produce_supply(user))
    maker = bool(user and record.captured_by_user_id == user.user_id)
    action = {
        "action_code": PRODUCE_SUPPLY_VERIFY_PERMISSION,
        "label": "Verify supply record",
        "enabled": can_verify and not maker and not record.verified_flag,
        "disabled_reason": None,
        "required_permission": PRODUCE_SUPPLY_VERIFY_PERMISSION,
        "required_role": None,
    }
    if maker:
        action["disabled_reason"] = "The record maker cannot verify this supply record."
    elif record.verified_flag:
        action["disabled_reason"] = "This supply record is already verified."
    elif not can_verify:
        action["disabled_reason"] = "Missing supply verification permission."
    data = {
        "produce_supply_record_id": str(record.produce_supply_record_id),
        "member_id": str(record.member_id),
        "financial_year": record.financial_year,
        "supplied_to_entity_type": record.supplied_to_entity_type,
        "supplied_to_entity_id": str(record.supplied_to_entity_id) if record.supplied_to_entity_id else None,
        "supply_route": record.supply_route,
        "producer_institution_member_id": str(record.producer_institution_member_id) if record.producer_institution_member_id else None,
        "crop_type": record.crop_type or None,
        "quantity": f"{record.quantity:.3f}" if record.quantity is not None else None,
        "value_amount": f"{record.value_amount:.2f}" if record.value_amount is not None else None,
        "evidence_reference": record.evidence_reference or None,
        "verified_flag": record.verified_flag,
        "verified_by_user_id": str(record.verified_by_user_id) if record.verified_by_user_id else None,
        "verified_at": record.verified_at.isoformat().replace("+00:00", "Z") if record.verified_at else None,
        "version": record.version,
    }
    if not portal:
        data["available_actions"] = [action]
    return data


@transaction.atomic
def verify_produce_supply_record(record_id, version, actor_user, request_ip="", request_user_agent=""):
    record = ProduceSupplyRecord.objects.select_for_update().filter(
        produce_supply_record_id=record_id
    ).first()
    if record is None:
        return None
    if record.captured_by_user_id == actor_user.user_id:
        raise PermissionError("The record maker cannot verify this supply record.")
    if not user_can_verify_produce_supply(actor_user):
        raise PermissionError("You do not have permission to verify produce supply records.")
    try:
        supplied_version = int(version)
    except (TypeError, ValueError):
        raise ValidationError({"version": "A valid version is required."})
    if supplied_version != record.version:
        raise ProduceSupplyConflict("STALE_WRITE", "Supply record has changed; refresh and retry.", {"version": "Version is stale."})
    if record.verified_flag:
        raise ProduceSupplyConflict("INVALID_STATE_TRANSITION", "Supply record is already verified.")
    instant = timezone.now()
    record.verified_flag = True
    record.verified_by_user = actor_user
    record.verified_at = instant
    record.version += 1
    record.save(update_fields=["verified_flag", "verified_by_user", "verified_at", "version"])
    projection = {
        "member_id": str(record.member_id), "financial_year": record.financial_year,
        "verification_status": "verified",
        "captured_by_user_id": str(record.captured_by_user_id),
        "verified_by_user_id": str(actor_user.user_id),
    }
    MemberChangeHistory.objects.create(
        member=record.member, actor_user=actor_user, change_type="produce_supply_verified",
        changed_fields=["produce_supply_verification"], new_value_json=projection,
    )
    AuditLog.objects.create(
        actor_user=actor_user, action="members.produce_supply.verified",
        entity_type="produce_supply_record", entity_id=record.produce_supply_record_id,
        new_value_json=projection, ip_address=request_ip, user_agent=request_user_agent,
    )
    return record


def serialize_shareholding(shareholding):
    return {
        "shareholding_id": str(shareholding.shareholding_id),
        "folio_number": shareholding.folio_number,
        "number_of_shares": shareholding.number_of_shares,
        "holding_mode": shareholding.holding_mode,
        "valuation_per_share": (
            f"{shareholding.valuation_per_share:.2f}"
            if shareholding.valuation_per_share is not None
            else None
        ),
        "valuation_effective_date": (
            shareholding.valuation_effective_date.isoformat()
            if shareholding.valuation_effective_date
            else None
        ),
        "pledged_share_count": shareholding.pledged_share_count,
        "available_share_count": shareholding.available_share_count,
        "future_shares_pledge_flag": shareholding.future_shares_pledge_flag,
        "status": shareholding.status,
    }


def paginated_land_holdings(member, query_params):
    page = _positive_int(query_params.get("page"), 1, "page")
    page_size = min(
        _positive_int(query_params.get("page_size"), _DEFAULT_PAGE_SIZE, "page_size"),
        _MAX_PAGE_SIZE,
    )
    queryset = member.land_holdings.order_by("created_at", "land_holding_id")
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    items = [serialize_land_holding(row) for row in queryset[offset : offset + page_size]]
    return items, {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def create_land_holding(member, payload, actor_user, request_ip="", request_user_agent=""):
    values = _validated_land_holding_payload(payload)
    land_holding = LandHolding.objects.create(
        member=member,
        document_type=values["document_type"],
        survey_number=values["survey_number"],
        village=values["village"],
        taluka=values["taluka"],
        district=values["district"],
        state=values["state"],
        area_acres=values["area_acres"],
        document_id=values["document_id"],
        verification_status="pending",
    )
    AuditLog.objects.create(
        actor_user=actor_user,
        action="members.land_holding.created",
        entity_type="land_holding",
        entity_id=land_holding.land_holding_id,
        new_value_json={
            "member_id": str(member.member_id),
            "land_holding_id": str(land_holding.land_holding_id),
            "document_type": land_holding.document_type,
            "survey_number": land_holding.survey_number,
            "area_acres": f"{land_holding.area_acres:.2f}",
            "document_id": str(land_holding.document_id),
            "verification_status": land_holding.verification_status,
        },
        ip_address=request_ip,
        user_agent=request_user_agent,
    )
    return land_holding


def serialize_land_holding(land_holding):
    return {
        "land_holding_id": str(land_holding.land_holding_id),
        "document_type": land_holding.document_type,
        "survey_number": land_holding.survey_number or None,
        "village": land_holding.village or None,
        "taluka": land_holding.taluka or None,
        "district": land_holding.district or None,
        "state": land_holding.state or None,
        "area_acres": f"{land_holding.area_acres:.2f}",
        "document_id": str(land_holding.document_id),
        "verification_status": land_holding.verification_status,
        "verified_by_user_id": (
            str(land_holding.verified_by_user_id)
            if land_holding.verified_by_user_id
            else None
        ),
        "verified_at": (
            land_holding.verified_at.isoformat().replace("+00:00", "Z")
            if land_holding.verified_at
            else None
        ),
        "created_at": land_holding.created_at.isoformat().replace("+00:00", "Z"),
    }


def paginated_crop_plans(member, query_params):
    page = _positive_int(query_params.get("page"), 1, "page")
    page_size = min(
        _positive_int(query_params.get("page_size"), _DEFAULT_PAGE_SIZE, "page_size"),
        _MAX_PAGE_SIZE,
    )
    queryset = member.crop_plans.order_by("created_at", "crop_plan_id")
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    items = [serialize_crop_plan(row) for row in queryset[offset : offset + page_size]]
    return items, {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def create_crop_plan(member, payload, actor_user, request_ip="", request_user_agent=""):
    values = _validated_crop_plan_payload(payload)
    crop_plan = CropPlan.objects.create(
        member=member,
        loan_application_id=values["loan_application_id"],
        crop_type=values["crop_type"],
        season=values["season"],
        planned_area_acres=values["planned_area_acres"],
        estimated_cost_amount=values["estimated_cost_amount"],
        loan_purpose_alignment=values["loan_purpose_alignment"],
        document_id=values["document_id"],
        verification_status="pending",
    )
    AuditLog.objects.create(
        actor_user=actor_user,
        action="members.crop_plan.created",
        entity_type="crop_plan",
        entity_id=crop_plan.crop_plan_id,
        new_value_json={
            "member_id": str(member.member_id),
            "crop_plan_id": str(crop_plan.crop_plan_id),
            "loan_application_id": (
                str(crop_plan.loan_application_id) if crop_plan.loan_application_id else None
            ),
            "crop_type": crop_plan.crop_type,
            "season": crop_plan.season,
            "planned_area_acres": f"{crop_plan.planned_area_acres:.2f}",
            "estimated_cost_amount": (
                f"{crop_plan.estimated_cost_amount:.2f}"
                if crop_plan.estimated_cost_amount is not None
                else None
            ),
            "loan_purpose_alignment": crop_plan.loan_purpose_alignment,
            "document_id": str(crop_plan.document_id) if crop_plan.document_id else None,
            "verification_status": crop_plan.verification_status,
        },
        ip_address=request_ip,
        user_agent=request_user_agent,
    )
    return crop_plan


def serialize_crop_plan(crop_plan):
    return {
        "crop_plan_id": str(crop_plan.crop_plan_id),
        "loan_application_id": (
            str(crop_plan.loan_application_id) if crop_plan.loan_application_id else None
        ),
        "crop_type": crop_plan.crop_type,
        "season": crop_plan.season or None,
        "planned_area_acres": f"{crop_plan.planned_area_acres:.2f}",
        "estimated_cost_amount": (
            f"{crop_plan.estimated_cost_amount:.2f}"
            if crop_plan.estimated_cost_amount is not None
            else None
        ),
        "loan_purpose_alignment": crop_plan.loan_purpose_alignment,
        "document_id": str(crop_plan.document_id) if crop_plan.document_id else None,
        "verification_status": crop_plan.verification_status,
        "verified_by_user_id": (
            str(crop_plan.verified_by_user_id) if crop_plan.verified_by_user_id else None
        ),
        "verified_at": (
            crop_plan.verified_at.isoformat().replace("+00:00", "Z")
            if crop_plan.verified_at
            else None
        ),
        "created_at": crop_plan.created_at.isoformat().replace("+00:00", "Z"),
    }


def paginated_bank_accounts(member, query_params):
    page = _positive_int(query_params.get("page"), 1, "page")
    page_size = min(
        _positive_int(query_params.get("page_size"), _DEFAULT_PAGE_SIZE, "page_size"),
        _MAX_PAGE_SIZE,
    )
    queryset = BankAccount.objects.filter(
        owner_party_type="member",
        owner_party_id=member.member_id,
    ).order_by("created_at", "bank_account_id")
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    items = [serialize_bank_account(row) for row in queryset[offset : offset + page_size]]
    return items, {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def create_bank_account(member, payload, actor_user, request_ip="", request_user_agent=""):
    values = _validated_bank_account_payload(payload)
    if values["cancelled_cheque_id"] and not member.cancelled_cheques.filter(
        cancelled_cheque_id=values["cancelled_cheque_id"]
    ).exists():
        raise ValidationError(
            {"cancelled_cheque_id": "Cancelled cheque was not found for this member."}
        )
    bank_account = BankAccount.objects.create(
        owner_party_type="member",
        owner_party_id=member.member_id,
        account_holder_name=values["account_holder_name"],
        account_number_encrypted=_protected_account_number_token(values["account_number"]),
        account_number_hash=identity_hash(values["account_number"]),
        account_number_last4=values["account_number"][-4:],
        ifsc=values["ifsc"],
        bank_name=values["bank_name"],
        branch_name=values["branch_name"],
        verification_status=values["verification_status"],
        cancelled_cheque_id=values["cancelled_cheque_id"],
        signature_verified_flag=values["signature_verified_flag"],
        status=values["status"],
    )
    AuditLog.objects.create(
        actor_user=actor_user,
        action="members.bank_account.created",
        entity_type="bank_account",
        entity_id=bank_account.bank_account_id,
        new_value_json={
            "member_id": str(member.member_id),
            "bank_account_id": str(bank_account.bank_account_id),
            "masked_account_number": _mask_account_last4(bank_account.account_number_last4, values["account_number_length"]),
            "account_number_last4": bank_account.account_number_last4,
            "ifsc": bank_account.ifsc,
            "verification_status": bank_account.verification_status,
            "signature_verified_flag": bank_account.signature_verified_flag,
            "status": bank_account.status,
        },
        ip_address=request_ip,
        user_agent=request_user_agent,
    )
    return bank_account


def serialize_bank_account(bank_account):
    return {
        "bank_account_id": str(bank_account.bank_account_id),
        "owner_party_type": bank_account.owner_party_type,
        "owner_party_id": str(bank_account.owner_party_id),
        "account_holder_name": bank_account.account_holder_name,
        "account_number": {
            "masked": _mask_account_last4(
                bank_account.account_number_last4,
                _protected_account_number_length(bank_account.account_number_encrypted),
            ),
            "last4": bank_account.account_number_last4 or None,
            "can_view_full": False,
        },
        "ifsc": bank_account.ifsc,
        "bank_name": bank_account.bank_name or None,
        "branch_name": bank_account.branch_name or None,
        "verification_status": bank_account.verification_status,
        "cancelled_cheque_id": (
            str(bank_account.cancelled_cheque_id)
            if bank_account.cancelled_cheque_id
            else None
        ),
        "signature_verified_flag": bank_account.signature_verified_flag,
        "status": bank_account.status,
        "created_at": bank_account.created_at.isoformat().replace("+00:00", "Z"),
    }


def paginated_cancelled_cheques(member, query_params):
    page = _positive_int(query_params.get("page"), 1, "page")
    page_size = min(
        _positive_int(query_params.get("page_size"), _DEFAULT_PAGE_SIZE, "page_size"),
        _MAX_PAGE_SIZE,
    )
    queryset = member.cancelled_cheques.order_by("created_at", "cancelled_cheque_id")
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    items = [serialize_cancelled_cheque(row) for row in queryset[offset : offset + page_size]]
    return items, {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def create_cancelled_cheque(member, payload, actor_user, request_ip="", request_user_agent=""):
    values = _validated_cancelled_cheque_payload(payload)
    cancelled_cheque = CancelledCheque.objects.create(
        loan_application_id=values["loan_application_id"],
        member=member,
        document_id=values["document_id"],
        account_number_encrypted=_protected_account_number_token(values["account_number"]),
        account_number_hash=identity_hash(values["account_number"]),
        account_number_last4=values["account_number"][-4:],
        ifsc=values["ifsc"],
        branch_name=values["branch_name"],
        verification_status=values["verification_status"],
        signature_mismatch_flag=values["signature_mismatch_flag"],
    )
    AuditLog.objects.create(
        actor_user=actor_user,
        action="members.cancelled_cheque.created",
        entity_type="cancelled_cheque",
        entity_id=cancelled_cheque.cancelled_cheque_id,
        new_value_json={
            "member_id": str(member.member_id),
            "cancelled_cheque_id": str(cancelled_cheque.cancelled_cheque_id),
            "loan_application_id": (
                str(cancelled_cheque.loan_application_id)
                if cancelled_cheque.loan_application_id
                else None
            ),
            "document_id": str(cancelled_cheque.document_id),
            "masked_account_number": _mask_account_last4(
                cancelled_cheque.account_number_last4,
                values["account_number_length"],
            ),
            "account_number_last4": cancelled_cheque.account_number_last4,
            "ifsc": cancelled_cheque.ifsc,
            "verification_status": cancelled_cheque.verification_status,
            "signature_mismatch_flag": cancelled_cheque.signature_mismatch_flag,
        },
        ip_address=request_ip,
        user_agent=request_user_agent,
    )
    return cancelled_cheque


def serialize_cancelled_cheque(cancelled_cheque):
    return {
        "cancelled_cheque_id": str(cancelled_cheque.cancelled_cheque_id),
        "loan_application_id": (
            str(cancelled_cheque.loan_application_id)
            if cancelled_cheque.loan_application_id
            else None
        ),
        "member_id": str(cancelled_cheque.member_id),
        "document_id": str(cancelled_cheque.document_id),
        "account_number": {
            "masked": _mask_account_last4(
                cancelled_cheque.account_number_last4,
                _protected_account_number_length(cancelled_cheque.account_number_encrypted),
            ),
            "last4": cancelled_cheque.account_number_last4 or None,
            "can_view_full": False,
        },
        "ifsc": cancelled_cheque.ifsc,
        "branch_name": cancelled_cheque.branch_name or None,
        "verification_status": cancelled_cheque.verification_status,
        "signature_mismatch_flag": cancelled_cheque.signature_mismatch_flag,
        "created_at": cancelled_cheque.created_at.isoformat().replace("+00:00", "Z"),
    }


def get_kyc_profile_for_member(party_type, party_id):
    if party_type != "member":
        raise ValidationError({"party_type": "Only member KYC profiles are supported."})
    parsed_party_id = _required_uuid(party_id, "party_id")
    member = get_accessible_member(parsed_party_id)
    if member is None:
        return None, None
    profile = (
        KycProfile.objects.prefetch_related("documents__document_file")
        .filter(party_type="member", party_id=member.member_id)
        .first()
    )
    return member, profile


def create_kyc_profile(payload, actor_user, request_ip="", request_user_agent=""):
    values = _validated_kyc_profile_payload(payload, partial=False)
    member = get_accessible_member(values["party_id"])
    if member is None:
        return None
    if KycProfile.objects.filter(party_type="member", party_id=member.member_id).exists():
        raise ValidationError(
            {"party_id": "A KYC profile already exists for this member."}
        )
    with transaction.atomic():
        profile = KycProfile.objects.create(
            party_type="member",
            party_id=member.member_id,
            kyc_status="pending",
            ckyc_consent_flag=values["ckyc_consent_flag"],
            beneficial_ownership_verified_flag=values[
                "beneficial_ownership_verified_flag"
            ],
            risk_rating=values["risk_rating"],
        )
        member.kyc_status = "pending"
        member.save(update_fields=["kyc_status"])
        AuditLog.objects.create(
            actor_user=actor_user,
            action="kyc.profile.created",
            entity_type="kyc_profile",
            entity_id=profile.kyc_profile_id,
            new_value_json=_kyc_profile_audit_metadata(profile),
            ip_address=request_ip,
            user_agent=request_user_agent,
        )
    return profile


def update_kyc_profile(profile_id, payload, actor_user, request_ip="", request_user_agent=""):
    profile = KycProfile.objects.filter(kyc_profile_id=profile_id).first()
    if profile is None:
        return None
    values = _validated_kyc_profile_payload(payload, partial=True)
    old_metadata = _kyc_profile_audit_metadata(profile)
    for field, value in values.items():
        setattr(profile, field, value)
    profile.updated_at = timezone.now()
    profile.save()
    AuditLog.objects.create(
        actor_user=actor_user,
        action="kyc.profile.updated",
        entity_type="kyc_profile",
        entity_id=profile.kyc_profile_id,
        old_value_json=old_metadata,
        new_value_json=_kyc_profile_audit_metadata(profile),
        ip_address=request_ip,
        user_agent=request_user_agent,
    )
    return profile


def upload_kyc_document(profile_id, request, actor_user):
    profile = KycProfile.objects.filter(kyc_profile_id=profile_id).first()
    if profile is None:
        return None
    values = _validated_kyc_document_upload(request.POST, request.FILES)
    uploaded_file = values["file"]
    storage = LocalDocumentStorage()
    stored = storage.store(uploaded_file)
    file_name = uploaded_file.name
    file_extension = Path(file_name).suffix or None
    with transaction.atomic():
        document_file = DocumentFile.objects.create(
            file_name=file_name,
            file_extension=file_extension,
            mime_type=getattr(uploaded_file, "content_type", "") or None,
            file_size_bytes=stored.file_size_bytes,
            storage_provider=stored.storage_provider,
            storage_key=stored.storage_key,
            checksum_sha256=stored.checksum_sha256,
            uploaded_by_user=actor_user,
            sensitivity_level=DocumentFile.SENSITIVITY_RESTRICTED,
        )
        kyc_document = KycDocument.objects.create(
            kyc_profile=profile,
            document_type=values["document_type"],
            document_file=document_file,
            self_attested_flag=values["self_attested_flag"],
            verification_status="pending",
        )
        AuditLog.objects.create(
            actor_user=actor_user,
            action="kyc.document.uploaded",
            entity_type="kyc_document",
            entity_id=kyc_document.kyc_document_id,
            new_value_json={
                "kyc_document_id": str(kyc_document.kyc_document_id),
                "kyc_profile_id": str(profile.kyc_profile_id),
                "party_type": profile.party_type,
                "party_id": str(profile.party_id),
                "document_type": kyc_document.document_type,
                "document_id": str(document_file.document_id),
                "self_attested_flag": kyc_document.self_attested_flag,
                "verification_status": kyc_document.verification_status,
                "file_name": document_file.file_name,
                "mime_type": document_file.mime_type,
                "file_size_bytes": document_file.file_size_bytes,
                "sensitivity_level": document_file.sensitivity_level,
            },
            ip_address=request_ip(request),
            user_agent=request_user_agent(request),
        )
    return kyc_document


def verify_kyc_document(document_id, payload, actor_user, request_ip="", request_user_agent=""):
    kyc_document = KycDocument.objects.select_related("kyc_profile").filter(
        kyc_document_id=document_id
    ).first()
    if kyc_document is None:
        return None
    profile = kyc_document.kyc_profile
    if profile.party_type == "member":
        member = Member.objects.filter(member_id=profile.party_id).first()
        if member and actor_user.pk in {member.created_by_user_id, member.updated_by_user_id}:
            AuditLog.objects.create(
                actor_user=actor_user,
                action="kyc.document.verification_denied",
                entity_type="kyc_document",
                entity_id=kyc_document.kyc_document_id,
                new_value_json={
                    "member_id": str(member.member_id),
                    "reason": "maker_checker_separation",
                },
                ip_address=request_ip,
                user_agent=request_user_agent,
            )
            raise ValidationError(
                {"verification_status": "Member maker cannot verify this member's KYC."}
            )
    status = str(payload.get("verification_status") or "").strip()
    if status not in {"verified", "rejected"}:
        raise ValidationError(
            {"verification_status": "Must be verified or rejected."}
        )
    remarks = str(payload.get("remarks") or "").strip()
    now = timezone.now()
    with transaction.atomic():
        kyc_document.verification_status = status
        kyc_document.remarks = remarks
        kyc_document.verified_by_user = actor_user
        kyc_document.verified_at = now
        kyc_document.save()

        profile = kyc_document.kyc_profile
        profile.kyc_status = status
        profile.last_verified_by_user = actor_user
        profile.last_verified_at = now if status == "verified" else None
        profile.rekyc_due_date = _two_years_after(now.date()) if status == "verified" else None
        profile.rejection_reason = remarks if status == "rejected" else None
        profile.updated_at = now
        profile.save()

        member = get_accessible_member(profile.party_id)
        if member is not None:
            member.kyc_status = status
            member.rekyc_due_date = profile.rekyc_due_date
            member.save(update_fields=["kyc_status", "rekyc_due_date"])

        AuditLog.objects.create(
            actor_user=actor_user,
            action="kyc.document.verified",
            entity_type="kyc_document",
            entity_id=kyc_document.kyc_document_id,
            new_value_json={
                "kyc_document_id": str(kyc_document.kyc_document_id),
                "kyc_profile_id": str(profile.kyc_profile_id),
                "party_type": profile.party_type,
                "party_id": str(profile.party_id),
                "document_type": kyc_document.document_type,
                "document_id": str(kyc_document.document_file_id),
                "verification_status": kyc_document.verification_status,
                "verified_by_user_id": str(actor_user.user_id),
                "verified_at": kyc_document.verified_at.isoformat().replace("+00:00", "Z"),
                "remarks": kyc_document.remarks,
                "profile_kyc_status": profile.kyc_status,
                "rekyc_due_date": (
                    profile.rekyc_due_date.isoformat() if profile.rekyc_due_date else None
                ),
            },
            ip_address=request_ip,
            user_agent=request_user_agent,
        )
    return kyc_document


def serialize_kyc_profile(profile):
    return {
        "kyc_profile_id": str(profile.kyc_profile_id),
        "party_type": profile.party_type,
        "party_id": str(profile.party_id),
        "kyc_status": profile.kyc_status,
        "ckyc_consent_flag": profile.ckyc_consent_flag,
        "beneficial_ownership_verified_flag": profile.beneficial_ownership_verified_flag,
        "risk_rating": profile.risk_rating,
        "last_verified_at": (
            profile.last_verified_at.isoformat().replace("+00:00", "Z")
            if profile.last_verified_at
            else None
        ),
        "last_verified_by_user_id": (
            str(profile.last_verified_by_user_id)
            if profile.last_verified_by_user_id
            else None
        ),
        "rekyc_due_date": profile.rekyc_due_date.isoformat() if profile.rekyc_due_date else None,
        "rejection_reason": profile.rejection_reason,
        "documents": [serialize_kyc_document(document) for document in profile.documents.all()],
    }


def serialize_kyc_document(kyc_document):
    document = kyc_document.document_file
    return {
        "kyc_document_id": str(kyc_document.kyc_document_id),
        "kyc_profile_id": str(kyc_document.kyc_profile_id),
        "document_type": kyc_document.document_type,
        "document_id": str(document.document_id),
        "file_name": document.file_name,
        "mime_type": document.mime_type,
        "file_size_bytes": document.file_size_bytes,
        "sensitivity_level": document.sensitivity_level,
        "self_attested_flag": kyc_document.self_attested_flag,
        "verification_status": kyc_document.verification_status,
        "verified_by_user_id": (
            str(kyc_document.verified_by_user_id)
            if kyc_document.verified_by_user_id
            else None
        ),
        "verified_at": (
            kyc_document.verified_at.isoformat().replace("+00:00", "Z")
            if kyc_document.verified_at
            else None
        ),
        "remarks": kyc_document.remarks,
        "created_at": kyc_document.created_at.isoformat().replace("+00:00", "Z"),
    }


def _validate_query(query_params):
    unknown = set(query_params.keys()) - _ALLOWED_PARAMS
    if unknown:
        raise ValidationError(
            {param: "Unknown query parameter." for param in sorted(unknown)}
        )

    filters = {
        "search": (query_params.get("search") or "").strip(),
        "member_type": query_params.get("member_type") or "",
        "membership_status": query_params.get("membership_status") or "",
        "kyc_status": query_params.get("kyc_status") or "",
        "default_status": query_params.get("default_status") or "",
    }
    _validate_enum(filters, "member_type", Member.MEMBER_TYPES)
    _validate_enum(filters, "membership_status", Member.MEMBERSHIP_STATUSES)
    _validate_enum(filters, "kyc_status", Member.KYC_STATUSES)
    _validate_enum(filters, "default_status", Member.DEFAULT_STATUSES)
    return filters


def _validate_enum(filters, field, allowed_values):
    value = filters[field]
    if value and value not in allowed_values:
        raise ValidationError({field: "Unsupported filter value."})


def _positive_int(value, default, field):
    if value in (None, ""):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(
            {field: "Pagination values must be positive integers."}
        ) from exc
    if parsed < 1:
        raise ValidationError({field: "Pagination values must be positive integers."})
    return parsed


def _mask_mobile(value):
    digits = "".join(char for char in (value or "") if char.isdigit())
    if not digits:
        return None
    suffix = digits[-4:]
    return f"{'*' * max(len(digits) - 4, 0)}{suffix}"


def _mask_last_four(value):
    if not value:
        return None
    text = str(value)
    return f"{'*' * max(len(text) - 4, 0)}{text[-4:]}"


def _validated_nominee_payload(payload):
    nominee_name = str(payload.get("nominee_name") or "").strip()
    gender = str(payload.get("gender") or "").strip()
    relationship = str(payload.get("relationship_to_borrower") or "").strip()
    if not nominee_name:
        raise NomineeValidationError(
            "MISSING_REQUIRED_FIELD",
            "Nominee name is required.",
            {"nominee_name": "This field is required."},
        )
    if not gender:
        raise NomineeValidationError(
            "MISSING_REQUIRED_FIELD",
            "Gender is required.",
            {"gender": "This field is required."},
        )

    date_of_birth = _required_date(payload.get("date_of_birth"))
    age = _age_on(date_of_birth, date.today())
    if age < _LEGAL_MAJORITY_AGE:
        raise NomineeValidationError(
            "NOMINEE_MINOR_NOT_ALLOWED",
            "Nominee must not be a minor.",
            {"date_of_birth": "Nominee must be at least 18 years old."},
        )

    pan = _required_identity(payload.get("pan"), "pan").upper()
    if not _PAN_RE.match(pan):
        raise NomineeValidationError(
            "INVALID_PAN_FORMAT",
            "PAN format is invalid.",
            {"pan": "PAN must match the source-defined format."},
        )

    aadhaar = _required_identity(payload.get("aadhaar"), "aadhaar").replace(" ", "")
    if not _AADHAAR_RE.match(aadhaar):
        raise NomineeValidationError(
            "INVALID_AADHAAR_FORMAT",
            "Aadhaar format is invalid.",
            {"aadhaar": "Aadhaar must be a 12 digit number."},
        )

    return {
        "nominee_name": nominee_name,
        "date_of_birth": date_of_birth,
        "age_at_application": age,
        "gender": gender,
        "relationship_to_borrower": relationship,
        "pan": pan,
        "aadhaar": aadhaar,
        "signature_required_flag": bool(payload.get("signature_required_flag", True)),
    }


def _validated_shareholding_payload(payload):
    folio_number = str(payload.get("folio_number") or "").strip()
    holding_mode = str(payload.get("holding_mode") or "").strip()
    if not folio_number:
        raise ValidationError({"folio_number": "This field is required."})
    if not holding_mode:
        raise ValidationError({"holding_mode": "This field is required."})
    if holding_mode not in Shareholding.HOLDING_MODES:
        raise ValidationError({"holding_mode": "Unsupported holding mode."})

    number_of_shares = _required_non_negative_int(
        payload.get("number_of_shares"), "number_of_shares"
    )
    pledged_share_count = _optional_non_negative_int(
        payload.get("pledged_share_count"), "pledged_share_count", 0
    )
    if pledged_share_count > number_of_shares:
        raise ValidationError(
            {"pledged_share_count": "Pledged shares cannot exceed total shares."}
        )

    return {
        "folio_number": folio_number,
        "number_of_shares": number_of_shares,
        "holding_mode": holding_mode,
        "demat_account_id": _optional_uuid(payload.get("demat_account_id"), "demat_account_id"),
        "latest_share_valuation_id": _optional_uuid(
            payload.get("latest_share_valuation_id"), "latest_share_valuation_id"
        ),
        "valuation_per_share": _optional_decimal(
            payload.get("valuation_per_share"), "valuation_per_share"
        ),
        "valuation_effective_date": _optional_date(
            payload.get("valuation_effective_date"), "valuation_effective_date"
        ),
        "pledged_share_count": pledged_share_count,
        "available_share_count": number_of_shares - pledged_share_count,
        "future_shares_pledge_flag": bool(payload.get("future_shares_pledge_flag", False)),
    }


def _validated_land_holding_payload(payload):
    document_type = str(payload.get("document_type") or "").strip()
    if not document_type:
        raise ValidationError({"document_type": "This field is required."})
    return {
        "document_type": document_type,
        "survey_number": str(payload.get("survey_number") or "").strip(),
        "village": str(payload.get("village") or "").strip(),
        "taluka": str(payload.get("taluka") or "").strip(),
        "district": str(payload.get("district") or "").strip(),
        "state": str(payload.get("state") or "").strip(),
        "area_acres": _required_positive_decimal(payload.get("area_acres"), "area_acres"),
        "document_id": _required_uuid(payload.get("document_id"), "document_id"),
    }


def _validated_crop_plan_payload(payload):
    crop_type = str(payload.get("crop_type") or "").strip()
    loan_purpose_alignment = str(payload.get("loan_purpose_alignment") or "").strip()
    if not crop_type:
        raise ValidationError({"crop_type": "This field is required."})
    if not loan_purpose_alignment:
        raise ValidationError({"loan_purpose_alignment": "This field is required."})
    return {
        "loan_application_id": _optional_uuid(
            payload.get("loan_application_id"), "loan_application_id"
        ),
        "crop_type": crop_type,
        "season": str(payload.get("season") or "").strip(),
        "planned_area_acres": _required_positive_decimal(
            payload.get("planned_area_acres"), "planned_area_acres"
        ),
        "estimated_cost_amount": _optional_decimal(
            payload.get("estimated_cost_amount"), "estimated_cost_amount"
        ),
        "loan_purpose_alignment": loan_purpose_alignment,
        "document_id": _optional_uuid(payload.get("document_id"), "document_id"),
    }


def _validated_bank_account_payload(payload):
    account_holder_name = str(payload.get("account_holder_name") or "").strip()
    ifsc = str(payload.get("ifsc") or "").strip().upper()
    verification_status = str(payload.get("verification_status") or "pending").strip()
    status = str(payload.get("status") or "active").strip()
    field_errors = {}
    if not account_holder_name:
        field_errors["account_holder_name"] = "This field is required."
    if not ifsc:
        field_errors["ifsc"] = "This field is required."
    if verification_status not in BankAccount.VERIFICATION_STATUSES:
        field_errors["verification_status"] = "Unsupported verification status."
    if status not in BankAccount.STATUSES:
        field_errors["status"] = "Unsupported bank account status."
    try:
        account_number = _required_account_number(payload.get("account_number"))
    except ValidationError as exc:
        field_errors.update(validation_field_errors(exc))
        account_number = ""
    try:
        cancelled_cheque_id = _optional_uuid(
            payload.get("cancelled_cheque_id"), "cancelled_cheque_id"
        )
    except ValidationError as exc:
        field_errors.update(validation_field_errors(exc))
        cancelled_cheque_id = None
    if field_errors:
        raise ValidationError(field_errors)
    return {
        "account_holder_name": account_holder_name,
        "account_number": account_number,
        "account_number_length": len(account_number),
        "ifsc": ifsc,
        "bank_name": str(payload.get("bank_name") or "").strip(),
        "branch_name": str(payload.get("branch_name") or "").strip(),
        "verification_status": verification_status,
        "cancelled_cheque_id": cancelled_cheque_id,
        "signature_verified_flag": _optional_bool(payload.get("signature_verified_flag")),
        "status": status,
    }


def _validated_cancelled_cheque_payload(payload):
    ifsc = str(payload.get("ifsc") or "").strip().upper()
    verification_status = str(payload.get("verification_status") or "pending").strip()
    field_errors = {}
    if not ifsc:
        field_errors["ifsc"] = "This field is required."
    if verification_status not in CancelledCheque.VERIFICATION_STATUSES:
        field_errors["verification_status"] = "Unsupported verification status."
    try:
        document_id = _required_uuid(payload.get("document_id"), "document_id")
    except ValidationError as exc:
        field_errors.update(validation_field_errors(exc))
        document_id = None
    try:
        account_number = _required_account_number(payload.get("account_number"))
    except ValidationError as exc:
        field_errors.update(validation_field_errors(exc))
        account_number = ""
    try:
        loan_application_id = _optional_uuid(
            payload.get("loan_application_id"), "loan_application_id"
        )
    except ValidationError as exc:
        field_errors.update(validation_field_errors(exc))
        loan_application_id = None
    if field_errors:
        raise ValidationError(field_errors)
    return {
        "loan_application_id": loan_application_id,
        "document_id": document_id,
        "account_number": account_number,
        "account_number_length": len(account_number),
        "ifsc": ifsc,
        "branch_name": str(payload.get("branch_name") or "").strip(),
        "verification_status": verification_status,
        "signature_mismatch_flag": bool(payload.get("signature_mismatch_flag", False)),
    }


def _validated_kyc_profile_payload(payload, partial):
    field_errors = {}
    values = {}
    if not partial or "party_type" in payload:
        party_type = str(payload.get("party_type") or "").strip()
        if party_type != "member":
            field_errors["party_type"] = "Only member KYC profiles are supported."
        values["party_type"] = party_type
    if not partial or "party_id" in payload:
        try:
            values["party_id"] = _required_uuid(payload.get("party_id"), "party_id")
        except ValidationError as exc:
            field_errors.update(validation_field_errors(exc))
    if not partial or "ckyc_consent_flag" in payload:
        if payload.get("ckyc_consent_flag") is None:
            field_errors["ckyc_consent_flag"] = "This field is required."
        else:
            values["ckyc_consent_flag"] = bool(payload.get("ckyc_consent_flag"))
    if "beneficial_ownership_verified_flag" in payload or not partial:
        raw_beneficial = payload.get("beneficial_ownership_verified_flag")
        values["beneficial_ownership_verified_flag"] = (
            None if raw_beneficial in ("", None) else bool(raw_beneficial)
        )
    if "risk_rating" in payload or not partial:
        risk_rating = str(payload.get("risk_rating") or "").strip().lower()
        if risk_rating and risk_rating not in KycProfile.RISK_RATINGS:
            field_errors["risk_rating"] = "Unsupported risk rating."
        values["risk_rating"] = risk_rating or None
    if "rejection_reason" in payload:
        values["rejection_reason"] = str(payload.get("rejection_reason") or "").strip() or None

    if partial:
        values.pop("party_type", None)
        values.pop("party_id", None)
    if field_errors:
        raise ValidationError(field_errors)
    return values


def _validated_kyc_document_upload(post_data, files):
    field_errors = {}
    document_type = str(post_data.get("document_type") or "").strip().lower()
    if not document_type:
        field_errors["document_type"] = "This field is required."
    elif document_type not in KycDocument.DOCUMENT_TYPES:
        field_errors["document_type"] = "Unsupported KYC document type."

    uploaded_file = files.get("file")
    if uploaded_file is None:
        field_errors["file"] = "This field is required."

    self_attested_flag = _parse_bool(post_data.get("self_attested_flag"))
    if (
        document_type in KycDocument.SELF_ATTESTED_REQUIRED_TYPES
        and self_attested_flag is not True
    ):
        field_errors["self_attested_flag"] = (
            "Self-attestation is required for PAN and Aadhaar."
        )
    if self_attested_flag is None:
        self_attested_flag = False

    if field_errors:
        raise ValidationError(field_errors)
    return {
        "document_type": document_type,
        "file": uploaded_file,
        "self_attested_flag": self_attested_flag,
    }


def _parse_bool(value):
    if isinstance(value, bool):
        return value
    normalized = str(value or "").strip().lower()
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off"}:
        return False
    return None


def _optional_bool(value):
    if value is None or value == "":
        return None
    parsed = _parse_bool(value)
    if parsed is None:
        return bool(value)
    return parsed


def _kyc_profile_audit_metadata(profile):
    return {
        "kyc_profile_id": str(profile.kyc_profile_id),
        "party_type": profile.party_type,
        "party_id": str(profile.party_id),
        "kyc_status": profile.kyc_status,
        "ckyc_consent_flag": profile.ckyc_consent_flag,
        "beneficial_ownership_verified_flag": profile.beneficial_ownership_verified_flag,
        "risk_rating": profile.risk_rating,
        "last_verified_at": (
            profile.last_verified_at.isoformat().replace("+00:00", "Z")
            if profile.last_verified_at
            else None
        ),
        "last_verified_by_user_id": (
            str(profile.last_verified_by_user_id)
            if profile.last_verified_by_user_id
            else None
        ),
        "rekyc_due_date": profile.rekyc_due_date.isoformat() if profile.rekyc_due_date else None,
        "rejection_reason": profile.rejection_reason,
    }


def _two_years_after(value):
    try:
        return value.replace(year=value.year + 2)
    except ValueError:
        return value.replace(month=2, day=28, year=value.year + 2)


def _required_non_negative_int(value, field):
    if value in (None, ""):
        raise ValidationError({field: "This field is required."})
    return _non_negative_int(value, field)


def _optional_non_negative_int(value, field, default):
    if value in (None, ""):
        return default
    return _non_negative_int(value, field)


def _non_negative_int(value, field):
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError({field: "Value must be a non-negative integer."}) from exc
    if parsed < 0:
        raise ValidationError({field: "Value must be a non-negative integer."})
    return parsed


def _optional_decimal(value, field):
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError({field: "Value must be a decimal amount."}) from exc


def _required_positive_decimal(value, field):
    if value in (None, ""):
        raise ValidationError({field: "This field is required."})
    parsed = _optional_decimal(value, field)
    if parsed is None or parsed <= 0:
        raise ValidationError({field: "Value must be greater than zero."})
    return parsed


def _optional_date(value, field):
    if value in (None, ""):
        return None
    parsed = parse_date(str(value))
    if parsed is None:
        raise ValidationError({field: "Value must be an ISO date."})
    return parsed


def _optional_uuid(value, field):
    if value in (None, ""):
        return None
    try:
        return uuid.UUID(str(value))
    except ValueError as exc:
        raise ValidationError({field: "Value must be a UUID."}) from exc


def _required_uuid(value, field):
    if value in (None, ""):
        raise ValidationError({field: "This field is required."})
    return _optional_uuid(value, field)


def _refresh_member_share_summary(member):
    active_shareholdings = member.shareholdings.filter(status="active")
    totals = active_shareholdings.aggregate(
        number_of_shares=Sum("number_of_shares"),
        available_share_count=Sum("available_share_count"),
    )
    modes = list(
        active_shareholdings.order_by("holding_mode")
        .values_list("holding_mode", flat=True)
        .distinct()
    )
    member.number_of_shares = totals["number_of_shares"] or 0
    member.available_share_count = totals["available_share_count"] or 0
    member.holding_mode = modes[0] if len(modes) == 1 else ("mixed" if modes else "")
    member.save(update_fields=["number_of_shares", "available_share_count", "holding_mode"])


def _required_date(value):
    if not value:
        raise NomineeValidationError(
            "MISSING_REQUIRED_FIELD",
            "Date of birth is required.",
            {"date_of_birth": "This field is required."},
        )
    parsed = parse_date(str(value))
    if parsed is None:
        raise NomineeValidationError(
            "MISSING_REQUIRED_FIELD",
            "Date of birth is required.",
            {"date_of_birth": "Enter a valid date."},
        )
    return parsed


def _required_identity(value, field):
    normalized = str(value or "").strip()
    if not normalized:
        raise NomineeValidationError(
            "MISSING_REQUIRED_FIELD",
            f"{field.capitalize()} is required.",
            {field: "This field is required."},
        )
    return normalized


def _age_on(born, today):
    before_birthday = (today.month, today.day) < (born.month, born.day)
    return today.year - born.year - int(before_birthday)


def _required_account_number(value):
    digits = "".join(char for char in str(value or "").strip() if char.isdigit())
    if not digits:
        raise ValidationError({"account_number": "This field is required."})
    if len(digits) < 4:
        raise ValidationError({"account_number": "Account number must have at least four digits."})
    return digits


def _protected_account_number_token(value):
    digest = identity_hash(f"bank-account:{value}")
    return f"enc:v1:{len(value)}:{digest}:{value[-4:]}"


def _protected_account_number_length(token):
    parts = str(token or "").split(":")
    if len(parts) == 5 and parts[0] == "enc" and parts[1] == "v1":
        try:
            return int(parts[2])
        except ValueError:
            return 4
    return len(str(token or ""))


def _mask_account_last4(last4, total_length):
    if not last4:
        return None
    return f"{'*' * max(int(total_length or 4) - 4, 0)}{last4}"


def _individual_profile(member):
    profile = getattr(member, "individual_profile", None)
    if profile is None:
        return None
    acres = profile.land_area_under_cultivation_acres
    years = profile.employment_or_service_years
    return {
        "first_name": profile.first_name,
        "middle_name": profile.middle_name or None,
        "last_name": profile.last_name,
        "gender": profile.gender or None,
        "date_of_birth": (
            profile.date_of_birth.isoformat() if profile.date_of_birth else None
        ),
        "occupation": profile.occupation or None,
        "land_area_under_cultivation_acres": f"{acres:.2f}" if acres is not None else None,
        "primary_crop": profile.primary_crop or None,
        "services_availed_flag": profile.services_availed_flag,
        "employment_or_service_years": (
            f"{years:.2f}" if years is not None else None
        ),
    }


def _producer_profile(member):
    profile = getattr(member, "producer_institution_profile", None)
    if profile is None:
        return None
    years = profile.produce_supply_years
    return {
        "institution_type": profile.institution_type,
        "registration_number": profile.registration_number or None,
        "authorised_signatory_name": profile.authorised_signatory_name,
        "board_resolution_required_flag": profile.board_resolution_required_flag,
        "services_availed_flag": profile.services_availed_flag,
        "produce_supply_years": f"{years:.2f}" if years is not None else None,
    }


def _available_actions(member, user):
    can_update = user_can_update_members(user)
    locked = member.kyc_status == "verified"
    request_pending = member.identity_change_requests.filter(status="pending").exists()
    can_approve = "members.member.identity_change.approve" in auth_service.effective_permission_codes(user)
    return [
        {
            "action_code": "members.member.update", "label": "Update member",
            "enabled": can_update, "disabled_reason": None if can_update else "Missing member update permission.",
            "required_permission": MEMBER_UPDATE_PERMISSION, "required_role": None,
        },
        {
            "action_code": "members.member.reverify_identity", "label": "Reverify identity",
            "enabled": can_update and locked and not request_pending,
            "disabled_reason": None if can_update and locked and not request_pending else ("An identity change request is already pending." if request_pending else ("Identity is not verified." if can_update else "Missing member update permission.")),
            "required_permission": MEMBER_UPDATE_PERMISSION, "required_role": None,
        },
        {
            "action_code": "members.member.identity_change.approve", "label": "Approve identity change",
            "enabled": can_approve and request_pending,
            "disabled_reason": None if can_approve and request_pending else ("No identity change request is pending." if can_approve else "Missing identity change approval permission."),
            "required_permission": "members.member.identity_change.approve", "required_role": None,
        },
    ]


__all__ = [
    "MEMBER_READ_PERMISSION",
    "NOMINEE_CREATE_PERMISSION",
    "NOMINEE_READ_PERMISSION",
    "NomineeValidationError",
    "SHAREHOLDING_CREATE_PERMISSION",
    "SHAREHOLDING_READ_PERMISSION",
    "LAND_CROP_CREATE_PERMISSION",
    "LAND_CROP_READ_PERMISSION",
    "KYC_DOCUMENT_UPLOAD_PERMISSION",
    "KYC_DOCUMENT_VERIFY_PERMISSION",
    "KYC_PROFILE_CREATE_PERMISSION",
    "KYC_PROFILE_READ_PERMISSION",
    "KYC_PROFILE_UPDATE_PERMISSION",
    "create_crop_plan",
    "create_kyc_profile",
    "create_land_holding",
    "create_nominee",
    "create_shareholding",
    "get_accessible_member",
    "get_kyc_profile_for_member",
    "get_member_profile",
    "paginated_crop_plans",
    "paginated_land_holdings",
    "paginated_nominees",
    "paginated_members",
    "paginated_shareholdings",
    "serialize_crop_plan",
    "serialize_kyc_document",
    "serialize_kyc_profile",
    "serialize_land_holding",
    "serialize_nominee",
    "serialize_member_profile",
    "serialize_shareholding",
    "user_can_create_land_crop",
    "user_can_create_kyc_profiles",
    "user_can_create_nominees",
    "user_can_create_shareholdings",
    "user_can_read_kyc_profiles",
    "user_can_read_land_crop",
    "user_can_read_members",
    "user_can_read_nominees",
    "user_can_read_shareholdings",
    "user_can_update_kyc_profiles",
    "user_can_upload_kyc_documents",
    "user_can_verify_kyc_documents",
    "update_kyc_profile",
    "upload_kyc_document",
    "verify_kyc_document",
    "validation_field_errors",
]
