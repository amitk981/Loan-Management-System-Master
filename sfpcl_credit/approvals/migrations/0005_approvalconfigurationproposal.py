import uuid

import django.db.models.deletion
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [("approvals", "0004_approval_configuration_history_constraints")]

    operations = [
        migrations.CreateModel(
            name="ApprovalConfigurationProposal",
            fields=[
                ("approval_configuration_proposal_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("proposal_type", models.CharField(db_index=True, max_length=40)),
                ("target_entity_id", models.UUIDField(blank=True, null=True)),
                ("payload_json", models.JSONField()),
                ("reason", models.TextField()),
                ("status", models.CharField(db_index=True, default="pending", max_length=20)),
                ("version", models.PositiveIntegerField(default=1)),
                ("made_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("decided_at", models.DateTimeField(blank=True, null=True)),
                ("rejection_reason", models.TextField(blank=True)),
                ("request_id", models.CharField(blank=True, max_length=255)),
                ("request_ip", models.CharField(blank=True, max_length=80)),
                ("request_user_agent", models.TextField(blank=True)),
                ("decided_by_user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="decided_approval_configuration_proposals", to="identity.user")),
                ("made_by_user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="made_approval_configuration_proposals", to="identity.user")),
            ],
            options={"db_table": "approval_configuration_proposals", "ordering": ["-made_at", "-approval_configuration_proposal_id"]},
        ),
        migrations.AddIndex(model_name="approvalconfigurationproposal", index=models.Index(fields=["status", "proposal_type"], name="idx_config_proposal_state")),
        migrations.AddConstraint(model_name="approvalconfigurationproposal", constraint=models.CheckConstraint(check=models.Q(("status__in", ["pending", "approved", "rejected"])), name="config_proposal_valid_status")),
        migrations.AddConstraint(model_name="approvalconfigurationproposal", constraint=models.CheckConstraint(check=models.Q(("version__gte", 1)), name="config_proposal_version_positive")),
    ]
