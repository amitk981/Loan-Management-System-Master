import uuid
from datetime import datetime, time, timedelta
from decimal import Decimal, InvalidOperation
from math import ceil

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date

from sfpcl_credit.approvals.modules.read_scope import has_active_audit_read_scope
from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.configurations.models import LoanPolicyConfig, VersionHistory
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.shared.masking import redact_sensitive_mapping


LOAN_POLICY_READ_PERMISSION = "config.loan_policy.read"
LOAN_POLICY_MANAGE_PERMISSION = "config.loan_policy.manage"
VERSION_HISTORY_READ_PERMISSION = "audit.version_history.read"
LOAN_POLICY_ENTITY_TYPE = "loan_policy_config"
LOAN_POLICY_CREATED_ACTION = "config.loan_policy.created"
LOAN_POLICY_UPDATED_ACTION = "config.loan_policy.updated"
LOAN_POLICY_ACTIVATED_ACTION = "config.loan_policy.activated"

_DEFAULT_PAGE_SIZE = 20
_MAX_PAGE_SIZE = 100
_REQUIRED_CREATE_FIELDS = {
    "policy_name",
    "policy_version",
    "effective_from",
    "short_term_duration_months",
    "approval_threshold_amount",
    "default_scale_of_finance_per_acre_amount",
    "interest_rate_type",
    "rekyc_frequency_months",
    "record_retention_years",
    "grace_period_months",
    "non_intentional_extension_months",
}
_STRING_FIELDS = {
    "policy_name",
    "policy_version",
    "interest_rate_type",
    "interest_benchmark",
    "board_approval_reference",
}
_DATE_FIELDS = {"effective_from", "effective_to"}
_DECIMAL_FIELDS = {
    "approval_threshold_amount": (18, 2),
    "default_scale_of_finance_per_acre_amount": (18, 2),
    "share_limit_percentage": (8, 4),
    "per_share_cap_amount": (18, 2),
    "penal_interest_rate": (8, 4),
}
_INTEGER_FIELDS = {
    "short_term_duration_months",
    "min_secured_loan_months",
    "max_secured_loan_years",
    "rekyc_frequency_months",
    "record_retention_years",
    "grace_period_months",
    "non_intentional_extension_months",
}
_OPTIONAL_FIELDS = {
    "effective_to",
    "min_secured_loan_months",
    "max_secured_loan_years",
    "share_limit_percentage",
    "per_share_cap_amount",
    "interest_benchmark",
    "penal_interest_rate",
    "board_approval_reference",
}
_LOAN_POLICY_FIELDS = (
    "policy_name",
    "policy_version",
    "effective_from",
    "effective_to",
    "short_term_duration_months",
    "min_secured_loan_months",
    "max_secured_loan_years",
    "approval_threshold_amount",
    "default_scale_of_finance_per_acre_amount",
    "share_limit_percentage",
    "per_share_cap_amount",
    "interest_rate_type",
    "interest_benchmark",
    "penal_interest_rate",
    "rekyc_frequency_months",
    "record_retention_years",
    "grace_period_months",
    "non_intentional_extension_months",
    "board_approval_reference",
    "status",
)
_VERSION_HISTORY_UUID_FILTERS = {
    "versioned_entity_id",
    "author_user_id",
    "reviewer_user_id",
    "approver_user_id",
}
_VERSION_HISTORY_FILTER_PARAMS = {
    "versioned_entity_type",
    "created_from",
    "created_to",
    "approval",
    "application_reference",
    "loan_account_reference",
} | _VERSION_HISTORY_UUID_FILTERS
_PAGINATION_PARAMS = {"page", "page_size"}
_VERSION_HISTORY_ALLOWED_PARAMS = _VERSION_HISTORY_FILTER_PARAMS | _PAGINATION_PARAMS


class InvalidStateTransition(Exception):
    pass


def user_can_read_loan_policy(user):
    return LOAN_POLICY_READ_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_manage_loan_policy(user):
    return LOAN_POLICY_MANAGE_PERMISSION in auth_service.effective_permission_codes(user)


def user_can_read_version_histories(user):
    if VERSION_HISTORY_READ_PERMISSION not in auth_service.effective_permission_codes(user):
        return False
    if "internal_auditor" in auth_service.effective_role_codes(user):
        return has_active_audit_read_scope(user)
    return True


def serialize_loan_policy_config(config):
    return {
        "loan_policy_config_id": str(config.loan_policy_config_id),
        "policy_name": config.policy_name,
        "policy_version": config.policy_version,
        "effective_from": config.effective_from.isoformat(),
        "effective_to": config.effective_to.isoformat() if config.effective_to else None,
        "short_term_duration_months": config.short_term_duration_months,
        "min_secured_loan_months": config.min_secured_loan_months,
        "max_secured_loan_years": config.max_secured_loan_years,
        "approval_threshold_amount": str(config.approval_threshold_amount),
        "default_scale_of_finance_per_acre_amount": str(
            config.default_scale_of_finance_per_acre_amount
        ),
        "share_limit_percentage": str(config.share_limit_percentage)
        if config.share_limit_percentage is not None
        else None,
        "per_share_cap_amount": str(config.per_share_cap_amount)
        if config.per_share_cap_amount is not None
        else None,
        "interest_rate_type": config.interest_rate_type,
        "interest_benchmark": config.interest_benchmark,
        "penal_interest_rate": str(config.penal_interest_rate)
        if config.penal_interest_rate is not None
        else None,
        "rekyc_frequency_months": config.rekyc_frequency_months,
        "record_retention_years": config.record_retention_years,
        "grace_period_months": config.grace_period_months,
        "non_intentional_extension_months": (
            config.non_intentional_extension_months
        ),
        "board_approval_reference": config.board_approval_reference,
        "status": config.status,
    }


def create_loan_policy_config(user, request, payload):
    cleaned = _validate_loan_policy_payload(payload, partial=False)
    cleaned.setdefault("status", LoanPolicyConfig.STATUS_DRAFT)
    with transaction.atomic():
        config = LoanPolicyConfig.objects.create(**cleaned)
        _record_policy_audit(
            user=user,
            request=request,
            action=LOAN_POLICY_CREATED_ACTION,
            config=config,
            old_value=None,
            new_value=serialize_loan_policy_config(config),
        )
    return serialize_loan_policy_config(config)


def update_loan_policy_config(user, request, loan_policy_config_id, payload):
    config = LoanPolicyConfig.objects.get(loan_policy_config_id=loan_policy_config_id)
    if config.status != LoanPolicyConfig.STATUS_DRAFT:
        raise InvalidStateTransition("Only draft loan policy configs can be updated.")
    old_value = serialize_loan_policy_config(config)
    cleaned = _validate_loan_policy_payload(payload, partial=True, existing=config)
    for field, value in cleaned.items():
        setattr(config, field, value)
    with transaction.atomic():
        config.save(update_fields=list(cleaned.keys()))
        _record_policy_audit(
            user=user,
            request=request,
            action=LOAN_POLICY_UPDATED_ACTION,
            config=config,
            old_value=old_value,
            new_value=serialize_loan_policy_config(config),
        )
    return serialize_loan_policy_config(config)


def activate_loan_policy_config(user, request, loan_policy_config_id):
    config = LoanPolicyConfig.objects.get(loan_policy_config_id=loan_policy_config_id)
    if config.status != LoanPolicyConfig.STATUS_DRAFT:
        raise InvalidStateTransition("Only draft loan policy configs can be activated.")
    if not config.board_approval_reference:
        raise ValidationError(
            {
                "board_approval_reference": (
                    "Board approval reference is required before activation."
                )
            }
        )
    old_value = serialize_loan_policy_config(config)
    with transaction.atomic():
        previous_active = LoanPolicyConfig.objects.filter(
            status=LoanPolicyConfig.STATUS_ACTIVE
        ).exclude(loan_policy_config_id=config.loan_policy_config_id)
        retirement_date = config.effective_from - timezone_delta(days=1)
        for active_config in previous_active:
            active_config.status = LoanPolicyConfig.STATUS_RETIRED
            active_config.effective_to = retirement_date
            active_config.save(update_fields=["status", "effective_to"])

        config.status = LoanPolicyConfig.STATUS_ACTIVE
        config.save(update_fields=["status"])
        VersionHistory.objects.create(
            versioned_entity_type=LOAN_POLICY_ENTITY_TYPE,
            versioned_entity_id=config.loan_policy_config_id,
            version_number=config.policy_version,
            change_summary=f"Activated loan policy version {config.policy_version}.",
            author_user=user,
            approver_user=user,
            board_approval_reference=config.board_approval_reference,
            effective_from=config.effective_from,
            effective_to=config.effective_to,
        )
        _record_policy_audit(
            user=user,
            request=request,
            action=LOAN_POLICY_ACTIVATED_ACTION,
            config=config,
            old_value=old_value,
            new_value=serialize_loan_policy_config(config),
        )
    return serialize_loan_policy_config(config)


def paginated_loan_policy_configs(query_params):
    unknown = set(query_params.keys()) - _PAGINATION_PARAMS
    if unknown:
        raise ValidationError(
            {param: "Unknown query parameter." for param in sorted(unknown)}
        )
    queryset = LoanPolicyConfig.objects.order_by(
        "-effective_from", "-loan_policy_config_id"
    )
    page = _positive_int(query_params.get("page"), 1)
    page_size = min(
        _positive_int(query_params.get("page_size"), _DEFAULT_PAGE_SIZE),
        _MAX_PAGE_SIZE,
    )
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size

    items = [
        serialize_loan_policy_config(row) for row in queryset[offset : offset + page_size]
    ]
    return items, {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def serialize_version_history(row):
    return {
        "version_history_id": str(row.version_history_id),
        "versioned_entity_type": row.versioned_entity_type,
        "versioned_entity_id": str(row.versioned_entity_id),
        "version_number": row.version_number,
        "change_summary": row.change_summary,
        "author": _serialize_user(row.author_user),
        "reviewer": _serialize_user(row.reviewer_user),
        "approver": _serialize_user(row.approver_user),
        "board_approval_reference": row.board_approval_reference,
        "approval_reference": row.approval_reference,
        "approved_at": (
            row.approved_at.isoformat().replace("+00:00", "Z")
            if row.approved_at
            else None
        ),
        "old_value": redact_sensitive_mapping(row.old_value_json),
        "new_value": redact_sensitive_mapping(row.new_value_json),
        "linked_record": {
            "entity_type": row.versioned_entity_type,
            "entity_id": str(row.versioned_entity_id),
        },
        "effective_from": row.effective_from.isoformat(),
        "effective_to": row.effective_to.isoformat() if row.effective_to else None,
        "created_at": row.created_at.isoformat().replace("+00:00", "Z"),
    }


def paginated_version_histories(*, actor, query_params):
    filters, predicates = _validated_version_history_filters(query_params)
    queryset = (
        VersionHistory.objects.select_related(
            "author_user", "reviewer_user", "approver_user"
        )
        .filter(**filters)
        .filter(predicates)
        .filter(_version_history_scope(actor))
        .order_by("-created_at", "-version_history_id")
    )
    page = _positive_int(query_params.get("page"), 1)
    page_size = min(
        _positive_int(query_params.get("page_size"), _DEFAULT_PAGE_SIZE),
        _MAX_PAGE_SIZE,
    )
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size

    items = [
        serialize_version_history(row) for row in queryset[offset : offset + page_size]
    ]
    return items, {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def validation_field_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": str(exc)}


def _validate_loan_policy_payload(payload, *, partial, existing=None):
    field_errors = {}
    unknown = set(payload.keys()) - set(_LOAN_POLICY_FIELDS)
    for field in sorted(unknown):
        field_errors[field] = "Unknown field."
    if not partial:
        for field in sorted(_REQUIRED_CREATE_FIELDS):
            if field not in payload or payload.get(field) in ("", None):
                field_errors[field] = "This field is required."

    cleaned = {}
    for field in _LOAN_POLICY_FIELDS:
        if field not in payload:
            continue
        value = payload[field]
        if value is None and field in _OPTIONAL_FIELDS:
            cleaned[field] = None
            continue
        if field in _STRING_FIELDS:
            cleaned[field] = _clean_string(field, value, field_errors)
        elif field in _DATE_FIELDS:
            cleaned[field] = _clean_date(field, value, field_errors)
        elif field in _DECIMAL_FIELDS:
            cleaned[field] = _clean_decimal(field, value, field_errors)
        elif field in _INTEGER_FIELDS:
            cleaned[field] = _clean_positive_int(field, value, field_errors)
        elif field == "status":
            cleaned[field] = _clean_status(value, field_errors)

    effective_from = cleaned.get(
        "effective_from", existing.effective_from if existing is not None else None
    )
    effective_to = cleaned.get(
        "effective_to", existing.effective_to if existing is not None else None
    )
    if effective_from and effective_to and effective_to < effective_from:
        field_errors["effective_to"] = "Must be on or after effective_from."
    if (
        not partial
        and cleaned.get("status") is not None
        and cleaned["status"] != LoanPolicyConfig.STATUS_DRAFT
    ):
        field_errors["status"] = "New loan policy configs must start as draft."

    if field_errors:
        raise ValidationError(field_errors)
    return cleaned


def _clean_string(field, value, field_errors):
    if value is None:
        field_errors[field] = "This field is required."
        return value
    cleaned = str(value).strip()
    if not cleaned and field not in _OPTIONAL_FIELDS:
        field_errors[field] = "This field is required."
    return cleaned or None


def _clean_date(field, value, field_errors):
    if value in ("", None):
        if field not in _OPTIONAL_FIELDS:
            field_errors[field] = "This field is required."
        return None
    parsed = parse_date(str(value))
    if parsed is None:
        field_errors[field] = "Must be a valid ISO date."
    return parsed


def _clean_decimal(field, value, field_errors):
    if value in ("", None):
        if field not in _OPTIONAL_FIELDS:
            field_errors[field] = "This field is required."
        return None
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError):
        field_errors[field] = "Must be a decimal string."
        return None
    if parsed < 0:
        field_errors[field] = "Must be non-negative."
    return parsed


def _clean_positive_int(field, value, field_errors):
    if value in ("", None):
        if field not in _OPTIONAL_FIELDS:
            field_errors[field] = "This field is required."
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        field_errors[field] = "Must be an integer."
        return None
    if parsed <= 0:
        field_errors[field] = "Must be positive."
    return parsed


def _clean_status(value, field_errors):
    status = str(value).strip().lower()
    if status not in LoanPolicyConfig.STATUSES:
        field_errors["status"] = "Must be one of draft, active, retired."
    return status


def _record_policy_audit(*, user, request, action, config, old_value, new_value):
    AuditLog.objects.create(
        actor_user=user,
        actor_type="user",
        action=action,
        entity_type=LOAN_POLICY_ENTITY_TYPE,
        entity_id=config.loan_policy_config_id,
        old_value_json=old_value,
        new_value_json=new_value,
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )


def _validated_version_history_filters(query_params):
    unknown = set(query_params.keys()) - _VERSION_HISTORY_ALLOWED_PARAMS
    if unknown:
        raise ValidationError(
            {param: "Unknown query parameter." for param in sorted(unknown)}
        )
    filters = {}
    entity_type = query_params.get("versioned_entity_type")
    if entity_type:
        filters["versioned_entity_type"] = entity_type
    for field in _VERSION_HISTORY_UUID_FILTERS:
        raw = query_params.get(field)
        if raw:
            filters[field] = _parse_uuid(field, raw)
    created_from = _history_date_filter(query_params, "created_from")
    created_to = _history_date_filter(query_params, "created_to")
    if created_from and created_to and created_from > created_to:
        raise ValidationError({"created_to": "Must be on or after created_from."})
    if created_from:
        filters["created_at__gte"] = _history_day_boundary(created_from)
    if created_to:
        filters["created_at__lt"] = _history_day_boundary(
            created_to + timedelta(days=1)
        )
    predicates = Q()
    predicates &= _version_reference_predicate(query_params)
    approval = query_params.get("approval")
    if approval not in (None, ""):
        if str(approval).lower() not in {"true", "false"}:
            raise ValidationError({"approval": "Must be true or false."})
        approved = Q(approver_user__isnull=False) | Q(approved_at__isnull=False)
        predicates &= approved if str(approval).lower() == "true" else ~approved
    return filters, predicates


def _version_history_scope(actor):
    if (
        "internal_auditor" in auth_service.effective_role_codes(actor)
        and has_active_audit_read_scope(actor)
    ):
        return Q()
    predicate = Q(author_user=actor) | Q(reviewer_user=actor) | Q(approver_user=actor)
    permissions = set(auth_service.effective_permission_codes(actor))
    if LOAN_POLICY_READ_PERMISSION in permissions:
        predicate |= Q(versioned_entity_type=LOAN_POLICY_ENTITY_TYPE)
    return predicate


def _history_date_filter(query_params, field):
    raw = query_params.get(field)
    if not raw:
        return None
    try:
        value = parse_date(raw)
    except (TypeError, ValueError):
        value = None
    if value is None:
        raise ValidationError({field: "Must be a valid ISO date."})
    return value


def _history_day_boundary(value):
    return timezone.make_aware(datetime.combine(value, time.min))


def _version_reference_predicate(query_params):
    predicate = Q()
    application_reference = query_params.get("application_reference")
    if application_reference:
        from sfpcl_credit.applications.models import LoanApplication

        predicate &= Q(
            versioned_entity_type="loan_application",
            versioned_entity_id__in=LoanApplication.objects.filter(
                application_reference_number__iexact=application_reference
            ).values("pk"),
        )
    loan_account_reference = query_params.get("loan_account_reference")
    if loan_account_reference:
        from sfpcl_credit.loans.models import LoanAccount

        predicate &= Q(
            versioned_entity_type="loan_account",
            versioned_entity_id__in=LoanAccount.objects.filter(
                loan_account_number__iexact=loan_account_reference
            ).values("pk"),
        )
    return predicate


def _parse_uuid(field, raw):
    try:
        return uuid.UUID(str(raw))
    except (ValueError, AttributeError, TypeError) as exc:
        raise ValidationError({field: "Must be a valid UUID."}) from exc


def _serialize_user(user):
    if user is None:
        return None
    return {"user_id": str(user.user_id), "full_name": user.full_name}


def timezone_delta(**kwargs):
    return timedelta(**kwargs)


def _positive_int(value, default):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default
