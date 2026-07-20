from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal, InvalidOperation
import hashlib
import json
from math import ceil

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Exists, F, OuterRef, Q, Subquery
from django.utils import timezone
from django.utils.dateparse import parse_date

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.communications.models import Communication
from sfpcl_credit.communications.modules.communication_dispatcher import (
    CommunicationDispatcher,
)
from sfpcl_credit.configurations.models import (
    BorrowerRateNoticeObligation,
    InterestRateConfig,
    InterestRateConsumptionSnapshot,
    InterestRateHistory,
    VersionHistory,
)
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service


READ_PERMISSION = "config.loan_policy.read"
MANAGE_PERMISSION = "config.interest_rate.manage"
COMMUNICATION_SEND_PERMISSION = "communications.communication.send"
ENTITY_TYPE = "interest_rate_config"
CREATED_ACTION = "config.interest_rate.created"
ACTIVATED_ACTION = "config.interest_rate.activated"
PERIOD_CLOSED_ACTION = "config.interest_rate.period_closed"
_PAGE_SIZE = 20
_MAX_PAGE_SIZE = 100
_FIELDS = {
    "version_number",
    "rate_type",
    "effective_rate",
    "effective_from",
    "effective_to",
    "benchmark_name",
    "spread_rate",
    "reset_frequency",
    "communication_required",
    "board_approval_reference",
}
_REQUIRED_FIELDS = {
    "version_number",
    "rate_type",
    "effective_rate",
    "effective_from",
    "communication_required",
    "board_approval_reference",
}


class InterestRateConflict(Exception):
    pass


class MissingEffectiveRate(Exception):
    pass


class AmbiguousEffectiveRate(Exception):
    pass


@dataclass(frozen=True)
class EffectiveRate:
    interest_rate_config_id: object
    version_number: str
    effective_rate: Decimal
    effective_from: object
    effective_to: object


@dataclass(frozen=True)
class LoanRateProjection:
    loan_account_id: object
    as_of_date: object
    interest_rate_config_id: object
    version_number: str
    effective_rate: Decimal
    current_interest_rate: Decimal
    projection_changed: bool


@dataclass(frozen=True)
class ApprovedRateDecision:
    interest_rate_config_id: object
    benchmark_name: str | None
    spread_rate: Decimal | None
    reset_frequency: str | None


def activate(*, actor, request, interest_rate_config_id, idempotency_key):
    if not can_activate(actor):
        raise InterestRateConflict(
            "Interest-rate activation requires configuration and communication authority."
        )
    key = _idempotency_key(idempotency_key)
    with transaction.atomic():
        rows = InterestRateConfig.objects.select_for_update().order_by(
            "effective_from", "interest_rate_config_id"
        )
        locked_rows = list(rows)
        row = next(
            (candidate for candidate in locked_rows if candidate.pk == interest_rate_config_id),
            None,
        )
        if row is None:
            raise InterestRateConfig.DoesNotExist
        digest = _activation_digest(row)
        retained = next(
            (
                candidate
                for candidate in locked_rows
                if candidate.activation_idempotency_key == key
            ),
            None,
        )
        if retained is not None and retained.pk != row.pk:
            raise InterestRateConflict(
                "The idempotency key is already bound to another rate activation."
            )
        if row.status == InterestRateConfig.STATUS_ACTIVE:
            if (
                row.activation_idempotency_key == key
                and row.activation_payload_digest == digest
            ):
                retained_response = VersionHistory.objects.filter(
                    versioned_entity_type=ENTITY_TYPE,
                    versioned_entity_id=row.pk,
                    approval_reference=key,
                    change_summary=f"Activated interest rate version {row.version_number}.",
                ).values_list("new_value_json", flat=True).first()
                if retained_response is None:
                    raise InterestRateConflict(
                        "The retained activation has no frozen replay response."
                    )
                return {
                    "idempotency_replayed": True,
                    "original_response": retained_response,
                }
            raise InterestRateConflict(
                "An active rate version is immutable and cannot be activated again."
            )
        if row.created_by_user_id == actor.pk:
            raise InterestRateConflict(
                "The rate proposal creator cannot approve the same version."
            )
        decision_time = timezone.now()

        active = [
            candidate
            for candidate in locked_rows
            if candidate.status == InterestRateConfig.STATUS_ACTIVE
        ]
        if active:
            predecessor = active[-1]
            if row.effective_from <= predecessor.effective_from:
                raise InterestRateConflict(
                    "A rate version cannot be inserted into already approved history."
                )
            expected_from = (
                predecessor.effective_to + timedelta(days=1)
                if predecessor.effective_to
                else row.effective_from
            )
            if row.effective_from != expected_from:
                raise InterestRateConflict(
                    "The rate version must start the day after the approved predecessor."
                )
            if predecessor.effective_to is None:
                if InterestRateConsumptionSnapshot.objects.filter(
                    rate_config=predecessor,
                    calculation_date__gte=row.effective_from,
                ).exists():
                    raise InterestRateConflict(
                        "The successor would exclude a retained rate-consumption date."
                    )
                predecessor_before = serialize(predecessor)
                predecessor.effective_to = row.effective_from - timedelta(days=1)
                InterestRateConfig.objects.filter(pk=predecessor.pk)._canonical_update(
                    effective_to=predecessor.effective_to
                )
                predecessor_after = serialize(predecessor)
                VersionHistory.objects.create(
                    versioned_entity_type=ENTITY_TYPE,
                    versioned_entity_id=predecessor.pk,
                    version_number=predecessor.version_number,
                    change_summary=(
                        "Closed the prior interest-rate period through approved successor "
                        f"{row.version_number}."
                    ),
                    author_user=predecessor.created_by_user,
                    approver_user=actor,
                    board_approval_reference=row.board_approval_reference,
                    approval_reference=key,
                    approved_at=decision_time,
                    old_value_json=predecessor_before,
                    new_value_json=predecessor_after,
                    effective_from=predecessor.effective_from,
                    effective_to=predecessor.effective_to,
                    created_at=decision_time,
                )
                AuditLog.objects.create(
                    actor_user=actor,
                    actor_type="user",
                    action=PERIOD_CLOSED_ACTION,
                    entity_type=ENTITY_TYPE,
                    entity_id=predecessor.pk,
                    old_value_json=predecessor_before,
                    new_value_json=predecessor_after,
                    ip_address=request_ip(request),
                    user_agent=request_user_agent(request),
                    created_at=decision_time,
                )

        before = serialize(row)
        row.status = InterestRateConfig.STATUS_ACTIVE
        row.approved_by_user = actor
        row.activated_at = decision_time
        row.activation_idempotency_key = key
        row.activation_payload_digest = digest
        InterestRateConfig.objects.filter(pk=row.pk)._canonical_update(
            status=row.status,
            approved_by_user=row.approved_by_user,
            activated_at=row.activated_at,
            activation_idempotency_key=row.activation_idempotency_key,
            activation_payload_digest=row.activation_payload_digest,
        )
        _create_rate_histories_and_notices(row=row, actor=actor, request=request)
        after = serialize(row)
        VersionHistory.objects.create(
            versioned_entity_type=ENTITY_TYPE,
            versioned_entity_id=row.pk,
            version_number=row.version_number,
            change_summary=f"Activated interest rate version {row.version_number}.",
            author_user=row.created_by_user,
            approver_user=actor,
            board_approval_reference=row.board_approval_reference,
            approval_reference=key,
            approved_at=row.activated_at,
            old_value_json=before,
            new_value_json=after,
            effective_from=row.effective_from,
            effective_to=row.effective_to,
            created_at=row.activated_at,
        )
        AuditLog.objects.create(
            actor_user=actor,
            actor_type="user",
            action=ACTIVATED_ACTION,
            entity_type=ENTITY_TYPE,
            entity_id=row.pk,
            old_value_json=before,
            new_value_json=after,
            ip_address=request_ip(request),
            user_agent=request_user_agent(request),
        )
        return after


def resolve_effective_rate(calculation_date):
    matches = list(
        InterestRateConfig.objects.filter(
            status=InterestRateConfig.STATUS_ACTIVE,
            effective_from__lte=calculation_date,
        )
        .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=calculation_date))
        .order_by("effective_from", "interest_rate_config_id")[:2]
    )
    if not matches:
        raise MissingEffectiveRate(
            "No approved interest rate exists for the calculation date."
        )
    if len(matches) != 1:
        raise AmbiguousEffectiveRate(
            "More than one approved interest rate exists for the calculation date."
        )
    row = matches[0]
    return EffectiveRate(
        interest_rate_config_id=row.pk,
        version_number=row.version_number,
        effective_rate=row.effective_rate,
        effective_from=row.effective_from,
        effective_to=row.effective_to,
    )


def get_approved_rate_decision(interest_rate_config_id):
    """Return calculation metadata without exposing the configuration model."""
    row = InterestRateConfig.objects.filter(
        pk=interest_rate_config_id,
        status=InterestRateConfig.STATUS_ACTIVE,
    ).first()
    if row is None:
        raise MissingEffectiveRate("The approved interest-rate decision does not exist.")
    return ApprovedRateDecision(
        interest_rate_config_id=row.pk,
        benchmark_name=row.benchmark_name,
        spread_rate=row.spread_rate,
        reset_frequency=row.reset_frequency,
    )


def converge_current_rate_projection(
    *, actor, request, loan_account_id, as_of_date
):
    """Publish the approved explicit-date rate to one loan's mutable current projection."""
    if not can_manage(actor):
        raise InterestRateConflict(
            "Current-rate convergence requires interest-rate management authority."
        )
    from sfpcl_credit.loans.models import LoanAccount

    with transaction.atomic():
        account = LoanAccount.objects.select_for_update().get(pk=loan_account_id)
        effective = resolve_effective_rate(as_of_date)
        if not InterestRateHistory.objects.filter(
            loan_account=account,
            rate_config_id=effective.interest_rate_config_id,
            effective_from=effective.effective_from,
            new_interest_rate=effective.effective_rate,
        ).exists():
            raise InterestRateConflict(
                "The loan has no retained history for the effective rate decision."
            )
        changed = account.current_interest_rate != effective.effective_rate
        if changed:
            old_rate = account.current_interest_rate
            account.current_interest_rate = effective.effective_rate
            account.save(update_fields=["current_interest_rate"])
            AuditLog.objects.create(
                actor_user=actor,
                actor_type="user",
                action="config.interest_rate.loan_projection_converged",
                entity_type="loan_account",
                entity_id=account.pk,
                old_value_json={"current_interest_rate": f"{old_rate:.4f}"},
                new_value_json={
                    "current_interest_rate": f"{effective.effective_rate:.4f}",
                    "interest_rate_config_id": str(effective.interest_rate_config_id),
                    "as_of_date": as_of_date.isoformat(),
                },
                ip_address=request_ip(request),
                user_agent=request_user_agent(request),
            )
        return LoanRateProjection(
            loan_account_id=account.pk,
            as_of_date=as_of_date,
            interest_rate_config_id=effective.interest_rate_config_id,
            version_number=effective.version_number,
            effective_rate=effective.effective_rate,
            current_interest_rate=account.current_interest_rate,
            projection_changed=changed,
        )


def current_rate_projection_is_coherent(*, account, as_of_date=None):
    """Resolve loan current-rate coherence without exposing configuration models."""
    boundary_date = as_of_date or timezone.localdate()
    latest = (
        InterestRateHistory.objects.select_related("rate_config")
        .filter(loan_account=account, effective_from__lte=boundary_date)
        .order_by("-effective_from", "-interest_rate_history_id")
        .first()
    )
    if latest is None:
        return account.current_interest_rate == account.terms.rate_of_interest
    return bool(
        latest.new_interest_rate == account.current_interest_rate
        and latest.rate_config.status == InterestRateConfig.STATUS_ACTIVE
        and latest.rate_config.effective_rate == latest.new_interest_rate
        and latest.rate_config.effective_from == latest.effective_from
    )


def filter_current_rate_projection_coherent(queryset, *, as_of_date=None):
    """Apply the same explicit-date rate decision to a loan queryset."""
    boundary_date = as_of_date or timezone.localdate()
    histories = InterestRateHistory.objects.filter(
        loan_account_id=OuterRef("pk"),
        effective_from__lte=boundary_date,
        rate_config__status=InterestRateConfig.STATUS_ACTIVE,
        rate_config__effective_rate=F("new_interest_rate"),
        rate_config__effective_from=F("effective_from"),
    ).order_by("-effective_from", "-interest_rate_history_id")
    return queryset.annotate(
        _current_rate_owner_value=Subquery(histories.values("new_interest_rate")[:1]),
        _has_current_rate_owner=Exists(histories),
    ).filter(
        Q(
            _has_current_rate_owner=False,
            terms__rate_of_interest=F("current_interest_rate"),
        )
        | Q(
            _has_current_rate_owner=True,
            _current_rate_owner_value=F("current_interest_rate"),
        )
    )


def consume_effective_rate(
    *, consumer_kind, consumer_reference_id, loan_account_id, calculation_date
):
    if consumer_kind not in {"interest_invoice", "interest_accrual"}:
        raise ValidationError({"consumer_kind": "Unsupported interest consumer."})
    try:
        with transaction.atomic():
            retained = InterestRateConsumptionSnapshot.objects.select_for_update().filter(
                consumer_kind=consumer_kind,
                consumer_reference_id=consumer_reference_id,
            ).first()
            if retained is not None:
                return _require_matching_consumption(
                    retained,
                    loan_account_id=loan_account_id,
                    calculation_date=calculation_date,
                )
            effective = resolve_effective_rate(calculation_date)
            return InterestRateConsumptionSnapshot.objects.create(
                consumer_kind=consumer_kind,
                consumer_reference_id=consumer_reference_id,
                loan_account_id=loan_account_id,
                calculation_date=calculation_date,
                rate_config_id=effective.interest_rate_config_id,
                version_number=effective.version_number,
                effective_rate=effective.effective_rate,
            )
    except IntegrityError:
        retained = InterestRateConsumptionSnapshot.objects.filter(
            consumer_kind=consumer_kind,
            consumer_reference_id=consumer_reference_id,
        ).first()
        if retained is None:
            raise InterestRateConflict(
                "The interest consumer could not retain one canonical snapshot."
            )
        return _require_matching_consumption(
            retained,
            loan_account_id=loan_account_id,
            calculation_date=calculation_date,
        )


def _require_matching_consumption(retained, *, loan_account_id, calculation_date):
    if (
        retained.loan_account_id == loan_account_id
        and retained.calculation_date == calculation_date
    ):
        return retained
    raise InterestRateConflict(
        "The interest consumer reference is already bound to another calculation."
    )


def can_read(user):
    permissions = set(auth_service.effective_permission_codes(user))
    return READ_PERMISSION in permissions or MANAGE_PERMISSION in permissions


def can_manage(user):
    return MANAGE_PERMISSION in auth_service.effective_permission_codes(user)


def can_activate(user):
    permissions = set(auth_service.effective_permission_codes(user))
    return {MANAGE_PERMISSION, COMMUNICATION_SEND_PERMISSION}.issubset(permissions)


def create_proposal(*, actor, request, payload):
    values = _validated_payload(payload)
    try:
        with transaction.atomic():
            row = InterestRateConfig.objects.create(created_by_user=actor, **values)
            AuditLog.objects.create(
                actor_user=actor,
                actor_type="user",
                action=CREATED_ACTION,
                entity_type=ENTITY_TYPE,
                entity_id=row.pk,
                old_value_json=None,
                new_value_json=_audit_values(row),
                ip_address=request_ip(request),
                user_agent=request_user_agent(request),
            )
    except IntegrityError as exc:
        raise ValidationError(
            {"version_number": "This interest-rate version already exists."}
        ) from exc
    return serialize(row)


def list_proposals(query_params):
    unknown = set(query_params.keys()) - {"page", "page_size"}
    if unknown:
        raise ValidationError(
            {field: "Unknown query parameter." for field in sorted(unknown)}
        )
    page = _positive_int(query_params.get("page"), 1)
    page_size = min(_positive_int(query_params.get("page_size"), _PAGE_SIZE), _MAX_PAGE_SIZE)
    queryset = InterestRateConfig.objects.select_related(
        "created_by_user", "approved_by_user"
    ).order_by("-effective_from", "-interest_rate_config_id")
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    return [serialize(row) for row in queryset[offset : offset + page_size]], {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def serialize(row):
    summary = {"pending": 0, "sent": 0, "failed": 0}
    channel_summary = {"pending": 0, "sent": 0, "failed": 0}
    obligations = row.borrower_notice_obligations.select_related(
        "email_communication", "sms_communication"
    )
    for obligation in obligations:
        summary[obligation.delivery_status] += 1
        channel_summary[obligation.email_delivery_status] += 1
        channel_summary[obligation.sms_delivery_status] += 1
    return {
        "interest_rate_config_id": str(row.pk),
        "version_number": row.version_number,
        "rate_type": row.rate_type,
        "effective_rate": f"{row.effective_rate:.4f}",
        "effective_from": row.effective_from.isoformat(),
        "effective_to": row.effective_to.isoformat() if row.effective_to else None,
        "benchmark_name": row.benchmark_name or None,
        "spread_rate": f"{row.spread_rate:.4f}" if row.spread_rate is not None else None,
        "reset_frequency": row.reset_frequency or None,
        "communication_required": row.communication_required,
        "board_approval_reference": row.board_approval_reference,
        "status": row.status,
        "created_by_user_id": str(row.created_by_user_id),
        "approved_by_user_id": str(row.approved_by_user_id) if row.approved_by_user_id else None,
        "activated_at": row.activated_at.isoformat().replace("+00:00", "Z") if row.activated_at else None,
        "notice_summary": summary,
        "notice_channel_summary": channel_summary,
    }


def validation_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": str(exc)}


def _validated_payload(payload):
    errors = {}
    for field in sorted(set(payload) - _FIELDS):
        errors[field] = "Unknown field."
    for field in sorted(_REQUIRED_FIELDS):
        if field not in payload or payload[field] in (None, ""):
            errors[field] = "This field is required."
    if errors:
        raise ValidationError(errors)

    version_number = _text(payload["version_number"], "version_number", 40)
    rate_type = _text(payload["rate_type"], "rate_type", 60).lower()
    if rate_type != "floating":
        errors["rate_type"] = "Only floating rates are supported."
    effective_rate = _decimal(payload["effective_rate"], "effective_rate", errors)
    if effective_rate is not None and not effective_rate.is_finite():
        errors["effective_rate"] = "Must be a finite decimal number."
    elif effective_rate is not None and effective_rate < 0:
        errors["effective_rate"] = "Must be zero or greater."
    _validate_rate_precision(effective_rate, "effective_rate", errors)
    effective_from = _date(payload["effective_from"], "effective_from", errors)
    effective_to = _optional_date(payload.get("effective_to"), "effective_to", errors)
    if effective_from and effective_to and effective_to < effective_from:
        errors["effective_to"] = "Must be on or after effective_from."
    spread_rate = _optional_decimal(payload.get("spread_rate"), "spread_rate", errors)
    if spread_rate is not None and not spread_rate.is_finite():
        errors["spread_rate"] = "Must be a finite decimal number."
    elif spread_rate is not None and spread_rate < 0:
        errors["spread_rate"] = "Must be zero or greater."
    _validate_rate_precision(spread_rate, "spread_rate", errors)
    if not isinstance(payload["communication_required"], bool):
        errors["communication_required"] = "Must be a boolean."
    if errors:
        raise ValidationError(errors)
    return {
        "version_number": version_number,
        "rate_type": rate_type,
        "effective_rate": effective_rate,
        "effective_from": effective_from,
        "effective_to": effective_to,
        "benchmark_name": _optional_text(payload.get("benchmark_name"), "benchmark_name", 120),
        "spread_rate": spread_rate,
        "reset_frequency": _optional_text(payload.get("reset_frequency"), "reset_frequency", 60),
        "communication_required": payload["communication_required"],
        "board_approval_reference": _text(
            payload["board_approval_reference"], "board_approval_reference", 255
        ),
    }


def _audit_values(row):
    values = serialize(row)
    values.pop("notice_summary")
    values.pop("notice_channel_summary")
    return values


def _text(value, field, limit):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError({field: "Must be a non-empty string."})
    value = value.strip()
    if len(value) > limit:
        raise ValidationError({field: f"Must be at most {limit} characters."})
    return value


def _optional_text(value, field, limit):
    if value in (None, ""):
        return None
    return _text(value, field, limit)


def _decimal(value, field, errors):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        errors[field] = "Must be a decimal number."
        return None


def _optional_decimal(value, field, errors):
    return None if value in (None, "") else _decimal(value, field, errors)


def _validate_rate_precision(value, field, errors):
    if value is None or not value.is_finite():
        return
    if abs(value) >= Decimal("10000") or value != value.quantize(Decimal("0.0001")):
        errors[field] = "Must fit four integer and four decimal places."


def _date(value, field, errors):
    parsed = parse_date(value) if isinstance(value, str) else None
    if parsed is None:
        errors[field] = "Must be a valid ISO date."
    return parsed


def _optional_date(value, field, errors):
    return None if value in (None, "") else _date(value, field, errors)


def _positive_int(value, default):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def _idempotency_key(value):
    key = value.strip() if isinstance(value, str) else ""
    if not key:
        raise ValidationError({"idempotency_key": "Idempotency-Key header is required."})
    if len(key) > 255:
        raise ValidationError(
            {"idempotency_key": "Idempotency-Key must be at most 255 characters."}
        )
    return key


def _activation_digest(row):
    payload = {
        "interest_rate_config_id": str(row.pk),
        "version_number": row.version_number,
        "effective_rate": f"{row.effective_rate:.4f}",
        "effective_from": row.effective_from.isoformat(),
        "communication_required": row.communication_required,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _create_rate_histories_and_notices(*, row, actor, request):
    from sfpcl_credit.loans.models import LoanAccount

    accounts = LoanAccount.objects.select_for_update().select_related("member").filter(
        loan_account_status="active",
        interest_rate_type="floating",
    ).order_by("loan_account_id")
    for account in accounts:
        predecessor_history = (
            InterestRateHistory.objects.filter(
                loan_account=account,
                effective_from__lt=row.effective_from,
            )
            .order_by("-effective_from", "-interest_rate_history_id")
            .first()
        )
        old_interest_rate = (
            predecessor_history.new_interest_rate
            if predecessor_history is not None
            else account.current_interest_rate
        )
        if row.effective_from <= timezone.localdate():
            account.current_interest_rate = row.effective_rate
            account.save(update_fields=["current_interest_rate"])
        email_communication = None
        if row.communication_required:
            obligation = BorrowerRateNoticeObligation.objects.create(
                interest_rate_config=row,
                loan_account=account,
            )
            for channel, address, template_code in (
                (
                    Communication.CHANNEL_EMAIL,
                    account.member.email,
                    "interest_rate_change_email",
                ),
                (
                    Communication.CHANNEL_SMS,
                    account.member.mobile_number,
                    "interest_rate_change_sms",
                ),
            ):
                if not address:
                    failure_field = f"{channel}_failure_code"
                    setattr(obligation, failure_field, "recipient_address_missing")
                    obligation.save(update_fields=[failure_field])
                    continue
                idempotency_prefix = f"rate-notice:{row.pk}:{account.pk}:{channel}"
                communication = CommunicationDispatcher.create_from_template(
                    actor=actor,
                    template_code=template_code,
                    recipient={
                        "party_type": "borrower",
                        "party_id": account.member_id,
                        "address": address,
                        "channel": channel,
                    },
                    context={
                        "request": request,
                        "idempotency_key": f"{idempotency_prefix}:snapshot",
                        "merge_data": {
                            "effective_rate": f"{row.effective_rate:.4f}",
                            "effective_from": row.effective_from.isoformat(),
                        },
                    },
                    related_entity={"type": ENTITY_TYPE, "id": row.pk},
                )
                CommunicationDispatcher.send(
                    communication_id=communication.pk,
                    idempotency_key=f"{idempotency_prefix}:delivery",
                )
                communication_field = f"{channel}_communication"
                setattr(obligation, communication_field, communication)
                obligation.save(update_fields=[communication_field])
                if channel == Communication.CHANNEL_EMAIL:
                    email_communication = communication
        InterestRateHistory.objects.create(
            loan_account=account,
            old_interest_rate=old_interest_rate,
            new_interest_rate=row.effective_rate,
            effective_from=row.effective_from,
            rate_config=row,
            borrower_communication=email_communication,
            changed_by_user=actor,
            changed_at=row.activated_at,
        )
