import django.db.models.deletion
import django.db.models.expressions
import django.utils.timezone
import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("loans", "0005_bankstatementimport_bankstatementline_and_more")]

    operations = [
        migrations.CreateModel(
            name="RepaymentReversal",
            fields=[
                ("repayment_reversal_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("reversal_reason", models.CharField(max_length=500)),
                ("principal_restored", models.DecimalField(decimal_places=2, max_digits=18)),
                ("interest_restored", models.DecimalField(decimal_places=2, max_digits=18)),
                ("charges_restored", models.DecimalField(decimal_places=2, default=0, max_digits=18)),
                ("total_before", models.DecimalField(decimal_places=2, max_digits=18)),
                ("total_after", models.DecimalField(decimal_places=2, max_digits=18)),
                ("idempotency_key_digest", models.CharField(max_length=64, unique=True)),
                ("payload_digest", models.CharField(max_length=64)),
                ("reversed_at", models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
            ],
            options={"db_table": "repayment_reversals"},
        ),
        migrations.CreateModel(
            name="RepaymentReversalLedgerEntry",
            fields=[
                ("repayment_reversal_ledger_entry_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("transaction_date", models.DateField(db_index=True)),
                ("debit_amount", models.DecimalField(decimal_places=2, max_digits=18)),
                ("principal_balance", models.DecimalField(decimal_places=2, max_digits=18)),
                ("interest_balance", models.DecimalField(decimal_places=2, max_digits=18)),
                ("charges_balance", models.DecimalField(decimal_places=2, max_digits=18)),
                ("total_outstanding", models.DecimalField(decimal_places=2, max_digits=18)),
                ("actor_display_name", models.CharField(max_length=200)),
                ("created_at", models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
            ],
            options={"db_table": "repayment_reversal_ledger_entries", "ordering": ["created_at", "repayment_reversal_ledger_entry_id"]},
        ),
        migrations.CreateModel(
            name="RepaymentScheduleAllocation",
            fields=[
                ("repayment_schedule_allocation_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("principal_applied", models.DecimalField(decimal_places=2, max_digits=18)),
                ("interest_applied", models.DecimalField(decimal_places=2, max_digits=18)),
                ("schedule_status_before", models.CharField(max_length=60)),
                ("schedule_status_after", models.CharField(max_length=60)),
            ],
            options={"db_table": "repayment_schedule_allocations"},
        ),
        migrations.CreateModel(
            name="ManualAllocationApproval",
            fields=[
                ("manual_allocation_approval_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("bank_statement_line_id", models.UUIDField()),
                ("approved_amount", models.DecimalField(decimal_places=2, max_digits=18)),
                ("approval_reason", models.CharField(max_length=500)),
                ("idempotency_key_digest", models.CharField(max_length=64, unique=True)),
                ("payload_digest", models.CharField(max_length=64)),
                ("approved_at", models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ("approval_audit", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="manual_allocation_approval", to="identity.auditlog")),
                ("approved_by_user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="manual_allocation_approvals", to="identity.user")),
                ("loan_account", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="manual_allocation_approvals", to="loans.loanaccount")),
                ("repayment", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="manual_allocation_approval", to="loans.repayment")),
            ],
            options={"db_table": "manual_allocation_approvals"},
        ),
        migrations.AddField(
            model_name="repaymentallocation",
            name="decision_reason",
            field=models.CharField(default="Principal-first allocation.", max_length=500),
        ),
        migrations.AddField(
            model_name="repaymentallocation",
            name="idempotency_key_digest",
            field=models.CharField(blank=True, max_length=64, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="repaymentallocation",
            name="payload_digest",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name="repaymentallocation",
            name="manual_approval",
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="allocation", to="loans.manualallocationapproval"),
        ),
        migrations.AddField(
            model_name="repaymentallocation",
            name="loan_status_before",
            field=models.CharField(default="active", max_length=80),
        ),
        migrations.AddField(
            model_name="repaymentallocation",
            name="loan_status_after",
            field=models.CharField(default="partially_repaid", max_length=80),
        ),
        migrations.RemoveConstraint(model_name="repayment", name="repayment_allocation_status_bounded"),
        migrations.AddConstraint(
            model_name="repayment",
            constraint=models.CheckConstraint(check=models.Q(allocation_status__in=("pending", "allocated", "allocated_with_exception", "reversed")), name="repayment_allocation_status_bounded"),
        ),
        migrations.AddField(
            model_name="repaymentreversal",
            name="allocation",
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="reversal", to="loans.repaymentallocation"),
        ),
        migrations.AddField(
            model_name="repaymentreversal",
            name="loan_account",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="repayment_reversals", to="loans.loanaccount"),
        ),
        migrations.AddField(
            model_name="repaymentreversal",
            name="repayment",
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="reversal", to="loans.repayment"),
        ),
        migrations.AddField(
            model_name="repaymentreversal",
            name="reversal_audit",
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="repayment_reversal", to="identity.auditlog"),
        ),
        migrations.AddField(
            model_name="repaymentreversal",
            name="reversed_by_user",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="repayment_reversals", to="identity.user"),
        ),
        migrations.AddField(
            model_name="repaymentreversalledgerentry",
            name="actor_user",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="repayment_reversal_ledger_entries", to="identity.user"),
        ),
        migrations.AddField(
            model_name="repaymentreversalledgerentry",
            name="loan_account",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="repayment_reversal_ledger_entries", to="loans.loanaccount"),
        ),
        migrations.AddField(
            model_name="repaymentreversalledgerentry",
            name="reversal",
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="ledger_entry", to="loans.repaymentreversal"),
        ),
        migrations.AddField(
            model_name="repaymentscheduleallocation",
            name="allocation",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="schedule_applications", to="loans.repaymentallocation"),
        ),
        migrations.AddField(
            model_name="repaymentscheduleallocation",
            name="repayment_schedule",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="allocation_applications", to="loans.repaymentschedule"),
        ),
        migrations.AddConstraint(
            model_name="manualallocationapproval",
            constraint=models.CheckConstraint(check=models.Q(approved_amount__gt=0), name="manual_allocation_approval_amount_positive"),
        ),
        migrations.AddConstraint(
            model_name="manualallocationapproval",
            constraint=models.CheckConstraint(check=~models.Q(approval_reason=""), name="manual_allocation_approval_reason_required"),
        ),
        migrations.AddConstraint(
            model_name="repaymentallocation",
            constraint=models.CheckConstraint(
                check=~models.Q(decision_reason=""),
                name="repayment_allocation_reason_required",
            ),
        ),
        migrations.AddConstraint(
            model_name="repaymentreversal",
            constraint=models.CheckConstraint(check=models.Q(principal_restored__gte=0) & models.Q(interest_restored__gte=0) & models.Q(charges_restored=0) & models.Q(total_before__gte=0) & models.Q(total_after__gte=0), name="repayment_reversal_amounts_valid"),
        ),
        migrations.AddConstraint(
            model_name="repaymentreversal",
            constraint=models.CheckConstraint(check=~models.Q(reversal_reason=""), name="repayment_reversal_reason_required"),
        ),
        migrations.AddConstraint(
            model_name="repaymentreversalledgerentry",
            constraint=models.CheckConstraint(check=models.Q(debit_amount__gt=0) & models.Q(principal_balance__gte=0) & models.Q(interest_balance__gte=0) & models.Q(charges_balance__gte=0) & models.Q(total_outstanding__gte=0), name="repayment_reversal_ledger_amounts_valid"),
        ),
        migrations.AddConstraint(
            model_name="repaymentreversalledgerentry",
            constraint=models.CheckConstraint(check=models.Q(total_outstanding=django.db.models.expressions.CombinedExpression(django.db.models.expressions.CombinedExpression(models.F("principal_balance"), "+", models.F("interest_balance")), "+", models.F("charges_balance"))), name="repayment_reversal_ledger_total_parts"),
        ),
        migrations.AddConstraint(
            model_name="repaymentscheduleallocation",
            constraint=models.UniqueConstraint(fields=("allocation", "repayment_schedule"), name="uniq_allocation_schedule_application"),
        ),
        migrations.AddConstraint(
            model_name="repaymentscheduleallocation",
            constraint=models.CheckConstraint(check=models.Q(principal_applied__gte=0) & models.Q(interest_applied__gte=0), name="schedule_allocation_amounts_nonnegative"),
        ),
        migrations.AddConstraint(
            model_name="repaymentscheduleallocation",
            constraint=models.CheckConstraint(check=models.Q(principal_applied__gt=0) | models.Q(interest_applied__gt=0), name="schedule_allocation_has_amount"),
        ),
    ]
