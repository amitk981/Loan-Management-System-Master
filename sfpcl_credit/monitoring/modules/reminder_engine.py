from uuid import UUID, uuid4

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_date

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.communications.models import CommunicationDeliveryJob, ContentTemplate
from sfpcl_credit.communications.modules.communication_dispatcher import (
    CommunicationDispatcher,
)
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.loans.modules.loan_account_read import (
    LoanAccountReadPermissionDenied,
    scoped_account_candidates,
)
from sfpcl_credit.monitoring.models import DpdStatus, Reminder


CREATE_PERMISSION = "monitoring.reminder.create"
RUN_LIMIT = 100
SERVICEABLE_STATUSES = {
    "active",
    "partially_repaid",
    "overdue",
    "grace_period",
    "extended",
    "non_recoverable_under_review",
}


class ReminderValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


class ReminderPermissionDenied(Exception):
    pass


class ReminderNotFound(Exception):
    pass


class ReminderConflict(Exception):
    pass


class ReminderEngine:
    @classmethod
    @transaction.atomic
    def create_reminder(cls, *, actor, loan_account_id, payload, request=None):
        cleaned = (
            _validate_phone_log(payload)
            if payload.get("channel") == Reminder.CHANNEL_PHONE
            else _validate_electronic_reminder(payload)
        )
        _require_permission(actor)
        account = cls._locked_scoped_account(actor=actor, loan_account_id=loan_account_id)
        dpd_status = cls._eligible_dpd_status(
            account=account, quarter_end_date=cleaned["quarter_end_date"]
        )
        if cleaned["channel"] in {Reminder.CHANNEL_SMS, Reminder.CHANNEL_EMAIL}:
            prefix = (
                f"manual-reminder:{account.pk}:{cleaned['quarter_end_date']}:"
                f"{cleaned['channel']}"
            )
            row = cls._create_electronic_snapshot(
                actor=actor,
                account=account,
                dpd_status=dpd_status,
                quarter_end_date=cleaned["quarter_end_date"],
                channel=cleaned["channel"],
                origin=Reminder.ORIGIN_MANUAL,
                content_template_id=cleaned["content_template_id"],
                idempotency_prefix=prefix,
                request=request,
            )
            if cleaned["send_now"]:
                return cls.send_reminder(
                    actor=actor,
                    reminder_id=row.pk,
                    idempotency_key=f"{prefix}:delivery",
                    request=request,
                )
            return serialize_reminder(row)

        row = Reminder.objects.create(
            loan_account=account,
            loan_application=account.loan_application,
            member=account.member,
            dpd_status=dpd_status,
            quarter_end_date=cleaned["quarter_end_date"],
            reminder_type=cleaned["reminder_type"],
            origin=Reminder.ORIGIN_MANUAL,
            channel=Reminder.CHANNEL_PHONE,
            message_body=cleaned["message_body"],
            delivery_status=Reminder.STATUS_CALL_LOGGED,
            contacted_person=cleaned["contacted_person"],
            call_outcome=cleaned["call_outcome"],
            next_follow_up_date=cleaned["next_follow_up_date"],
            created_by_user=actor,
            sent_at=timezone.now(),
        )
        AuditLog.objects.create(
            actor_user=actor,
            action="monitoring.reminder.phone_logged",
            entity_type="reminder",
            entity_id=row.pk,
            new_value_json={
                "quarter_end_date": cleaned["quarter_end_date"].isoformat(),
                "reminder_type": cleaned["reminder_type"],
                "channel": Reminder.CHANNEL_PHONE,
                "contacted_person": cleaned["contacted_person"],
                "next_follow_up_date": cleaned["next_follow_up_date"].isoformat(),
            },
            ip_address=request_ip(request) if request is not None else "",
            user_agent=request_user_agent(request) if request is not None else "",
        )
        return serialize_reminder(row)

    @classmethod
    @transaction.atomic
    def send_reminder(cls, *, actor, reminder_id, idempotency_key, request=None):
        _require_permission(actor)
        if not isinstance(idempotency_key, str) or not idempotency_key.strip():
            raise ReminderValidation({"idempotency_key": "Idempotency-Key is required."})
        row = (
            Reminder.objects.select_for_update()
            .select_related("loan_account")
            .filter(pk=reminder_id)
            .first()
        )
        if row is None or not _scoped_accounts(actor).filter(pk=row.loan_account_id).exists():
            raise ReminderNotFound
        if row.channel not in {Reminder.CHANNEL_SMS, Reminder.CHANNEL_EMAIL} or row.communication_id is None:
            raise ReminderConflict("Only electronic reminder snapshots can be sent.")
        account = row.loan_account
        current_dpd = DpdStatus.objects.filter(
            pk=account.current_dpd_status_id,
            loan_account=account,
            as_of_date=row.quarter_end_date,
            days_past_due__gte=365,
            total_overdue_amount__gt=0,
        ).exists()
        if (
            not current_dpd
            or account.total_outstanding <= 0
            or account.loan_account_status not in SERVICEABLE_STATUSES
        ):
            row.delivery_status = Reminder.STATUS_CANCELLED
            row.status_reason = "loan_no_longer_eligible"
            row.save(update_fields=["delivery_status", "status_reason"])
            AuditLog.objects.create(
                actor_user=actor,
                action="monitoring.reminder.cancelled",
                entity_type="reminder",
                entity_id=row.pk,
                new_value_json={"reason": "loan_no_longer_eligible"},
                ip_address=request_ip(request) if request is not None else "",
                user_agent=request_user_agent(request) if request is not None else "",
            )
            return serialize_reminder(row)
        CommunicationDispatcher.send(
            communication_id=row.communication_id,
            idempotency_key=idempotency_key.strip(),
        )
        return serialize_reminder(row)

    @classmethod
    def run_quarter_end(cls, *, actor, payload, request=None):
        cleaned = _validate_quarter_run(payload)
        _require_permission(actor)
        scoped = _scoped_accounts(actor)
        candidates = list(
            DpdStatus.objects.select_related("loan_account__member", "loan_account__loan_application")
            .filter(
                loan_account__in=scoped,
                as_of_date=cleaned["quarter_end_date"],
                days_past_due__gte=365,
                total_overdue_amount__gt=0,
                loan_account__total_outstanding__gt=0,
                loan_account__loan_account_status__in=SERVICEABLE_STATUSES,
            )
            .order_by("loan_account_id")[:RUN_LIMIT]
        )
        results = []
        for dpd_status in candidates:
            row, created = cls._create_automatic(
                actor=actor,
                dpd_status=dpd_status,
                quarter_end_date=cleaned["quarter_end_date"],
                channel=cleaned["channel"],
                content_template_id=cleaned["content_template_id"],
                request=request,
            )
            results.append({"created": created, "reminder": serialize_reminder(row)})
        return {
            "quarter_end_date": cleaned["quarter_end_date"].isoformat(),
            "channel": cleaned["channel"],
            "created_count": sum(item["created"] for item in results),
            "retained_count": sum(not item["created"] for item in results),
            "results": [item["reminder"] for item in results],
        }

    @classmethod
    def _locked_scoped_account(cls, *, actor, loan_account_id):
        account = (
            _scoped_accounts(actor)
            .select_for_update()
            .select_related("member", "loan_application")
            .filter(pk=loan_account_id)
            .first()
        )
        if account is None:
            raise ReminderNotFound
        return account

    @classmethod
    def _eligible_dpd_status(cls, *, account, quarter_end_date):
        dpd_status = DpdStatus.objects.filter(
            pk=account.current_dpd_status_id,
            loan_account=account,
            as_of_date=quarter_end_date,
            days_past_due__gte=365,
            total_overdue_amount__gt=0,
        ).first()
        if (
            dpd_status is None
            or account.total_outstanding <= 0
            or account.loan_account_status not in SERVICEABLE_STATUSES
        ):
            raise ReminderConflict("The loan is no longer eligible for this reminder.")
        return dpd_status

    @classmethod
    def _create_electronic_snapshot(
        cls,
        *,
        actor,
        account,
        dpd_status,
        quarter_end_date,
        channel,
        origin,
        content_template_id,
        idempotency_prefix,
        request,
    ):
        address = (
            account.member.mobile_number
            if channel == Reminder.CHANNEL_SMS
            else account.member.email
        )
        if not address:
            raise ReminderValidation({"recipient": f"The borrower has no {channel} contact."})
        try:
            template = ContentTemplate.objects.get(pk=content_template_id)
        except ContentTemplate.DoesNotExist as exc:
            raise ReminderValidation(
                {"content_template_id": "Content template was not found."}
            ) from exc
        reminder_id = uuid4()
        communication = CommunicationDispatcher.create_from_template(
            actor=actor,
            template_code=template.template_code,
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
                    "loan_account_number": account.loan_account_number,
                    "quarter_end_date": quarter_end_date.isoformat(),
                },
            },
            related_entity={"type": "monitoring_reminder", "id": reminder_id},
        )
        row = Reminder.objects.create(
            reminder_id=reminder_id,
            loan_account=account,
            loan_application=account.loan_application,
            member=account.member,
            dpd_status=dpd_status,
            quarter_end_date=quarter_end_date,
            reminder_type=Reminder.TYPE_OUTSTANDING_BEYOND_ONE_YEAR,
            origin=origin,
            channel=channel,
            content_template=communication.content_template,
            message_body=communication.body_snapshot,
            communication=communication,
            delivery_status=Reminder.STATUS_QUEUED,
            created_by_user=actor,
        )
        AuditLog.objects.create(
            actor_user=actor,
            action="monitoring.reminder.created",
            entity_type="reminder",
            entity_id=row.pk,
            new_value_json={
                "quarter_end_date": quarter_end_date.isoformat(),
                "reminder_type": Reminder.TYPE_OUTSTANDING_BEYOND_ONE_YEAR,
                "channel": channel,
            },
            ip_address=request_ip(request) if request is not None else "",
            user_agent=request_user_agent(request) if request is not None else "",
        )
        return row

    @classmethod
    @transaction.atomic
    def _create_automatic(
        cls, *, actor, dpd_status, quarter_end_date, channel, content_template_id, request
    ):
        account = cls._locked_scoped_account(
            actor=actor, loan_account_id=dpd_status.loan_account_id
        )
        retained = Reminder.objects.filter(
            loan_account=account,
            quarter_end_date=quarter_end_date,
            reminder_type=Reminder.TYPE_OUTSTANDING_BEYOND_ONE_YEAR,
            origin=Reminder.ORIGIN_AUTOMATIC,
            channel=channel,
        ).first()
        if retained is not None:
            return retained, False
        current_dpd = cls._eligible_dpd_status(
            account=account, quarter_end_date=quarter_end_date
        )
        prefix = f"quarter-reminder:{account.pk}:{quarter_end_date}:{channel}"
        row = cls._create_electronic_snapshot(
            actor=actor,
            account=account,
            dpd_status=current_dpd,
            quarter_end_date=quarter_end_date,
            channel=channel,
            origin=Reminder.ORIGIN_AUTOMATIC,
            content_template_id=content_template_id,
            idempotency_prefix=prefix,
            request=request,
        )
        CommunicationDispatcher.send(
            communication_id=row.communication_id,
            idempotency_key=f"{prefix}:delivery",
        )
        return row, True


def _validate_quarter_run(payload):
    expected = {"quarter_end_date", "channel", "content_template_id"}
    if set(payload) != expected:
        raise ReminderValidation({"body": "Use quarter_end_date, channel and content_template_id."})
    parsed = parse_date(payload.get("quarter_end_date")) if isinstance(payload.get("quarter_end_date"), str) else None
    if parsed is None or (parsed.month, parsed.day) not in {(3, 31), (6, 30), (9, 30), (12, 31)}:
        raise ReminderValidation({"quarter_end_date": "Must be an ISO calendar quarter-end date."})
    channel = payload.get("channel")
    if channel not in {Reminder.CHANNEL_SMS, Reminder.CHANNEL_EMAIL}:
        raise ReminderValidation({"channel": "Quarter runs support sms or email."})
    try:
        template_id = UUID(str(payload.get("content_template_id")))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ReminderValidation({"content_template_id": "Must be a UUID."}) from exc
    return {"quarter_end_date": parsed, "channel": channel, "content_template_id": template_id}


def _validate_phone_log(payload):
    expected = {
        "quarter_end_date",
        "reminder_type",
        "channel",
        "message_body",
        "call_outcome",
        "contacted_person",
        "next_follow_up_date",
        "send_now",
    }
    if set(payload) != expected:
        raise ReminderValidation({"body": "Use the complete phone reminder fields."})
    quarter_end = parse_date(payload.get("quarter_end_date")) if isinstance(payload.get("quarter_end_date"), str) else None
    follow_up = parse_date(payload.get("next_follow_up_date")) if isinstance(payload.get("next_follow_up_date"), str) else None
    errors = {}
    if quarter_end is None or (quarter_end.month, quarter_end.day) not in {(3, 31), (6, 30), (9, 30), (12, 31)}:
        errors["quarter_end_date"] = "Must be an ISO calendar quarter-end date."
    if payload.get("reminder_type") != Reminder.TYPE_OUTSTANDING_BEYOND_ONE_YEAR:
        errors["reminder_type"] = "Only outstanding_beyond_one_year is supported."
    if payload.get("channel") != Reminder.CHANNEL_PHONE:
        errors["channel"] = "This manual log requires phone."
    if payload.get("send_now") is not False:
        errors["send_now"] = "Phone logs cannot invoke a provider send."
    for field in ("message_body", "call_outcome"):
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip() or len(value.strip()) > 1000:
            errors[field] = "Must be nonblank and at most 1000 characters."
    if payload.get("contacted_person") not in {"borrower", "nominee", "representative"}:
        errors["contacted_person"] = "Use borrower, nominee or representative."
    if follow_up is None or (quarter_end is not None and follow_up < quarter_end):
        errors["next_follow_up_date"] = "Must be an ISO date on or after quarter end."
    if errors:
        raise ReminderValidation(errors)
    return {
        "quarter_end_date": quarter_end,
        "reminder_type": payload["reminder_type"],
        "channel": Reminder.CHANNEL_PHONE,
        "message_body": payload["message_body"].strip(),
        "call_outcome": payload["call_outcome"].strip(),
        "contacted_person": payload["contacted_person"],
        "next_follow_up_date": follow_up,
    }


def _validate_electronic_reminder(payload):
    expected = {
        "quarter_end_date",
        "reminder_type",
        "channel",
        "content_template_id",
        "message_body",
        "send_now",
    }
    if set(payload) != expected:
        raise ReminderValidation({"body": "Use the complete electronic reminder fields."})
    quarter_end = parse_date(payload.get("quarter_end_date")) if isinstance(payload.get("quarter_end_date"), str) else None
    errors = {}
    if quarter_end is None or (quarter_end.month, quarter_end.day) not in {(3, 31), (6, 30), (9, 30), (12, 31)}:
        errors["quarter_end_date"] = "Must be an ISO calendar quarter-end date."
    if payload.get("reminder_type") != Reminder.TYPE_OUTSTANDING_BEYOND_ONE_YEAR:
        errors["reminder_type"] = "Only outstanding_beyond_one_year is supported."
    channel = payload.get("channel")
    if channel not in {Reminder.CHANNEL_SMS, Reminder.CHANNEL_EMAIL}:
        errors["channel"] = "Use sms or email."
    try:
        template_id = UUID(str(payload.get("content_template_id")))
    except (ValueError, TypeError, AttributeError):
        template_id = None
        errors["content_template_id"] = "Must be a UUID."
    message = payload.get("message_body")
    if not isinstance(message, str) or not message.strip() or len(message.strip()) > 1000:
        errors["message_body"] = "Must be nonblank and at most 1000 characters."
    if not isinstance(payload.get("send_now"), bool):
        errors["send_now"] = "Must be a boolean."
    if errors:
        raise ReminderValidation(errors)
    return {
        "quarter_end_date": quarter_end,
        "reminder_type": payload["reminder_type"],
        "channel": channel,
        "content_template_id": template_id,
        "send_now": payload["send_now"],
    }


def _require_permission(actor):
    if not actor.can_authenticate() or CREATE_PERMISSION not in auth_service.effective_permission_codes(actor):
        raise ReminderPermissionDenied


def _scoped_accounts(actor):
    try:
        return scoped_account_candidates(actor=actor)
    except LoanAccountReadPermissionDenied as exc:
        raise ReminderPermissionDenied from exc


def serialize_reminder(row):
    delivery_status = row.delivery_status
    if row.communication_id and delivery_status != Reminder.STATUS_CANCELLED:
        job_status = CommunicationDeliveryJob.objects.filter(
            communication_id=row.communication_id
        ).values_list("status", flat=True).first()
        if job_status == CommunicationDeliveryJob.STATUS_SENT:
            delivery_status = Reminder.STATUS_SENT
        elif job_status == CommunicationDeliveryJob.STATUS_FAILED:
            delivery_status = Reminder.STATUS_FAILED
    return {
        "reminder_id": str(row.pk),
        "loan_account_id": str(row.loan_account_id),
        "member_id": str(row.member_id),
        "quarter_end_date": row.quarter_end_date.isoformat(),
        "reminder_type": row.reminder_type,
        "origin": row.origin,
        "channel": row.channel,
        "delivery_status": delivery_status,
        "status_reason": row.status_reason or None,
        "next_follow_up_date": row.next_follow_up_date.isoformat() if row.next_follow_up_date else None,
        "created_at": row.created_at.isoformat(),
    }
