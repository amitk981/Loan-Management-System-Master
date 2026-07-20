import django.db.models.deletion
import uuid

from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):
    dependencies = [
        ("configurations", "0007_rate_status_approval_coherence"),
        ("identity", "0004_auditlog_selector_manifest_sha256"),
        ("loans", "0008_subsidiary_deduction_reconciliation"),
    ]

    operations = [
        migrations.CreateModel(
            name="CurrentRateProjectionDecision",
            fields=[
                (
                    "current_rate_projection_decision_id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("as_of_date", models.DateField(db_index=True)),
                ("idempotency_key", models.CharField(max_length=255, unique=True)),
                ("payload_digest", models.CharField(max_length=64)),
                ("old_interest_rate", models.DecimalField(decimal_places=4, max_digits=8)),
                ("current_interest_rate", models.DecimalField(decimal_places=4, max_digits=8)),
                ("projection_changed", models.BooleanField()),
                ("actor_role_codes_json", models.JSONField(default=list)),
                ("actor_type", models.CharField(max_length=20)),
                ("invocation", models.CharField(max_length=40)),
                ("created_at", models.DateTimeField(default=timezone.now)),
                (
                    "actor_user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="current_rate_projection_decisions",
                        to="identity.user",
                    ),
                ),
                (
                    "audit_log",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="current_rate_projection_decision",
                        to="identity.auditlog",
                    ),
                ),
                (
                    "loan_account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="current_rate_projection_decisions",
                        to="loans.loanaccount",
                    ),
                ),
                (
                    "rate_config",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="current_projection_decisions",
                        to="configurations.interestrateconfig",
                    ),
                ),
            ],
            options={"db_table": "current_rate_projection_decisions"},
        ),
        migrations.AddConstraint(
            model_name="currentrateprojectiondecision",
            constraint=models.UniqueConstraint(
                fields=("loan_account", "rate_config"),
                name="uniq_current_rate_account_version",
            ),
        ),
        migrations.AddIndex(
            model_name="currentrateprojectiondecision",
            index=models.Index(
                fields=["as_of_date", "loan_account"],
                name="idx_current_rate_date_account",
            ),
        ),
    ]
