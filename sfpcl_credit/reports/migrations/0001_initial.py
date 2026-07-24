import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("identity", "0004_auditlog_selector_manifest_sha256"),
    ]

    operations = [
        migrations.CreateModel(
            name="ReportExportJob",
            fields=[
                (
                    "export_job_id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("report_code", models.CharField(max_length=80)),
                ("canonical_filters", models.JSONField(default=dict)),
                ("filters_digest", models.CharField(max_length=64)),
                ("export_format", models.CharField(max_length=12)),
                ("idempotency_key", models.CharField(max_length=255)),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("queued", "Queued"),
                            ("running", "Running"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                        ],
                        default="queued",
                        max_length=20,
                    ),
                ),
                ("requested_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("failure_code", models.CharField(blank=True, max_length=80)),
                ("storage_key", models.CharField(blank=True, max_length=500)),
                ("checksum_sha256", models.CharField(blank=True, max_length=64)),
                ("file_size_bytes", models.PositiveBigIntegerField(blank=True, null=True)),
                ("content_type", models.CharField(blank=True, max_length=120)),
                ("download_expires_at", models.DateTimeField(blank=True, null=True)),
                ("file_deleted_at", models.DateTimeField(blank=True, null=True)),
                ("worker_claim_id", models.UUIDField(blank=True, null=True)),
                ("worker_lease_expires_at", models.DateTimeField(blank=True, null=True)),
                (
                    "actor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="report_export_jobs",
                        to="identity.user",
                    ),
                ),
            ],
            options={
                "db_table": "report_export_jobs",
                "indexes": [
                    models.Index(
                        fields=["state", "requested_at"],
                        name="idx_report_export_state_time",
                    ),
                    models.Index(
                        fields=["actor", "requested_at"],
                        name="idx_report_export_actor_time",
                    ),
                ],
                "constraints": [
                    models.UniqueConstraint(
                        fields=(
                            "actor",
                            "report_code",
                            "filters_digest",
                            "export_format",
                            "idempotency_key",
                        ),
                        name="uniq_report_export_request_identity",
                    ),
                    models.CheckConstraint(
                        check=models.Q(
                            ("state__in", ["queued", "running", "completed", "failed"])
                        ),
                        name="report_export_state_bounded",
                    ),
                ],
            },
        ),
    ]
