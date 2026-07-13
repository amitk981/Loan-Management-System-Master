import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("applications", "0010_loanapplication_nominee"),
        ("credit", "0005_appraisalreviewdecision"),
        ("identity", "0003_portal_member_auth"),
    ]

    operations = [
        migrations.CreateModel(
            name="ApprovalCase",
            fields=[
                (
                    "approval_case_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "approval_type",
                    models.CharField(db_index=True, default="sanction", max_length=80),
                ),
                (
                    "current_status",
                    models.CharField(db_index=True, default="pending", max_length=60),
                ),
                (
                    "exception_required_flag",
                    models.BooleanField(db_index=True, default=False),
                ),
                ("submission_remarks", models.TextField()),
                (
                    "submitted_at",
                    models.DateTimeField(db_index=True, default=django.utils.timezone.now),
                ),
                (
                    "loan_appraisal_note",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="sanction_approval_case",
                        to="credit.loanappraisalnote",
                    ),
                ),
                (
                    "loan_application",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="sanction_approval_case",
                        to="applications.loanapplication",
                    ),
                ),
                (
                    "submitted_by_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="submitted_sanction_cases",
                        to="identity.user",
                    ),
                ),
            ],
            options={
                "db_table": "approval_cases",
                "indexes": [
                    models.Index(
                        fields=["approval_type", "current_status"],
                        name="idx_approval_type_status",
                    ),
                    models.Index(
                        fields=["exception_required_flag", "current_status"],
                        name="idx_approval_exception",
                    ),
                ],
            },
        ),
    ]
