import django.db.models.deletion
import django.utils.timezone
import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("compliance", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Section186Tracker",
            fields=[
                ("section_186_tracker_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("financial_year", models.CharField(db_index=True, max_length=20)),
                ("quarter", models.CharField(db_index=True, max_length=10)),
                ("paid_up_capital_amount", models.DecimalField(decimal_places=2, max_digits=18)),
                ("free_reserves_amount", models.DecimalField(decimal_places=2, max_digits=18)),
                ("securities_premium_amount", models.DecimalField(decimal_places=2, max_digits=18)),
                ("limit_60_percent_basis_amount", models.DecimalField(decimal_places=2, max_digits=18)),
                ("limit_100_percent_basis_amount", models.DecimalField(decimal_places=2, max_digits=18)),
                ("applicable_limit_amount", models.DecimalField(decimal_places=2, max_digits=18)),
                ("total_loans_exposure_amount", models.DecimalField(decimal_places=2, max_digits=18)),
                ("headroom_amount", models.DecimalField(decimal_places=2, max_digits=18)),
                ("within_limit_flag", models.BooleanField(db_index=True)),
                ("special_resolution_required_flag", models.BooleanField()),
                ("prepared_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("submitted_for_review_at", models.DateTimeField(blank=True, null=True)),
                ("review_decision", models.CharField(blank=True, max_length=40)),
                ("review_comments", models.TextField(blank=True)),
                ("presented_to_board_flag", models.BooleanField(default=False)),
                ("board_evidence_snapshot_json", models.JSONField(default=dict)),
                ("input_snapshot_json", models.JSONField()),
                ("result_snapshot_json", models.JSONField()),
                ("reviewer_snapshot_json", models.JSONField()),
                ("evidence_snapshot_json", models.JSONField()),
                ("evidence", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="section_186_trackers", to="compliance.complianceevidence")),
                ("board_document", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="section_186_board_reviews", to="documents.documentfile")),
                ("prepared_by_user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="prepared_section_186_trackers", to="identity.user")),
                ("reviewer_user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="section_186_trackers_to_review", to="identity.user")),
                ("task", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="section_186_tracker", to="compliance.compliancetask")),
            ],
            options={
                "db_table": "section_186_trackers",
                "ordering": ["financial_year", "quarter"],
                "constraints": [
                    models.UniqueConstraint(fields=("financial_year", "quarter"), name="uniq_section_186_period"),
                    models.CheckConstraint(check=models.Q(("review_decision__in", ("", "accepted", "rejected"))), name="section_186_review_bounded"),
                    models.CheckConstraint(check=~models.Q(("prepared_by_user", models.F("reviewer_user"))), name="section_186_maker_checker"),
                ],
            },
        ),
        migrations.CreateModel(
            name="NbfcPrincipalBusinessTest",
            fields=[
                ("nbfc_principal_test_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("financial_year", models.CharField(db_index=True, max_length=20)),
                ("quarter", models.CharField(db_index=True, max_length=10)),
                ("financial_assets_amount", models.DecimalField(decimal_places=2, max_digits=18)),
                ("total_assets_amount", models.DecimalField(decimal_places=2, max_digits=18)),
                ("financial_asset_ratio", models.DecimalField(decimal_places=4, max_digits=8)),
                ("financial_income_amount", models.DecimalField(decimal_places=2, max_digits=18)),
                ("gross_income_amount", models.DecimalField(decimal_places=2, max_digits=18)),
                ("financial_income_ratio", models.DecimalField(decimal_places=4, max_digits=8)),
                ("early_warning_threshold_ratio", models.DecimalField(decimal_places=4, max_digits=6)),
                ("registration_triggered_flag", models.BooleanField(db_index=True)),
                ("one_ratio_above_statutory_flag", models.BooleanField(default=False)),
                ("early_warning_flag", models.BooleanField()),
                ("presented_to_board_flag", models.BooleanField(default=False)),
                ("prepared_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("submitted_for_review_at", models.DateTimeField(blank=True, null=True)),
                ("review_decision", models.CharField(blank=True, max_length=40)),
                ("review_comments", models.TextField(blank=True)),
                ("board_evidence_snapshot_json", models.JSONField(default=dict)),
                ("input_snapshot_json", models.JSONField()),
                ("result_snapshot_json", models.JSONField()),
                ("reviewer_snapshot_json", models.JSONField()),
                ("evidence_snapshot_json", models.JSONField()),
                ("evidence", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="nbfc_principal_tests", to="compliance.complianceevidence")),
                ("board_document", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="nbfc_board_reviews", to="documents.documentfile")),
                ("prepared_by_user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="prepared_nbfc_principal_tests", to="identity.user")),
                ("reviewer_user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="nbfc_principal_tests_to_review", to="identity.user")),
                ("task", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="nbfc_principal_test", to="compliance.compliancetask")),
            ],
            options={
                "db_table": "nbfc_principal_tests",
                "ordering": ["financial_year", "quarter"],
                "constraints": [
                    models.UniqueConstraint(fields=("financial_year", "quarter"), name="uniq_nbfc_principal_period"),
                    models.CheckConstraint(check=models.Q(("review_decision__in", ("", "accepted", "rejected"))), name="nbfc_principal_review_bounded"),
                    models.CheckConstraint(check=~models.Q(("prepared_by_user", models.F("reviewer_user"))), name="nbfc_principal_maker_checker"),
                ],
            },
        ),
    ]
