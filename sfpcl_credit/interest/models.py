import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class InterestInvoiceConfiguration(models.Model):
    STATUS_ACTIVE = "active"
    METHOD_SIMPLE_DAILY = "simple_daily"

    interest_invoice_configuration_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    version_number = models.CharField(max_length=40, unique=True)
    effective_from = models.DateField(db_index=True)
    effective_to = models.DateField(db_index=True)
    calculation_method = models.CharField(max_length=40)
    day_count_basis = models.PositiveSmallIntegerField()
    tax_rate = models.DecimalField(max_digits=8, decimal_places=4)
    fixed_fee_amount = models.DecimalField(max_digits=18, decimal_places=2)
    owner_role_codes = models.JSONField(default=list)
    communication_template = models.ForeignKey(
        "communications.ContentTemplate",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="interest_invoice_configurations",
    )
    status = models.CharField(max_length=40, db_index=True)
    approved_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="approved_interest_invoice_configurations",
    )
    approved_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "interest_invoice_configurations"
        ordering = ["-effective_from", "-interest_invoice_configuration_id"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(effective_to__gte=models.F("effective_from")),
                name="interest_invoice_config_period_order",
            ),
            models.CheckConstraint(
                check=models.Q(calculation_method="simple_daily"),
                name="interest_invoice_config_method",
            ),
            models.CheckConstraint(
                check=models.Q(day_count_basis__gt=0),
                name="interest_invoice_day_basis_positive",
            ),
            models.CheckConstraint(
                check=models.Q(tax_rate__gte=0) & models.Q(fixed_fee_amount__gte=0),
                name="interest_invoice_config_amounts_nonnegative",
            ),
            models.CheckConstraint(
                check=models.Q(status="active"),
                name="interest_invoice_config_active",
            ),
        ]


class ImmutableInterestInvoiceQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError({"interest_invoice": "Interest invoice snapshots cannot be bulk-updated."})

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValidationError({"interest_invoice": "Interest invoice snapshots cannot be bulk-updated."})

    def delete(self):
        raise ValidationError({"interest_invoice": "Interest invoice history is immutable."})


class InterestInvoice(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_ISSUED = "issued"
    STATUSES = {STATUS_DRAFT, STATUS_ISSUED}

    interest_invoice_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    loan_account = models.ForeignKey(
        "loans.LoanAccount", on_delete=models.PROTECT, related_name="interest_invoices"
    )
    member = models.ForeignKey(
        "members.Member", on_delete=models.PROTECT, related_name="interest_invoices"
    )
    loan_account_number = models.CharField(max_length=80)
    member_number = models.CharField(max_length=80, blank=True, default="")
    member_display_name = models.CharField(max_length=255)
    financial_year = models.CharField(max_length=20, db_index=True)
    invoice_number = models.CharField(max_length=80, unique=True)
    invoice_date = models.DateField(db_index=True)
    interest_period_start = models.DateField()
    interest_period_end = models.DateField()
    principal_base_amount = models.DecimalField(max_digits=18, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=8, decimal_places=4)
    rate_config = models.ForeignKey(
        "configurations.InterestRateConfig",
        on_delete=models.PROTECT,
        related_name="interest_invoices",
    )
    rate_version_number = models.CharField(max_length=40)
    calculation_configuration = models.ForeignKey(
        InterestInvoiceConfiguration,
        on_delete=models.PROTECT,
        related_name="interest_invoices",
    )
    calculation_version = models.CharField(max_length=40)
    calculation_method = models.CharField(max_length=40)
    day_count_basis = models.PositiveSmallIntegerField()
    calculation_days = models.PositiveSmallIntegerField()
    gross_interest_amount = models.DecimalField(max_digits=18, decimal_places=2)
    interest_paid_amount = models.DecimalField(max_digits=18, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=8, decimal_places=4)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2)
    fixed_fee_amount = models.DecimalField(max_digits=18, decimal_places=2)
    interest_amount = models.DecimalField(max_digits=18, decimal_places=2)
    invoice_status = models.CharField(max_length=60, default=STATUS_DRAFT, db_index=True)
    generated_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="generated_interest_invoices"
    )
    generated_at = models.DateTimeField(default=timezone.now)
    generation_idempotency_key_digest = models.CharField(max_length=64, unique=True)
    generation_payload_digest = models.CharField(max_length=64)
    generation_audit = models.OneToOneField(
        "identity.AuditLog", on_delete=models.PROTECT, related_name="generated_interest_invoice"
    )
    document = models.OneToOneField(
        "documents.DocumentFile",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="interest_invoice",
    )
    communication = models.OneToOneField(
        "communications.Communication",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="interest_invoice",
    )
    issued_by_user = models.ForeignKey(
        "identity.User",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="issued_interest_invoices",
    )
    issued_at = models.DateTimeField(null=True, blank=True)
    issuance_idempotency_key_digest = models.CharField(
        max_length=64, null=True, blank=True, unique=True
    )
    issuance_payload_digest = models.CharField(max_length=64, blank=True, default="")
    issuance_audit = models.OneToOneField(
        "identity.AuditLog",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="issued_interest_invoice",
    )

    objects = ImmutableInterestInvoiceQuerySet.as_manager()

    class Meta:
        db_table = "interest_invoices"
        ordering = ["-invoice_date", "-interest_invoice_id"]
        indexes = [
            models.Index(fields=["loan_account", "invoice_status"], name="idx_interest_inv_loan_status"),
            models.Index(fields=["financial_year", "invoice_status"], name="idx_interest_inv_fy_status"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["loan_account", "interest_period_start", "interest_period_end"],
                name="uniq_interest_invoice_loan_period",
            ),
            models.CheckConstraint(
                check=models.Q(invoice_status__in=("draft", "issued")),
                name="interest_invoice_status_valid",
            ),
            models.CheckConstraint(
                check=models.Q(interest_period_end__gte=models.F("interest_period_start")),
                name="interest_invoice_period_order",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(principal_base_amount__gte=0)
                    & models.Q(interest_rate__gte=0)
                    & models.Q(gross_interest_amount__gte=0)
                    & models.Q(interest_paid_amount__gte=0)
                    & models.Q(tax_rate__gte=0)
                    & models.Q(tax_amount__gte=0)
                    & models.Q(fixed_fee_amount__gte=0)
                    & models.Q(interest_amount__gte=0)
                ),
                name="interest_invoice_amounts_nonnegative",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(
                        invoice_status="draft",
                        document__isnull=True,
                        communication__isnull=True,
                        issued_by_user__isnull=True,
                        issued_at__isnull=True,
                        issuance_idempotency_key_digest__isnull=True,
                        issuance_payload_digest="",
                        issuance_audit__isnull=True,
                    )
                    | models.Q(
                        invoice_status="issued",
                        document__isnull=False,
                        communication__isnull=False,
                        issued_by_user__isnull=False,
                        issued_at__isnull=False,
                        issuance_idempotency_key_digest__isnull=False,
                        issuance_audit__isnull=False,
                    )
                ),
                name="interest_invoice_issue_evidence_complete",
            ),
        ]

    _FROZEN_FIELDS = (
        "loan_account_id", "member_id", "loan_account_number", "member_number",
        "member_display_name", "financial_year", "invoice_number", "invoice_date",
        "interest_period_start", "interest_period_end", "principal_base_amount",
        "interest_rate", "rate_config_id", "rate_version_number",
        "calculation_configuration_id", "calculation_version", "calculation_method",
        "day_count_basis", "calculation_days", "gross_interest_amount",
        "interest_paid_amount", "tax_rate", "tax_amount", "fixed_fee_amount",
        "interest_amount", "generated_by_user_id", "generated_at",
        "generation_idempotency_key_digest", "generation_payload_digest",
        "generation_audit_id",
    )

    def save(self, *args, **kwargs):
        if not self._state.adding:
            retained = type(self)._base_manager.get(pk=self.pk)
            if any(getattr(retained, field) != getattr(self, field) for field in self._FROZEN_FIELDS):
                raise ValidationError({"interest_invoice": "Calculation snapshots are immutable."})
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError({"interest_invoice": "Interest invoice history is immutable."})


class ImmutableAccrualQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError({"accrual_entry": "Accrual snapshots cannot be bulk-updated."})

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValidationError({"accrual_entry": "Accrual snapshots cannot be bulk-updated."})

    def delete(self):
        raise ValidationError({"accrual_entry": "Accrual history is immutable."})


class AccrualEntry(models.Model):
    STATUS_PENDING = "pending"
    STATUS_POSTED = "posted"
    STATUS_FAILED = "failed"
    STATUSES = {STATUS_PENDING, STATUS_POSTED, STATUS_FAILED}

    accrual_entry_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan_account = models.ForeignKey(
        "loans.LoanAccount", on_delete=models.PROTECT, related_name="accrual_entries"
    )
    accrual_month = models.CharField(max_length=7, db_index=True)
    interest_period_start = models.DateField()
    interest_period_end = models.DateField()
    principal_base_amount = models.DecimalField(max_digits=18, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=8, decimal_places=4)
    rate_config = models.ForeignKey(
        "configurations.InterestRateConfig",
        on_delete=models.PROTECT,
        related_name="accrual_entries",
    )
    rate_version_number = models.CharField(max_length=40)
    calculation_configuration = models.ForeignKey(
        InterestInvoiceConfiguration,
        on_delete=models.PROTECT,
        related_name="accrual_entries",
    )
    calculation_version = models.CharField(max_length=40)
    calculation_method = models.CharField(max_length=40)
    day_count_basis = models.PositiveSmallIntegerField()
    calculation_days = models.PositiveSmallIntegerField()
    interest_accrued_amount = models.DecimalField(max_digits=18, decimal_places=2)
    posted_status = models.CharField(max_length=60, default=STATUS_PENDING, db_index=True)
    sap_entry_reference = models.CharField(max_length=120, blank=True, default="", db_index=True)
    posted_by_user = models.ForeignKey(
        "identity.User",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="posted_interest_accruals",
    )
    posted_at = models.DateTimeField(null=True, blank=True)
    generated_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="generated_interest_accruals"
    )
    generated_at = models.DateTimeField(default=timezone.now)
    generation_idempotency_key_digest = models.CharField(max_length=64, unique=True)
    generation_payload_digest = models.CharField(max_length=64)
    generation_audit = models.OneToOneField(
        "identity.AuditLog", on_delete=models.PROTECT, related_name="generated_interest_accrual"
    )
    posting_idempotency_key_digest = models.CharField(
        max_length=64, null=True, blank=True, unique=True
    )
    posting_payload_digest = models.CharField(max_length=64, blank=True, default="")
    posting_audit = models.OneToOneField(
        "identity.AuditLog",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="posted_interest_accrual",
    )

    objects = ImmutableAccrualQuerySet.as_manager()

    class Meta:
        db_table = "accrual_entries"
        ordering = ["-accrual_month", "-accrual_entry_id"]
        indexes = [
            models.Index(fields=["loan_account", "posted_status"], name="idx_accrual_loan_status"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["loan_account", "accrual_month"], name="uniq_accrual_loan_month"
            ),
            models.CheckConstraint(
                check=models.Q(posted_status__in=("pending", "posted", "failed")),
                name="accrual_posted_status_valid",
            ),
            models.CheckConstraint(
                check=models.Q(interest_period_end__gte=models.F("interest_period_start")),
                name="accrual_period_order",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(principal_base_amount__gt=0)
                    & models.Q(interest_rate__gte=0)
                    & models.Q(interest_accrued_amount__gte=0)
                    & models.Q(day_count_basis__gt=0)
                    & models.Q(calculation_days__gt=0)
                ),
                name="accrual_calculation_values_valid",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(
                        posted_status="pending",
                        sap_entry_reference="",
                        posted_by_user__isnull=True,
                        posted_at__isnull=True,
                        posting_idempotency_key_digest__isnull=True,
                        posting_payload_digest="",
                        posting_audit__isnull=True,
                    )
                    | (
                        models.Q(posted_status="posted")
                        & ~models.Q(sap_entry_reference="")
                        & models.Q(
                            posted_by_user__isnull=False,
                            posted_at__isnull=False,
                            posting_idempotency_key_digest__isnull=False,
                            posting_audit__isnull=False,
                        )
                    )
                    | models.Q(
                        posted_status="failed",
                        sap_entry_reference="",
                        posted_by_user__isnull=False,
                        posted_at__isnull=False,
                        posting_idempotency_key_digest__isnull=False,
                        posting_audit__isnull=False,
                    )
                ),
                name="accrual_posting_evidence_coherent",
            ),
        ]

    _FROZEN_FIELDS = (
        "loan_account_id", "accrual_month", "interest_period_start", "interest_period_end",
        "principal_base_amount", "interest_rate", "rate_config_id", "rate_version_number",
        "calculation_configuration_id", "calculation_version", "calculation_method",
        "day_count_basis", "calculation_days", "interest_accrued_amount",
        "generated_by_user_id", "generated_at", "generation_idempotency_key_digest",
        "generation_payload_digest", "generation_audit_id",
    )

    def save(self, *args, **kwargs):
        if not self._state.adding:
            retained = type(self)._base_manager.get(pk=self.pk)
            if any(getattr(retained, field) != getattr(self, field) for field in self._FROZEN_FIELDS):
                raise ValidationError({"accrual_entry": "Calculation snapshots are immutable."})
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError({"accrual_entry": "Accrual history is immutable."})


class AccrualSapPostingObligation(models.Model):
    accrual_sap_posting_obligation_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    accrual_entry = models.OneToOneField(
        AccrualEntry, on_delete=models.PROTECT, related_name="sap_posting_obligation"
    )
    status = models.CharField(max_length=60, default=AccrualEntry.STATUS_PENDING, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "accrual_sap_posting_obligations"
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(status="pending", resolved_at__isnull=True)
                    | models.Q(status__in=("posted", "failed"), resolved_at__isnull=False)
                ),
                name="accrual_sap_obligation_status_valid",
            ),
        ]
