import uuid

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("compliance", "0004_grievance_grievancedocument_and_more"),
        ("identity", "0004_auditlog_selector_manifest_sha256"),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditObservation",
            fields=[
                (
                    "audit_observation_id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created_by_full_name",
                    models.CharField(max_length=200),
                ),
                (
                    "created_by_role_code",
                    models.CharField(max_length=80),
                ),
                (
                    "created_by_team_codes_json",
                    models.JSONField(default=list),
                ),
                (
                    "audit_scope",
                    models.CharField(db_index=True, max_length=40),
                ),
                (
                    "observation_text",
                    models.CharField(max_length=2000),
                ),
                (
                    "source_references_json",
                    models.JSONField(),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now
                    ),
                ),
                (
                    "created_by_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="audit_observations",
                        to="identity.user",
                    ),
                ),
            ],
            options={
                "db_table": "audit_observations",
                "ordering": ["-created_at", "-audit_observation_id"],
            },
        ),
        migrations.AddIndex(
            model_name="auditobservation",
            index=models.Index(
                fields=["created_by_user", "created_at"],
                name="idx_audit_obs_creator_time",
            ),
        ),
        migrations.AddConstraint(
            model_name="auditobservation",
            constraint=models.CheckConstraint(
                check=models.Q(("audit_scope", "audit_readonly")),
                name="audit_observation_scope_bounded",
            ),
        ),
    ]
