import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("approvals", "0020_approvalaction_approver_display_name"),
        ("defaults", "0004_non_payment_note"),
        ("identity", "0004_auditlog_selector_manifest_sha256"),
        ("workflows", "0001_canonical_workflow_event"),
    ]

    operations = [
        migrations.CreateModel(
            name="RecoveryDecision",
            fields=[
                ("recovery_decision_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("decision", models.CharField(db_index=True, max_length=100)),
                ("decision_reason", models.TextField()),
                ("status", models.CharField(db_index=True, default="approved", max_length=60)),
                ("approval_evidence_json", models.JSONField(default=dict)),
                ("decided_by_role_code", models.CharField(max_length=100)),
                ("decided_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("approval_case", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="recovery_decision", to="approvals.approvalcase")),
                ("decided_by_user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="recovery_decisions", to="identity.user")),
                ("default_case", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="recovery_decision", to="defaults.defaultcase")),
                ("non_payment_note", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="recovery_decision", to="defaults.nonpaymentnote")),
                ("workflow_event", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="recovery_decision", to="workflows.workflowevent")),
            ],
            options={
                "db_table": "recovery_decisions",
                "ordering": ["-decided_at", "-recovery_decision_id"],
            },
        ),
        migrations.AddConstraint(
            model_name="recoverydecision",
            constraint=models.CheckConstraint(check=models.Q(("status", "approved")), name="recovery_decision_approved_only"),
        ),
        migrations.AddConstraint(
            model_name="recoverydecision",
            constraint=models.CheckConstraint(check=models.Q(models.Q(("decision", ""), _negated=True), models.Q(("decision_reason", ""), _negated=True)), name="recovery_decision_text_required"),
        ),
    ]
