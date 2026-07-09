import hashlib
import hmac
import re
from datetime import date
from math import ceil

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.dateparse import parse_date

from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.members.models import Member, Nominee


MEMBER_READ_PERMISSION = "members.member.read"
NOMINEE_READ_PERMISSION = "members.nominee.read"
NOMINEE_CREATE_PERMISSION = "members.nominee.create"
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


def user_can_read_nominees(user):
    return NOMINEE_READ_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_create_nominees(user):
    return NOMINEE_CREATE_PERMISSION in auth_service.effective_permission_codes(user)


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


def serialize_member_profile(member, user):
    return {
        **serialize_member(member),
        "membership_start_date": (
            member.membership_start_date.isoformat()
            if member.membership_start_date
            else None
        ),
        "pan": {"masked": _mask_last_four(member.pan_encrypted), "can_view_full": False},
        "aadhaar": {
            "masked": _mask_last_four(member.aadhaar_encrypted),
            "can_view_full": False,
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
        "available_actions": _available_actions(member, user),
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
        pan_encrypted=_protected_identity_token(values["pan"], 10),
        pan_hash=_identity_hash(values["pan"]),
        aadhaar_encrypted=_protected_identity_token(values["aadhaar"], 12),
        aadhaar_hash=_identity_hash(values["aadhaar"]),
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
            "pan_hash": nominee.pan_hash,
            "aadhaar_hash": nominee.aadhaar_hash,
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
            "masked": _mask_protected_identity(nominee.pan_encrypted, 10),
            "can_view_full": False,
        },
        "aadhaar": {
            "masked": _mask_protected_identity(nominee.aadhaar_encrypted, 12),
            "can_view_full": False,
        },
        "kyc_status": nominee.kyc_status,
        "minor_flag": nominee.minor_flag,
        "signature_required_flag": nominee.signature_required_flag,
        "created_at": nominee.created_at.isoformat().replace("+00:00", "Z"),
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


def _identity_hash(value):
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _protected_identity_token(value, expected_length):
    digest = _identity_hash(f"enc:{value}")
    return f"enc:v1:{expected_length}:{digest}:{value[-4:]}"


def _mask_protected_identity(token, default_length):
    parts = str(token or "").split(":")
    if len(parts) == 5 and parts[0] == "enc" and parts[1] == "v1":
        try:
            length = int(parts[2])
        except ValueError:
            length = default_length
        return f"{'*' * max(length - 4, 0)}{parts[4]}"
    return _mask_last_four(token)


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
    required_permission = "applications.loan_application.create"
    permissions = auth_service.effective_permission_codes(user)
    enabled = (
        required_permission in permissions
        and member.membership_status == "active"
        and member.kyc_status == "verified"
        and member.default_status == "no_default"
    )
    return [
        {
            "action_code": "create_loan_application",
            "label": "Start Application",
            "enabled": enabled,
            "disabled_reason": None if enabled else "Member is not currently eligible for this action.",
            "required_permission": required_permission,
        }
    ]


__all__ = [
    "MEMBER_READ_PERMISSION",
    "NOMINEE_CREATE_PERMISSION",
    "NOMINEE_READ_PERMISSION",
    "NomineeValidationError",
    "create_nominee",
    "get_accessible_member",
    "get_member_profile",
    "paginated_nominees",
    "paginated_members",
    "serialize_nominee",
    "serialize_member_profile",
    "user_can_create_nominees",
    "user_can_read_members",
    "user_can_read_nominees",
    "validation_field_errors",
]
