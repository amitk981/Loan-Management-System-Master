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
