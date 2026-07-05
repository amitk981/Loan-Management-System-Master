# Generated for Ralph slice 003E.

import uuid

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("identity", "0002_permission_rolepermission_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="LoanPolicyConfig",
            fields=[
                (
                    "loan_policy_config_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("policy_name", models.CharField(max_length=255)),
                ("policy_version", models.CharField(max_length=40)),
                ("effective_from", models.DateField(db_index=True)),
                ("effective_to", models.DateField(blank=True, db_index=True, null=True)),
                ("short_term_duration_months", models.IntegerField()),
                ("min_secured_loan_months", models.IntegerField(blank=True, null=True)),
                ("max_secured_loan_years", models.IntegerField(blank=True, null=True)),
                (
                    "approval_threshold_amount",
                    models.DecimalField(decimal_places=2, max_digits=18),
                ),
                (
                    "default_scale_of_finance_per_acre_amount",
                    models.DecimalField(decimal_places=2, max_digits=18),
                ),
                (
                    "share_limit_percentage",
                    models.DecimalField(
                        blank=True, decimal_places=4, max_digits=8, null=True
                    ),
                ),
                (
                    "per_share_cap_amount",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=18, null=True
                    ),
                ),
                ("interest_rate_type", models.CharField(max_length=60)),
                (
                    "interest_benchmark",
                    models.CharField(blank=True, max_length=120, null=True),
                ),
                (
                    "penal_interest_rate",
                    models.DecimalField(
                        blank=True, decimal_places=4, max_digits=8, null=True
                    ),
                ),
                ("rekyc_frequency_months", models.IntegerField()),
                ("record_retention_years", models.IntegerField()),
                ("grace_period_months", models.IntegerField()),
                ("non_intentional_extension_months", models.IntegerField()),
                (
                    "board_approval_reference",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "status",
                    models.CharField(db_index=True, default="draft", max_length=60),
                ),
            ],
            options={
                "db_table": "loan_policy_configs",
                "ordering": ["-effective_from", "-loan_policy_config_id"],
            },
        ),
        migrations.CreateModel(
            name="VersionHistory",
            fields=[
                (
                    "version_history_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "versioned_entity_type",
                    models.CharField(db_index=True, max_length=80),
                ),
                ("versioned_entity_id", models.UUIDField(db_index=True)),
                ("version_number", models.CharField(max_length=40)),
                ("change_summary", models.TextField()),
                (
                    "board_approval_reference",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("effective_from", models.DateField()),
                ("effective_to", models.DateField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "approver_user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="approved_version_histories",
                        to="identity.user",
                    ),
                ),
                (
                    "author_user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="authored_version_histories",
                        to="identity.user",
                    ),
                ),
                (
                    "reviewer_user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="reviewed_version_histories",
                        to="identity.user",
                    ),
                ),
            ],
            options={
                "db_table": "version_histories",
                "ordering": ["-created_at", "-version_history_id"],
            },
        ),
    ]
