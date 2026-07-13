import django.db.models.deletion
import django.utils.timezone
import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("approvals", "0007_approvalcase_enrichment_snapshot"),
        ("identity", "0003_portal_member_auth"),
    ]

    operations = [
        migrations.CreateModel(
            name="ApprovalAction",
            fields=[
                (
                    "approval_action_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("approver_role_code", models.CharField(db_index=True, max_length=100)),
                ("decision", models.CharField(db_index=True, max_length=60)),
                ("comments", models.TextField(blank=True, null=True)),
                ("acted_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("digital_signature_id", models.UUIDField(blank=True, null=True)),
                ("ip_address", models.CharField(blank=True, max_length=80, null=True)),
                ("user_agent", models.TextField(blank=True, null=True)),
                (
                    "approval_case",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="actions",
                        to="approvals.approvalcase",
                    ),
                ),
                (
                    "approver_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="approval_actions",
                        to="identity.user",
                    ),
                ),
            ],
            options={
                "db_table": "approval_actions",
                "ordering": ["acted_at", "approval_action_id"],
                "indexes": [
                    models.Index(
                        fields=["approval_case", "decision"],
                        name="idx_action_case_decision",
                    )
                ],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("approval_case", "approver_user"),
                        name="unique_case_approver_action",
                    ),
                    models.CheckConstraint(
                        check=models.Q(
                            ("decision__in", ["approved", "rejected", "returned"])
                        ),
                        name="approval_action_valid_decision",
                    ),
                ],
            },
        )
    ]
