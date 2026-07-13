import uuid

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("approvals", "0015_generalmeetingapproval_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="CreditSanctionRegisterEntry",
            fields=[
                ("credit_sanction_register_entry_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("application_number", models.CharField(max_length=40)),
                ("borrower_name", models.CharField(max_length=255)),
                ("borrower_type", models.CharField(max_length=60)),
                ("requested_amount", models.DecimalField(decimal_places=2, max_digits=18)),
                ("eligible_amount", models.DecimalField(decimal_places=2, max_digits=18)),
                ("recommended_amount", models.DecimalField(decimal_places=2, max_digits=18)),
                ("sanctioned_amount", models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True)),
                ("authority_applied_summary", models.TextField()),
                ("approver_names_json", models.JSONField(default=list)),
                ("approval_date", models.DateField(db_index=True)),
                ("decision", models.CharField(choices=[("sanctioned", "Sanctioned"), ("rejected", "Rejected")], db_index=True, max_length=60)),
                ("reasons", models.TextField()),
                ("exception_reference_json", models.JSONField(blank=True, null=True)),
                ("conflict_abstention_details_json", models.JSONField(default=list)),
                ("general_meeting_approval_reference_json", models.JSONField(blank=True, null=True)),
                ("recorded_at", models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ("approval_case", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="credit_sanction_register_entry", to="approvals.approvalcase")),
                ("loan_application", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="credit_sanction_register_entries", to="applications.loanapplication")),
                ("member", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="credit_sanction_register_entries", to="members.member")),
                ("recorded_by_user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="recorded_credit_sanction_register_entries", to="identity.user")),
                ("sanction_decision", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="credit_sanction_register_entry", to="approvals.sanctiondecision")),
                ("workflow_event", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="credit_sanction_register_entry", to="workflows.workflowevent")),
            ],
            options={
                "db_table": "credit_sanction_register_entries",
                "ordering": ["-approval_date", "-recorded_at", "-credit_sanction_register_entry_id"],
                "indexes": [models.Index(fields=["decision", "approval_date"], name="idx_sanction_register_decision")],
                "constraints": [
                    models.CheckConstraint(check=models.Q(("decision__in", ["sanctioned", "rejected"])), name="sanction_register_valid_decision"),
                    models.CheckConstraint(check=models.Q(models.Q(("decision", "sanctioned"), ("sanction_decision__isnull", False)), models.Q(("decision", "rejected"), ("sanction_decision__isnull", True)), _connector="OR"), name="sanction_register_decision_link"),
                ],
            },
        ),
    ]
