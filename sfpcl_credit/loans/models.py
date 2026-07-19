import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class ImmutableLoanTermsQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError({"loan_terms": "Loan terms are immutable."})

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValidationError({"loan_terms": "Loan terms are immutable."})

    def delete(self):
        raise ValidationError({"loan_terms": "Loan terms are immutable."})


class AppendOnlyLoanStatusHistoryQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError({"loan_status_history": "Loan status history is append-only."})

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValidationError({"loan_status_history": "Loan status history is append-only."})

    def delete(self):
        raise ValidationError({"loan_status_history": "Loan status history is append-only."})


class LoanAccount(models.Model):
    STATUS_SANCTIONED = "sanctioned"
    LOAN_TYPES = {"short_term", "long_term"}

    loan_account_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    loan_application = models.OneToOneField(
        "applications.LoanApplication",
        on_delete=models.PROTECT,
        related_name="loan_account",
    )
    loan_account_number = models.CharField(max_length=80)
    loan_account_number_normalized = models.CharField(max_length=80, unique=True)
    member = models.ForeignKey(
        "members.Member", on_delete=models.PROTECT, related_name="loan_accounts"
    )
    sap_customer_code = models.ForeignKey(
        "sap_workflow.SapCustomerCode",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="loan_accounts",
    )
    sanction_decision = models.OneToOneField(
        "approvals.SanctionDecision",
        on_delete=models.PROTECT,
        related_name="loan_account",
    )
    sanctioned_amount = models.DecimalField(max_digits=18, decimal_places=2)
    disbursed_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    loan_type = models.CharField(max_length=60, db_index=True)
    tenure_start_date = models.DateField(null=True, blank=True)
    tenure_end_date = models.DateField(null=True, blank=True)
    interest_rate_type = models.CharField(max_length=60)
    current_interest_rate = models.DecimalField(max_digits=8, decimal_places=4)
    repayment_date = models.DateField(db_index=True)
    principal_outstanding = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    interest_outstanding = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    charges_outstanding = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total_outstanding = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    loan_account_status = models.CharField(
        max_length=80, default=STATUS_SANCTIONED, db_index=True
    )
    current_dpd_status_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "loan_accounts"
        indexes = [
            models.Index(fields=["member", "loan_account_status"], name="idx_loan_member_status"),
            models.Index(fields=["loan_type", "repayment_date"], name="idx_loan_type_repay"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(sanctioned_amount__gt=0),
                name="loan_account_sanction_positive",
            ),
            models.CheckConstraint(
                check=models.Q(disbursed_amount__gte=0),
                name="loan_account_disbursed_nonnegative",
            ),
            models.CheckConstraint(
                check=models.Q(principal_outstanding__gte=0),
                name="loan_account_principal_nonnegative",
            ),
            models.CheckConstraint(
                check=models.Q(interest_outstanding__gte=0),
                name="loan_account_interest_nonnegative",
            ),
            models.CheckConstraint(
                check=models.Q(charges_outstanding__gte=0),
                name="loan_account_charges_nonnegative",
            ),
            models.CheckConstraint(
                check=models.Q(total_outstanding__gte=0),
                name="loan_account_total_nonnegative",
            ),
            models.CheckConstraint(
                check=models.Q(loan_type__in=("short_term", "long_term")),
                name="loan_account_type_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(disbursed_amount__lte=models.F("sanctioned_amount")),
                name="loan_account_disbursed_lte_sanction",
            ),
        ]


class LoanTerms(models.Model):
    loan_terms_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    loan_account = models.OneToOneField(
        LoanAccount, on_delete=models.PROTECT, related_name="terms"
    )
    borrower_details_snapshot_json = models.JSONField()
    nominee_details_snapshot_json = models.JSONField()
    shareholding_snapshot_json = models.JSONField()
    facility_type = models.CharField(max_length=60)
    loan_amount = models.DecimalField(max_digits=18, decimal_places=2)
    purpose = models.TextField()
    rate_of_interest = models.DecimalField(max_digits=8, decimal_places=4)
    interest_rate_type = models.CharField(max_length=60)
    interest_tenure = models.CharField(max_length=120)
    repayment_date = models.DateField()
    penalty_interest_rate = models.DecimalField(max_digits=8, decimal_places=4)
    other_charges_fees_json = models.JSONField()
    security_details_json = models.JSONField()
    dispute_resolution_text = models.TextField()
    term_sheet_document = models.ForeignKey(
        "documents.DocumentFile",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="term_sheet_loan_terms",
    )
    loan_agreement_document = models.ForeignKey(
        "documents.DocumentFile",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="loan_agreement_loan_terms",
    )
    created_at = models.DateTimeField(default=timezone.now)

    objects = ImmutableLoanTermsQuerySet.as_manager()

    class Meta:
        db_table = "loan_terms"
        constraints = [
            models.CheckConstraint(
                check=models.Q(loan_amount__gt=0), name="loan_terms_amount_positive"
            ),
            models.CheckConstraint(
                check=models.Q(facility_type__in=("short_term", "long_term")),
                name="loan_terms_facility_bounded",
            ),
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError({"loan_terms": "Loan terms are immutable."})
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError({"loan_terms": "Loan terms are immutable."})


class LoanStatusHistory(models.Model):
    loan_status_history_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    loan_account = models.ForeignKey(
        LoanAccount, on_delete=models.PROTECT, related_name="status_history"
    )
    from_status = models.CharField(max_length=80, null=True, blank=True)
    to_status = models.CharField(max_length=80, db_index=True)
    reason = models.TextField(blank=True)
    changed_by_user = models.ForeignKey(
        "identity.User",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="loan_status_changes",
    )
    changed_at = models.DateTimeField(default=timezone.now)
    loan_application_id_snapshot = models.UUIDField()
    member_id_snapshot = models.UUIDField()
    sanction_decision_id_snapshot = models.UUIDField()
    sap_customer_code_id_snapshot = models.UUIDField(null=True, blank=True)
    loan_terms_id_snapshot = models.UUIDField()
    replay_flag = models.BooleanField(default=False)
    outcome = models.CharField(max_length=40, default="created")

    objects = AppendOnlyLoanStatusHistoryQuerySet.as_manager()

    class Meta:
        db_table = "loan_status_histories"
        ordering = ["changed_at", "loan_status_history_id"]
        indexes = [
            models.Index(fields=["loan_account", "changed_at"], name="idx_loan_status_time")
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError(
                {"loan_status_history": "Loan status history is append-only."}
            )
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError({"loan_status_history": "Loan status history is append-only."})


class RepaymentSchedule(models.Model):
    repayment_schedule_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    loan_account = models.ForeignKey(
        LoanAccount, on_delete=models.PROTECT, related_name="repayment_schedule_lines"
    )
    installment_number = models.PositiveIntegerField()
    due_date = models.DateField(db_index=True)
    principal_due = models.DecimalField(max_digits=18, decimal_places=2)
    interest_due = models.DecimalField(max_digits=18, decimal_places=2)
    charges_due = models.DecimalField(max_digits=18, decimal_places=2)
    total_due = models.DecimalField(max_digits=18, decimal_places=2)
    paid_principal = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    paid_interest = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    paid_charges = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    schedule_status = models.CharField(max_length=60, db_index=True)
    extended_due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "repayment_schedules"
        ordering = ["installment_number", "repayment_schedule_id"]
        indexes = [
            models.Index(
                fields=["loan_account", "due_date"], name="idx_schedule_account_due"
            )
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["loan_account", "installment_number"],
                name="uniq_schedule_installment",
            ),
            models.CheckConstraint(
                check=models.Q(installment_number__gt=0),
                name="schedule_installment_positive",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(principal_due__gte=0)
                    & models.Q(interest_due__gte=0)
                    & models.Q(charges_due__gte=0)
                    & models.Q(total_due__gte=0)
                    & models.Q(paid_principal__gte=0)
                    & models.Q(paid_interest__gte=0)
                    & models.Q(paid_charges__gte=0)
                ),
                name="schedule_amounts_nonnegative",
            ),
            models.CheckConstraint(
                check=models.Q(
                    total_due=(
                        models.F("principal_due")
                        + models.F("interest_due")
                        + models.F("charges_due")
                    )
                ),
                name="schedule_total_matches_parts",
            ),
            models.CheckConstraint(
                check=models.Q(
                    schedule_status__in=(
                        "pending",
                        "paid",
                        "overdue",
                    )
                ),
                name="schedule_status_bounded",
            ),
        ]


class Repayment(models.Model):
    repayment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan_account = models.ForeignKey(
        LoanAccount, on_delete=models.PROTECT, related_name="repayments"
    )
    member = models.ForeignKey(
        "members.Member", on_delete=models.PROTECT, related_name="repayments"
    )
    repayment_source = models.CharField(max_length=60, default="direct_farmer", db_index=True)
    amount_received = models.DecimalField(max_digits=18, decimal_places=2)
    received_date = models.DateField(db_index=True)
    payment_method = models.CharField(max_length=60)
    bank_reference_number = models.CharField(max_length=120)
    bank_reference_number_normalized = models.CharField(max_length=120, unique=True)
    bank_statement_line_id = models.UUIDField(null=True, blank=True)
    remarks = models.CharField(max_length=2000)
    allocation_status = models.CharField(max_length=60, default="pending", db_index=True)
    sap_posting_status = models.CharField(max_length=60, default="pending", db_index=True)
    captured_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="captured_repayments"
    )
    idempotency_key_digest = models.CharField(max_length=64, unique=True)
    payload_digest = models.CharField(max_length=64)
    capture_audit = models.OneToOneField(
        "identity.AuditLog", on_delete=models.PROTECT, related_name="captured_repayment"
    )
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = "repayments"
        indexes = [
            models.Index(
                fields=["loan_account", "received_date"], name="idx_repay_account_date"
            ),
            models.Index(
                fields=["member", "received_date"], name="idx_repay_member_date"
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount_received__gt=0), name="repayment_amount_positive"
            ),
            models.CheckConstraint(
                check=models.Q(
                    repayment_source__in=("direct_farmer", "subsidiary_deduction")
                ),
                name="repayment_source_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(
                    payment_method__in=("rtgs", "neft", "subsidiary_transfer")
                ),
                name="repayment_method_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(allocation_status="pending"),
                name="repayment_allocation_pending",
            ),
            models.CheckConstraint(
                check=models.Q(sap_posting_status__in=("pending", "posted")),
                name="repayment_sap_status_bounded",
            ),
            models.CheckConstraint(
                check=~models.Q(bank_reference_number="")
                & ~models.Q(bank_reference_number_normalized="")
                & ~models.Q(remarks=""),
                name="repayment_required_text",
            ),
        ]


class RepaymentSapPostingObligation(models.Model):
    obligation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    repayment = models.OneToOneField(
        Repayment, on_delete=models.PROTECT, related_name="sap_posting_obligation"
    )
    due_date = models.DateField(db_index=True)
    status = models.CharField(max_length=60, default="pending", db_index=True)
    task = models.OneToOneField(
        "communications.Notification",
        on_delete=models.PROTECT,
        related_name="repayment_sap_posting_obligation",
    )
    sap_entry_reference = models.CharField(max_length=120, null=True, blank=True)
    posted_by_user = models.ForeignKey(
        "identity.User",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="posted_repayment_sap_obligations",
    )
    posted_at = models.DateTimeField(null=True, blank=True)
    posting_audit = models.OneToOneField(
        "identity.AuditLog",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="posted_repayment_sap_obligation",
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "repayment_sap_posting_obligations"
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(
                        status="pending",
                        sap_entry_reference__isnull=True,
                        posted_by_user__isnull=True,
                        posted_at__isnull=True,
                        posting_audit__isnull=True,
                    )
                    | models.Q(
                        status="posted",
                        sap_entry_reference__isnull=False,
                        posted_by_user__isnull=False,
                        posted_at__isnull=False,
                        posting_audit__isnull=False,
                    )
                ),
                name="repayment_sap_evidence_complete",
            ),
            models.CheckConstraint(
                check=models.Q(sap_entry_reference__isnull=True)
                | ~models.Q(sap_entry_reference=""),
                name="repayment_sap_reference_present",
            ),
        ]
