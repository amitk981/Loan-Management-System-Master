import django.db.models.deletion
import django.utils.timezone
import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("closure", "0003_security_return_tracking"),
        ("identity", "0004_auditlog_selector_manifest_sha256"),
        ("loans", "0009_dpd_pointer_integrity"),
        ("workflows", "0001_canonical_workflow_event"),
    ]

    operations = [
        migrations.CreateModel(
            name="ArchiveRecord",
            fields=[
                ("archive_record_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("file_location_physical", models.CharField(blank=True, max_length=255, null=True)),
                ("file_location_digital", models.CharField(blank=True, max_length=255, null=True)),
                ("retention_start_date", models.DateField()),
                ("retention_until_date", models.DateField(db_index=True)),
                ("archived_by_role_code", models.CharField(max_length=100)),
                ("archived_at", models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ("destruction_eligible_flag", models.BooleanField(default=False)),
                ("destruction_certificate_id", models.UUIDField(blank=True, null=True)),
                ("idempotency_key_digest", models.CharField(max_length=64, unique=True)),
                ("payload_digest", models.CharField(max_length=64)),
                ("archive_audit", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="archive_record", to="identity.auditlog")),
                ("archive_workflow_event", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="archive_record", to="workflows.workflowevent")),
                ("archived_by_user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="archived_loan_files", to="identity.user")),
                ("loan_account", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="archive_record", to="loans.loanaccount")),
                ("loan_closure", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="archive_record", to="closure.loanclosure")),
            ],
            options={"db_table": "archive_records"},
        ),
        migrations.AddConstraint(
            model_name="archiverecord",
            constraint=models.CheckConstraint(
                check=(models.Q(file_location_physical__isnull=False) & ~models.Q(file_location_physical="")) | (models.Q(file_location_digital__isnull=False) & ~models.Q(file_location_digital="")),
                name="archive_record_location_required",
            ),
        ),
        migrations.AddConstraint(
            model_name="archiverecord",
            constraint=models.CheckConstraint(check=models.Q(retention_until_date__gte=models.F("retention_start_date")), name="archive_retention_dates_ordered"),
        ),
        migrations.AddConstraint(
            model_name="archiverecord",
            constraint=models.CheckConstraint(check=~models.Q(archived_by_role_code=""), name="archive_actor_role_required"),
        ),
        migrations.AddConstraint(
            model_name="archiverecord",
            constraint=models.CheckConstraint(check=models.Q(destruction_eligible_flag=False) & models.Q(destruction_certificate_id__isnull=True), name="archive_destruction_future_only"),
        ),
    ]
