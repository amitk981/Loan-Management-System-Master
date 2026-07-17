import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("configurations", "0002_version_history_approval_evidence"),
        ("identity", "0003_portal_member_auth"),
        (
            "members",
            "0014_remove_memberscopeassignment_uniq_member_scope_assignment_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="SourceBankAccountGovernance",
            fields=[
                (
                    "source_bank_account_governance_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("status", models.CharField(db_index=True, default="active", max_length=40)),
                ("source_facts_digest", models.CharField(max_length=64)),
                ("reason_digest", models.CharField(max_length=64)),
                ("request_id", models.CharField(max_length=255, unique=True)),
                (
                    "activated_at",
                    models.DateTimeField(db_index=True, default=django.utils.timezone.now),
                ),
                (
                    "activated_by_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="activated_source_bank_accounts",
                        to="identity.user",
                    ),
                ),
                (
                    "activation_audit",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="source_bank_governance",
                        to="identity.auditlog",
                    ),
                ),
                (
                    "bank_account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="source_bank_governance_records",
                        to="members.bankaccount",
                    ),
                ),
                (
                    "version_history",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="source_bank_governance",
                        to="configurations.versionhistory",
                    ),
                ),
            ],
            options={"db_table": "source_bank_account_governance"},
        ),
        migrations.AddConstraint(
            model_name="sourcebankaccountgovernance",
            constraint=models.CheckConstraint(
                check=models.Q(("status__in", ("active", "inactive"))),
                name="source_bank_governance_status_valid",
            ),
        ),
        migrations.AddConstraint(
            model_name="sourcebankaccountgovernance",
            constraint=models.UniqueConstraint(
                condition=models.Q(("status", "active")),
                fields=("status",),
                name="uniq_active_source_bank_governance",
            ),
        ),
    ]
