from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):
    dependencies = [("approvals", "0008_approvalaction")]

    operations = [
        migrations.AddField(
            model_name="approvalcase",
            name="closed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="approvalcase",
            name="reason_for_rejection",
            field=models.TextField(blank=True),
        ),
        migrations.CreateModel(
            name="SanctionDecision",
            fields=[
                ("sanction_decision_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("decision", models.CharField(db_index=True, max_length=60)),
                ("sanctioned_amount", models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True)),
                ("sanctioned_tenure_months", models.PositiveIntegerField(blank=True, null=True)),
                ("interest_rate_type", models.CharField(max_length=60)),
                ("interest_rate_value", models.DecimalField(blank=True, decimal_places=4, max_digits=8, null=True)),
                ("repayment_date", models.DateField(blank=True, null=True)),
                ("penal_interest_rate", models.DecimalField(blank=True, decimal_places=4, max_digits=8, null=True)),
                ("charges_json", models.JSONField(blank=True, default=dict)),
                ("security_required_summary", models.TextField()),
                ("conditions_precedent", models.TextField(blank=True)),
                ("decision_reason", models.TextField()),
                ("recorded_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("approval_case", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="sanction_decision", to="approvals.approvalcase")),
                ("loan_application", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="sanction_decision", to="applications.loanapplication")),
            ],
            options={"db_table": "sanction_decisions"},
        ),
        migrations.AddIndex(
            model_name="sanctiondecision",
            index=models.Index(fields=["decision", "recorded_at"], name="idx_sanction_decision_time"),
        ),
    ]
