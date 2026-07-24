import uuid

from django.db import models
from django.utils import timezone


class ReportExportJob(models.Model):
    STATE_QUEUED = "queued"
    STATE_RUNNING = "running"
    STATE_COMPLETED = "completed"
    STATE_FAILED = "failed"
    STATES = (
        (STATE_QUEUED, "Queued"),
        (STATE_RUNNING, "Running"),
        (STATE_COMPLETED, "Completed"),
        (STATE_FAILED, "Failed"),
    )

    export_job_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    actor = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="report_export_jobs",
    )
    report_code = models.CharField(max_length=80)
    canonical_filters = models.JSONField(default=dict)
    filters_digest = models.CharField(max_length=64)
    export_format = models.CharField(max_length=12)
    idempotency_key = models.CharField(max_length=255)
    state = models.CharField(
        max_length=20,
        choices=STATES,
        default=STATE_QUEUED,
    )
    requested_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    failure_code = models.CharField(max_length=80, blank=True)
    storage_key = models.CharField(max_length=500, blank=True)
    checksum_sha256 = models.CharField(max_length=64, blank=True)
    file_size_bytes = models.PositiveBigIntegerField(blank=True, null=True)
    content_type = models.CharField(max_length=120, blank=True)
    download_expires_at = models.DateTimeField(blank=True, null=True)
    file_deleted_at = models.DateTimeField(blank=True, null=True)
    worker_claim_id = models.UUIDField(blank=True, null=True)
    worker_lease_expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "report_export_jobs"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "actor",
                    "report_code",
                    "filters_digest",
                    "export_format",
                    "idempotency_key",
                ],
                name="uniq_report_export_request_identity",
            ),
            models.CheckConstraint(
                check=models.Q(
                    state__in=[
                        "queued",
                        "running",
                        "completed",
                        "failed",
                    ]
                ),
                name="report_export_state_bounded",
            ),
        ]
        indexes = [
            models.Index(
                fields=["state", "requested_at"],
                name="idx_report_export_state_time",
            ),
            models.Index(
                fields=["actor", "requested_at"],
                name="idx_report_export_actor_time",
            ),
        ]
