from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from sfpcl_credit.scheduler.models import ScheduledJob


_ALLOWED_JOB_TYPES = {
    "report_export",
    "notification_generation",
    "reminder_generation",
    "interest_accrual",
    "dpd_calculation",
    "compliance_reminder",
    "default_assessment",
    "workflow_task_reconciliation",
}
_TERMINAL_STATUSES = {
    ScheduledJob.STATUS_SUCCEEDED,
    ScheduledJob.STATUS_FAILED,
}
_MAX_ERROR_SUMMARY_LENGTH = 500


def enqueue_scheduled_job(
    *,
    job_type,
    due_at,
    idempotency_key=None,
    related_entity_type=None,
    related_entity_id=None,
):
    cleaned = _clean_enqueue_args(
        job_type=job_type,
        due_at=due_at,
        idempotency_key=idempotency_key,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
    )
    if cleaned["idempotency_key"]:
        return _enqueue_idempotently(cleaned)
    return ScheduledJob.objects.create(**cleaned), True


def mark_job_running(job_id):
    with transaction.atomic():
        row = _locked_job(job_id)
        _require_status(row, {ScheduledJob.STATUS_QUEUED})
        row.status = ScheduledJob.STATUS_RUNNING
        row.started_at = timezone.now()
        row.completed_at = None
        row.attempts += 1
        row.last_error_summary = ""
        row.save(
            update_fields=[
                "status",
                "started_at",
                "completed_at",
                "attempts",
                "last_error_summary",
                "updated_at",
            ]
        )
    return row


def mark_job_succeeded(job_id):
    with transaction.atomic():
        row = _locked_job(job_id)
        _require_status(row, {ScheduledJob.STATUS_RUNNING})
        row.status = ScheduledJob.STATUS_SUCCEEDED
        row.completed_at = timezone.now()
        row.last_error_summary = ""
        row.save(
            update_fields=[
                "status",
                "completed_at",
                "last_error_summary",
                "updated_at",
            ]
        )
    return row


def mark_job_failed(job_id, error_summary):
    with transaction.atomic():
        row = _locked_job(job_id)
        _require_status(row, {ScheduledJob.STATUS_RUNNING})
        row.status = ScheduledJob.STATUS_FAILED
        row.completed_at = timezone.now()
        row.last_error_summary = _clean_error_summary(error_summary)
        row.save(
            update_fields=[
                "status",
                "completed_at",
                "last_error_summary",
                "updated_at",
            ]
        )
    return row


def _enqueue_idempotently(cleaned):
    try:
        with transaction.atomic():
            row, created = ScheduledJob.objects.get_or_create(
                idempotency_key=cleaned["idempotency_key"],
                defaults=cleaned,
            )
    except IntegrityError:
        row = ScheduledJob.objects.get(idempotency_key=cleaned["idempotency_key"])
        created = False
    if not created and row.status in _TERMINAL_STATUSES:
        raise ValidationError(
            {"idempotency_key": "Idempotency key already belongs to a completed job."}
        )
    return row, created


def _locked_job(job_id):
    try:
        return ScheduledJob.objects.select_for_update().get(job_id=job_id)
    except ScheduledJob.DoesNotExist as exc:
        raise ValidationError({"job_id": "Scheduled job was not found."}) from exc


def _require_status(row, allowed_statuses):
    if row.status not in allowed_statuses:
        expected = ", ".join(sorted(allowed_statuses))
        raise ValidationError(
            {"status": f"Cannot transition job from {row.status}; expected {expected}."}
        )


def _clean_enqueue_args(
    *, job_type, due_at, idempotency_key, related_entity_type, related_entity_id
):
    field_errors = {}
    cleaned_job_type = _clean_required_string("job_type", job_type, field_errors)
    if cleaned_job_type and cleaned_job_type not in _ALLOWED_JOB_TYPES:
        field_errors["job_type"] = (
            "Must be one of compliance_reminder, default_assessment, dpd_calculation, "
            "interest_accrual, notification_generation, reminder_generation, report_export, "
            "workflow_task_reconciliation."
        )
    if due_at is None:
        field_errors["due_at"] = "This field is required."
    cleaned_related_type = _clean_optional_string(related_entity_type)
    if related_entity_id and not cleaned_related_type:
        field_errors["related_entity_type"] = (
            "This field is required when related_entity_id is supplied."
        )
    if cleaned_related_type and related_entity_id is None:
        field_errors["related_entity_id"] = (
            "This field is required when related_entity_type is supplied."
        )
    if field_errors:
        raise ValidationError(field_errors)
    return {
        "job_type": cleaned_job_type,
        "status": ScheduledJob.STATUS_QUEUED,
        "due_at": due_at,
        "related_entity_type": cleaned_related_type,
        "related_entity_id": related_entity_id,
        "idempotency_key": _clean_optional_string(idempotency_key),
        "attempts": 0,
        "last_error_summary": "",
    }


def _clean_required_string(field, value, field_errors):
    cleaned = _clean_optional_string(value)
    if not cleaned:
        field_errors[field] = "This field is required."
    return cleaned


def _clean_optional_string(value):
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _clean_error_summary(value):
    cleaned = _clean_optional_string(value)
    if not cleaned:
        raise ValidationError({"last_error_summary": "This field is required."})
    return cleaned[:_MAX_ERROR_SUMMARY_LENGTH]
