import uuid

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [("loans", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="RepaymentSchedule",
            fields=[
                (
                    "repayment_schedule_id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("installment_number", models.PositiveIntegerField()),
                ("due_date", models.DateField(db_index=True)),
                ("principal_due", models.DecimalField(decimal_places=2, max_digits=18)),
                ("interest_due", models.DecimalField(decimal_places=2, max_digits=18)),
                ("charges_due", models.DecimalField(decimal_places=2, max_digits=18)),
                ("total_due", models.DecimalField(decimal_places=2, max_digits=18)),
                (
                    "paid_principal",
                    models.DecimalField(decimal_places=2, default=0, max_digits=18),
                ),
                (
                    "paid_interest",
                    models.DecimalField(decimal_places=2, default=0, max_digits=18),
                ),
                (
                    "paid_charges",
                    models.DecimalField(decimal_places=2, default=0, max_digits=18),
                ),
                ("schedule_status", models.CharField(db_index=True, max_length=60)),
                ("extended_due_date", models.DateField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "loan_account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="repayment_schedule_lines",
                        to="loans.loanaccount",
                    ),
                ),
            ],
            options={
                "db_table": "repayment_schedules",
                "ordering": ["installment_number", "repayment_schedule_id"],
                "indexes": [
                    models.Index(
                        fields=["loan_account", "due_date"],
                        name="idx_schedule_account_due",
                    )
                ],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("loan_account", "installment_number"),
                        name="uniq_schedule_installment",
                    ),
                    models.CheckConstraint(
                        check=models.Q(("installment_number__gt", 0)),
                        name="schedule_installment_positive",
                    ),
                    models.CheckConstraint(
                        check=(
                            models.Q(("principal_due__gte", 0))
                            & models.Q(("interest_due__gte", 0))
                            & models.Q(("charges_due__gte", 0))
                            & models.Q(("total_due__gte", 0))
                            & models.Q(("paid_principal__gte", 0))
                            & models.Q(("paid_interest__gte", 0))
                            & models.Q(("paid_charges__gte", 0))
                        ),
                        name="schedule_amounts_nonnegative",
                    ),
                    models.CheckConstraint(
                        check=models.Q(
                            (
                                "total_due",
                                models.F("principal_due")
                                + models.F("interest_due")
                                + models.F("charges_due"),
                            )
                        ),
                        name="schedule_total_matches_parts",
                    ),
                    models.CheckConstraint(
                        check=models.Q(
                            (
                                "schedule_status__in",
                                ("pending", "paid", "overdue"),
                            )
                        ),
                        name="schedule_status_bounded",
                    ),
                ],
            },
        )
    ]
