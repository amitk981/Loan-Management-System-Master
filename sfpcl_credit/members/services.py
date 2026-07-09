from math import ceil

from django.core.exceptions import ValidationError
from django.db.models import Q

from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.members.models import Member


MEMBER_READ_PERMISSION = "members.member.read"
_DEFAULT_PAGE_SIZE = 20
_MAX_PAGE_SIZE = 100
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
    "get_member_profile",
    "paginated_members",
    "serialize_member_profile",
    "user_can_read_members",
    "validation_field_errors",
]
