import uuid

from django.db import models


class ScheduledJob(models.Model):
    STATUS_QUEUED = "queued"
    STATUS_RUNNING = "running"
    STATUS_SUCCEEDED = "succeeded"
    STATUS_FAILED = "failed"
    STATUSES = {STATUS_QUEUED, STATUS_RUNNING, STATUS_SUCCEEDED, STATUS_FAILED}

    job_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job_type = models.CharField(max_length=120, db_index=True)
    status = models.CharField(
        max_length=40, default=STATUS_QUEUED, db_index=True
    )
    due_at = models.DateTimeField(db_index=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    related_entity_type = models.CharField(max_length=80, blank=True, null=True)
    related_entity_id = models.UUIDField(blank=True, null=True, db_index=True)
    idempotency_key = models.CharField(
        max_length=255, blank=True, null=True, unique=True
    )
    attempts = models.PositiveIntegerField(default=0)
    last_error_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "scheduled_jobs"
        ordering = ["due_at", "job_id"]
        indexes = [
            models.Index(fields=["status", "due_at"]),
            models.Index(fields=["related_entity_type", "related_entity_id"]),
        ]
