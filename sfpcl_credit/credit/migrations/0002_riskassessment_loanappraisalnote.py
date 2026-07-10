import django.db.models.deletion
import django.utils.timezone
import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("credit", "0001_credit_assessment_model_ownership"),
        ("identity", "0003_portal_member_auth"),
    ]

    operations = [
        migrations.CreateModel(
            name="RiskAssessment",
            fields=[
                ("risk_assessment_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("market_risk_rating", models.CharField(max_length=60)),
                ("operational_risk_rating", models.CharField(max_length=60)),
                ("borrower_risk_rating", models.CharField(max_length=60)),
                ("overall_risk_rating", models.CharField(db_index=True, max_length=60)),
                ("risk_mitigation_notes", models.TextField(blank=True)),
                ("assessed_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("assessed_by_user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="risk_assessments", to="identity.user")),
                ("loan_application", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="risk_assessment", to="applications.loanapplication")),
            ],
            options={
                "db_table": "risk_assessments",
                "indexes": [models.Index(fields=["loan_application"], name="idx_risk_app"), models.Index(fields=["overall_risk_rating"], name="idx_risk_overall")],
            },
        ),
        migrations.CreateModel(
            name="LoanAppraisalNote",
            fields=[
                ("loan_appraisal_note_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("prepared_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("tat_due_at", models.DateTimeField(db_index=True)),
                ("tat_status", models.CharField(db_index=True, max_length=60)),
                ("eligibility_assessment_id_snapshot", models.UUIDField()),
                ("loan_limit_assessment_id_snapshot", models.UUIDField()),
                ("borrower_summary", models.TextField()),
                ("eligibility_summary", models.TextField()),
                ("loan_limit_summary", models.TextField()),
                ("recommended_amount", models.DecimalField(decimal_places=2, max_digits=18)),
                ("recommended_tenure_months", models.PositiveIntegerField(blank=True, null=True)),
                ("recommended_interest_type", models.CharField(blank=True, max_length=60)),
                ("recommended_security_summary", models.TextField()),
                ("recommendation", models.CharField(db_index=True, max_length=60)),
                ("appraisal_status", models.CharField(db_index=True, default="draft", max_length=60)),
                ("loan_application", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="appraisal_note", to="applications.loanapplication")),
                ("prepared_by_user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="prepared_appraisal_notes", to="identity.user")),
                ("reviewed_by_user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="reviewed_appraisal_notes", to="identity.user")),
                ("risk_assessment", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="appraisal_note", to="credit.riskassessment")),
            ],
            options={
                "db_table": "loan_appraisal_notes",
                "indexes": [models.Index(fields=["tat_status", "tat_due_at"], name="idx_appraisal_tat"), models.Index(fields=["recommendation"], name="idx_appraisal_recommend"), models.Index(fields=["appraisal_status"], name="idx_appraisal_status")],
            },
        ),
    ]
