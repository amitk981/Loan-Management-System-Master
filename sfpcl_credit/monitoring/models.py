import uuid

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class DpdOperationalBucketScheme(models.Model):
    dpd_operational_bucket_scheme_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    version = models.CharField(max_length=40, unique=True)
    effective_from = models.DateField(db_index=True)
    effective_to = models.DateField(null=True, blank=True, db_index=True)
    first_upper_days = models.PositiveIntegerField(default=30)
    second_upper_days = models.PositiveIntegerField(default=60)
    third_upper_days = models.PositiveIntegerField(default=90)
    status = models.CharField(max_length=20, default="active", db_index=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "dpd_operational_bucket_schemes"
        indexes = [
            models.Index(
                fields=["status", "effective_from", "effective_to"],
                name="idx_dpd_scheme_effective",
            )
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(effective_to__isnull=True)
                | models.Q(effective_to__gte=models.F("effective_from")),
                name="dpd_scheme_period_order",
            ),
            models.CheckConstraint(
                check=models.Q(
                    first_upper_days=30,
                    second_upper_days=60,
                    third_upper_days=90,
                ),
                name="dpd_scheme_bounds_order",
            ),
            models.CheckConstraint(
                check=models.Q(status__in=("active", "retired")),
                name="dpd_scheme_status_bounded",
            ),
        ]


class AppendOnlyDpdStatusQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError({"dpd_status": "DPD snapshots are append-only."})

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValidationError({"dpd_status": "DPD snapshots are append-only."})

    def delete(self):
        raise ValidationError({"dpd_status": "DPD snapshots are append-only."})


class DpdStatus(models.Model):
    dpd_status_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan_account = models.ForeignKey(
        "loans.LoanAccount", on_delete=models.PROTECT, related_name="dpd_statuses"
    )
    as_of_date = models.DateField(db_index=True)
    days_past_due = models.PositiveIntegerField()
    sop_bucket = models.CharField(max_length=40, db_index=True)
    standard_bucket = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    principal_overdue_amount = models.DecimalField(max_digits=18, decimal_places=2)
    interest_overdue_amount = models.DecimalField(max_digits=18, decimal_places=2)
    total_overdue_amount = models.DecimalField(max_digits=18, decimal_places=2)
    earliest_unpaid_due_date = models.DateField(null=True, blank=True)
    calculation_version = models.CharField(max_length=40, default="DPD-CALC-1")
    operational_scheme = models.ForeignKey(
        DpdOperationalBucketScheme,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="dpd_statuses",
    )
    calculation_inputs_json = models.JSONField(default=dict)
    calculated_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="calculated_dpd_statuses"
    )
    calculation_audit = models.OneToOneField(
        "identity.AuditLog", on_delete=models.PROTECT, related_name="dpd_status"
    )
    created_at = models.DateTimeField(default=timezone.now)

    objects = AppendOnlyDpdStatusQuerySet.as_manager()

    class Meta:
        db_table = "dpd_statuses"
        ordering = ["-as_of_date", "-created_at", "-dpd_status_id"]
        indexes = [
            models.Index(
                fields=["loan_account", "as_of_date"], name="idx_dpd_account_asof"
            )
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["loan_account", "as_of_date"], name="uniq_dpd_account_asof"
            ),
            models.CheckConstraint(
                check=models.Q(principal_overdue_amount__gte=0)
                & models.Q(interest_overdue_amount__gte=0)
                & models.Q(total_overdue_amount__gte=0),
                name="dpd_amounts_nonnegative",
            ),
            models.CheckConstraint(
                check=models.Q(
                    total_overdue_amount=models.F("principal_overdue_amount")
                    + models.F("interest_overdue_amount")
                ),
                name="dpd_total_matches_parts",
            ),
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError({"dpd_status": "DPD snapshots are append-only."})
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError({"dpd_status": "DPD snapshots are append-only."})


class Reminder(models.Model):
    CHANNEL_SMS = "sms"
    CHANNEL_EMAIL = "email"
    CHANNEL_PHONE = "phone"
    CHANNELS = {CHANNEL_SMS, CHANNEL_EMAIL, CHANNEL_PHONE}
    TYPE_OUTSTANDING_BEYOND_ONE_YEAR = "outstanding_beyond_one_year"
    ORIGIN_AUTOMATIC = "automatic"
    ORIGIN_MANUAL = "manual"
    STATUS_QUEUED = "queued"
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CALL_LOGGED = "call_logged"

    reminder_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan_account = models.ForeignKey(
        "loans.LoanAccount", on_delete=models.PROTECT, related_name="reminders"
    )
    loan_application = models.ForeignKey(
        "applications.LoanApplication", on_delete=models.PROTECT, related_name="reminders"
    )
    member = models.ForeignKey(
        "members.Member", on_delete=models.PROTECT, related_name="reminders"
    )
    dpd_status = models.ForeignKey(
        DpdStatus, on_delete=models.PROTECT, related_name="reminders"
    )
    quarter_end_date = models.DateField(db_index=True)
    eligibility_decision_json = models.JSONField(default=dict)
    reminder_type = models.CharField(max_length=80, db_index=True)
    origin = models.CharField(max_length=20, db_index=True)
    channel = models.CharField(max_length=60, db_index=True)
    content_template = models.ForeignKey(
        "communications.ContentTemplate",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_reminders",
    )
    message_body = models.TextField(blank=True)
    communication = models.OneToOneField(
        "communications.Communication",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="monitoring_reminder",
    )
    delivery_status = models.CharField(max_length=60, db_index=True)
    status_reason = models.CharField(max_length=120, blank=True)
    contacted_person = models.CharField(max_length=80, blank=True)
    call_outcome = models.TextField(blank=True)
    next_follow_up_date = models.DateField(null=True, blank=True, db_index=True)
    created_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="created_reminders"
    )
    sent_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "reminders"
        ordering = ["-quarter_end_date", "loan_account_id", "channel"]
        indexes = [
            models.Index(
                fields=["quarter_end_date", "delivery_status"],
                name="idx_reminder_quarter_status",
            ),
            models.Index(fields=["member", "created_at"], name="idx_reminder_member_date"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["loan_account", "quarter_end_date", "reminder_type", "channel"],
                condition=models.Q(origin="automatic"),
                name="uniq_reminder_loan_quarter_reason_channel",
            ),
            models.CheckConstraint(
                check=models.Q(origin__in=("automatic", "manual")),
                name="reminder_origin_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(channel__in=("sms", "email", "phone")),
                name="reminder_channel_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(
                    delivery_status__in=(
                        "queued",
                        "sent",
                        "failed",
                        "cancelled",
                        "call_logged",
                    )
                ),
                name="reminder_status_bounded",
            ),
            models.CheckConstraint(
                check=(
                    ~models.Q(message_body="")
                    & (
                        models.Q(
                            channel="phone",
                            content_template__isnull=True,
                            communication__isnull=True,
                            delivery_status="call_logged",
                            sent_at__isnull=False,
                        )
                        & ~models.Q(call_outcome="")
                        & ~models.Q(contacted_person="")
                        | models.Q(
                            channel__in=("sms", "email"),
                            content_template__isnull=False,
                            communication__isnull=False,
                            delivery_status__in=("queued", "sent", "failed", "cancelled"),
                        )
                    )
                ),
                name="reminder_channel_evidence_complete",
            ),
        ]


class ImmutablePortfolioSnapshotQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError({"portfolio_snapshot": "Portfolio snapshots are immutable."})

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValidationError({"portfolio_snapshot": "Portfolio snapshots are immutable."})

    def delete(self):
        raise ValidationError({"portfolio_snapshot": "Portfolio snapshots are immutable."})


class PortfolioSnapshot(models.Model):
    loan_portfolio_snapshot_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    as_of_date = models.DateField(db_index=True)
    period_start_date = models.DateField()
    total_active_loans_count = models.PositiveIntegerField()
    total_sanctioned_amount = models.DecimalField(max_digits=18, decimal_places=2)
    total_disbursed_amount = models.DecimalField(max_digits=18, decimal_places=2)
    principal_outstanding_amount = models.DecimalField(max_digits=18, decimal_places=2)
    interest_outstanding_amount = models.DecimalField(max_digits=18, decimal_places=2)
    total_overdue_amount = models.DecimalField(max_digits=18, decimal_places=2)
    dpd_bucket_summary_json = models.JSONField(default=dict)
    default_cases_count = models.PositiveIntegerField(null=True, blank=True)
    extensions_count = models.PositiveIntegerField(null=True, blank=True)
    recovery_cases_count = models.PositiveIntegerField(null=True, blank=True)
    closed_loans_count = models.PositiveIntegerField(null=True, blank=True)
    totals_json = models.JSONField(default=dict)
    availability_json = models.JSONField(default=dict)
    rows_json = models.JSONField(default=list)
    source_manifest_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)

    objects = ImmutablePortfolioSnapshotQuerySet.as_manager()

    class Meta:
        db_table = "loan_portfolio_snapshots"
        indexes = [models.Index(fields=["as_of_date", "created_at"], name="idx_portfolio_asof_created")]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError({"portfolio_snapshot": "Portfolio snapshots are immutable."})
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError({"portfolio_snapshot": "Portfolio snapshots are immutable."})


class RetainedQuarterlyMisQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError({"quarterly_mis_report": "Quarterly MIS writes use governed transitions."})

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValidationError({"quarterly_mis_report": "Quarterly MIS writes use governed transitions."})

    def delete(self):
        raise ValidationError({"quarterly_mis_report": "Quarterly MIS history is retained."})


class QuarterlyMisReport(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_SUBMITTED = "submitted"
    STATUS_REVIEWED = "reviewed"

    quarterly_mis_report_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    financial_year = models.CharField(max_length=20, db_index=True)
    quarter = models.CharField(max_length=10, db_index=True)
    as_of_date = models.DateField(db_index=True)
    revision = models.PositiveIntegerField(default=1)
    portfolio_snapshot = models.OneToOneField(PortfolioSnapshot, on_delete=models.PROTECT, related_name="quarterly_mis_report")
    status = models.CharField(max_length=20, default=STATUS_DRAFT, db_index=True)
    prepared_by_user = models.ForeignKey("identity.User", on_delete=models.PROTECT, related_name="prepared_quarterly_mis_reports")
    generated_at = models.DateTimeField(default=timezone.now)
    generation_idempotency_key_digest = models.CharField(max_length=64, unique=True)
    generation_payload_digest = models.CharField(max_length=64)
    generation_original_response_json = models.JSONField(default=dict)
    generation_audit = models.OneToOneField("identity.AuditLog", on_delete=models.PROTECT, related_name="generated_quarterly_mis_report")
    submitted_to_user = models.ForeignKey(
        "identity.User", null=True, blank=True, on_delete=models.PROTECT,
        related_name="quarterly_mis_reports_for_review",
    )
    submitted_by_user = models.ForeignKey(
        "identity.User", null=True, blank=True, on_delete=models.PROTECT,
        related_name="submitted_quarterly_mis_reports",
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    submission_audit = models.OneToOneField(
        "identity.AuditLog", null=True, blank=True, on_delete=models.PROTECT,
        related_name="submitted_quarterly_mis_report",
    )
    submission_idempotency_key_digest = models.CharField(max_length=64, null=True, blank=True, unique=True)
    submission_payload_digest = models.CharField(max_length=64, blank=True, default="")
    submission_original_response_json = models.JSONField(default=dict)
    reviewed_by_user = models.ForeignKey(
        "identity.User", null=True, blank=True, on_delete=models.PROTECT,
        related_name="reviewed_quarterly_mis_reports",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_audit = models.OneToOneField(
        "identity.AuditLog", null=True, blank=True, on_delete=models.PROTECT,
        related_name="reviewed_quarterly_mis_report",
    )
    review_idempotency_key_digest = models.CharField(max_length=64, null=True, blank=True, unique=True)
    review_payload_digest = models.CharField(max_length=64, blank=True, default="")
    review_original_response_json = models.JSONField(default=dict)
    report_document = models.OneToOneField("documents.DocumentFile", null=True, blank=True, on_delete=models.PROTECT, related_name="quarterly_mis_pdf_report")
    excel_document = models.OneToOneField("documents.DocumentFile", null=True, blank=True, on_delete=models.PROTECT, related_name="quarterly_mis_excel_report")

    objects = RetainedQuarterlyMisQuerySet.as_manager()

    class Meta:
        db_table = "quarterly_mis_reports"
        ordering = ["-as_of_date", "-revision", "-quarterly_mis_report_id"]
        indexes = [models.Index(fields=["financial_year", "quarter", "status"], name="idx_mis_period_status")]
        constraints = [
            models.UniqueConstraint(fields=["financial_year", "quarter", "as_of_date", "revision"], name="uniq_mis_period_revision"),
            models.CheckConstraint(check=models.Q(status__in=("draft", "submitted", "reviewed")), name="mis_status_bounded"),
            models.CheckConstraint(
                check=(
                    models.Q(
                        status="draft", submitted_to_user__isnull=True,
                        submitted_by_user__isnull=True, submitted_at__isnull=True,
                        submission_audit__isnull=True, reviewed_by_user__isnull=True,
                        reviewed_at__isnull=True, review_audit__isnull=True,
                    )
                    | models.Q(
                        status="submitted", submitted_to_user__isnull=False,
                        submitted_by_user__isnull=False, submitted_at__isnull=False,
                        submission_audit__isnull=False, reviewed_by_user__isnull=True,
                        reviewed_at__isnull=True, review_audit__isnull=True,
                    )
                    | models.Q(
                        status="reviewed", submitted_to_user__isnull=False,
                        submitted_by_user__isnull=False, submitted_at__isnull=False,
                        submission_audit__isnull=False, reviewed_by_user__isnull=False,
                        reviewed_at__isnull=False, review_audit__isnull=False,
                    )
                ),
                name="mis_transition_evidence_coherent",
            ),
        ]

    _FROZEN_FIELDS = (
        "financial_year", "quarter", "as_of_date", "revision", "portfolio_snapshot_id",
        "prepared_by_user_id", "generated_at", "generation_audit_id",
        "generation_idempotency_key_digest", "generation_payload_digest",
    )

    def save(self, *args, **kwargs):
        if not self._state.adding:
            retained = type(self)._base_manager.get(pk=self.pk)
            if any(getattr(retained, field) != getattr(self, field) for field in self._FROZEN_FIELDS):
                raise ValidationError({"quarterly_mis_report": "Generated report evidence is immutable."})
            if retained.generation_original_response_json and retained.generation_original_response_json != self.generation_original_response_json:
                raise ValidationError({"quarterly_mis_report": "Generation replay evidence is immutable."})
            if retained.status == self.STATUS_REVIEWED:
                raise ValidationError({"quarterly_mis_report": "Reviewed report evidence is immutable."})
            if retained.status == self.STATUS_SUBMITTED:
                preserved = (
                    "submitted_to_user_id", "submitted_by_user_id", "submitted_at",
                    "submission_audit_id", "report_document_id", "excel_document_id",
                )
                if self.status != self.STATUS_REVIEWED or any(
                    getattr(retained, field) != getattr(self, field) for field in preserved
                ):
                    raise ValidationError({"quarterly_mis_report": "Submitted report evidence is immutable."})
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError({"quarterly_mis_report": "Quarterly MIS history is retained."})
