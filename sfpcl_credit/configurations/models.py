import uuid

from django.db import models
from django.utils import timezone


class LoanPolicyConfig(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_ACTIVE = "active"
    STATUS_RETIRED = "retired"
    STATUSES = {STATUS_DRAFT, STATUS_ACTIVE, STATUS_RETIRED}

    loan_policy_config_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    policy_name = models.CharField(max_length=255)
    policy_version = models.CharField(max_length=40)
    effective_from = models.DateField(db_index=True)
    effective_to = models.DateField(blank=True, null=True, db_index=True)
    short_term_duration_months = models.IntegerField()
    min_secured_loan_months = models.IntegerField(blank=True, null=True)
    max_secured_loan_years = models.IntegerField(blank=True, null=True)
    approval_threshold_amount = models.DecimalField(max_digits=18, decimal_places=2)
    default_scale_of_finance_per_acre_amount = models.DecimalField(
        max_digits=18, decimal_places=2
    )
    share_limit_percentage = models.DecimalField(
        max_digits=8, decimal_places=4, blank=True, null=True
    )
    per_share_cap_amount = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    interest_rate_type = models.CharField(max_length=60)
    interest_benchmark = models.CharField(max_length=120, blank=True, null=True)
    penal_interest_rate = models.DecimalField(
        max_digits=8, decimal_places=4, blank=True, null=True
    )
    rekyc_frequency_months = models.IntegerField()
    record_retention_years = models.IntegerField()
    grace_period_months = models.IntegerField()
    non_intentional_extension_months = models.IntegerField()
    board_approval_reference = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=60, default=STATUS_DRAFT, db_index=True)

    class Meta:
        db_table = "loan_policy_configs"
        ordering = ["-effective_from", "-loan_policy_config_id"]


class VersionHistory(models.Model):
    version_history_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    versioned_entity_type = models.CharField(max_length=80, db_index=True)
    versioned_entity_id = models.UUIDField(db_index=True)
    version_number = models.CharField(max_length=40)
    change_summary = models.TextField()
    author_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="authored_version_histories",
    )
    reviewer_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="reviewed_version_histories",
    )
    approver_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="approved_version_histories",
    )
    board_approval_reference = models.CharField(max_length=255, blank=True, null=True)
    approval_reference = models.CharField(max_length=255, blank=True, default="")
    approved_at = models.DateTimeField(blank=True, null=True)
    old_value_json = models.JSONField(blank=True, null=True)
    new_value_json = models.JSONField(blank=True, null=True)
    effective_from = models.DateField()
    effective_to = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "version_histories"
        ordering = ["-created_at", "-version_history_id"]


class InterestRateConfig(models.Model):
    STATUS_PROPOSED = "proposed"
    STATUS_ACTIVE = "active"

    interest_rate_config_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    version_number = models.CharField(max_length=40, unique=True)
    rate_type = models.CharField(max_length=60, default="floating")
    effective_rate = models.DecimalField(max_digits=8, decimal_places=4)
    effective_from = models.DateField(db_index=True)
    effective_to = models.DateField(blank=True, null=True, db_index=True)
    benchmark_name = models.CharField(max_length=120, blank=True, null=True)
    spread_rate = models.DecimalField(
        max_digits=8, decimal_places=4, blank=True, null=True
    )
    reset_frequency = models.CharField(max_length=60, blank=True, null=True)
    communication_required = models.BooleanField(default=True)
    board_approval_reference = models.CharField(max_length=255)
    status = models.CharField(max_length=40, default=STATUS_PROPOSED, db_index=True)
    created_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="created_interest_rate_configs",
    )
    approved_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="approved_interest_rate_configs",
    )
    activated_at = models.DateTimeField(blank=True, null=True)
    activation_idempotency_key = models.CharField(
        max_length=255, blank=True, null=True, unique=True
    )
    activation_payload_digest = models.CharField(max_length=64, blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "interest_rate_configs"
        ordering = ["-effective_from", "-interest_rate_config_id"]
        indexes = [
            models.Index(
                fields=["status", "effective_from", "effective_to"],
                name="idx_rate_status_period",
            )
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(rate_type="floating"),
                name="interest_rate_type_floating",
            ),
            models.CheckConstraint(
                check=models.Q(effective_rate__gte=0),
                name="interest_rate_effective_nonnegative",
            ),
            models.CheckConstraint(
                check=models.Q(spread_rate__isnull=True) | models.Q(spread_rate__gte=0),
                name="interest_rate_spread_nonnegative",
            ),
            models.CheckConstraint(
                check=models.Q(effective_to__isnull=True)
                | models.Q(effective_to__gte=models.F("effective_from")),
                name="interest_rate_period_order",
            ),
            models.CheckConstraint(
                check=models.Q(status__in=("proposed", "active")),
                name="interest_rate_status_valid",
            ),
        ]


class InterestRateHistory(models.Model):
    interest_rate_history_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    loan_account = models.ForeignKey(
        "loans.LoanAccount",
        on_delete=models.PROTECT,
        related_name="interest_rate_histories",
    )
    old_interest_rate = models.DecimalField(
        max_digits=8, decimal_places=4, blank=True, null=True
    )
    new_interest_rate = models.DecimalField(max_digits=8, decimal_places=4)
    effective_from = models.DateField(db_index=True)
    rate_config = models.ForeignKey(
        InterestRateConfig,
        on_delete=models.PROTECT,
        related_name="loan_rate_histories",
    )
    borrower_communication = models.ForeignKey(
        "communications.Communication",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="interest_rate_histories",
    )
    changed_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="changed_interest_rate_histories",
    )
    changed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "interest_rate_histories"
        ordering = ["effective_from", "interest_rate_history_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["loan_account", "rate_config"],
                name="uniq_loan_rate_config_history",
            )
        ]


class BorrowerRateNoticeObligation(models.Model):
    borrower_rate_notice_obligation_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    interest_rate_config = models.ForeignKey(
        InterestRateConfig,
        on_delete=models.PROTECT,
        related_name="borrower_notice_obligations",
    )
    loan_account = models.ForeignKey(
        "loans.LoanAccount",
        on_delete=models.PROTECT,
        related_name="rate_notice_obligations",
    )
    email_communication = models.OneToOneField(
        "communications.Communication",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="email_rate_notice_obligation",
    )
    sms_communication = models.OneToOneField(
        "communications.Communication",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="sms_rate_notice_obligation",
    )
    email_failure_code = models.CharField(max_length=80, blank=True, default="")
    sms_failure_code = models.CharField(max_length=80, blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "borrower_rate_notice_obligations"
        ordering = ["interest_rate_config_id", "loan_account_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["interest_rate_config", "loan_account"],
                name="uniq_rate_notice_loan",
            ),
        ]

    @property
    def delivery_status(self):
        statuses = {self.email_delivery_status, self.sms_delivery_status}
        if "failed" in statuses:
            return "failed"
        if statuses == {"sent"}:
            return "sent"
        return "pending"

    @property
    def email_delivery_status(self):
        return self._channel_delivery_status("email")

    @property
    def sms_delivery_status(self):
        return self._channel_delivery_status("sms")

    def _channel_delivery_status(self, channel):
        failure_code = getattr(self, f"{channel}_failure_code")
        communication = getattr(self, f"{channel}_communication")
        communication_id = getattr(self, f"{channel}_communication_id")
        if failure_code or communication_id is None:
            return "failed"
        if communication.delivery_status == "sent":
            return "sent"
        from sfpcl_credit.communications.models import CommunicationDeliveryJob

        job_status = CommunicationDeliveryJob.objects.filter(
            communication_id=communication_id
        ).values_list("status", flat=True).first()
        return "failed" if job_status == CommunicationDeliveryJob.STATUS_FAILED else "pending"


class ImmutableInterestRateConsumptionQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError({"interest_rate_consumption": "Consumed rate snapshots are immutable."})

    def delete(self):
        raise ValidationError({"interest_rate_consumption": "Consumed rate snapshots are immutable."})


class InterestRateConsumptionSnapshot(models.Model):
    interest_rate_consumption_snapshot_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    consumer_kind = models.CharField(max_length=60)
    consumer_reference_id = models.UUIDField()
    loan_account = models.ForeignKey(
        "loans.LoanAccount",
        on_delete=models.PROTECT,
        related_name="interest_rate_consumption_snapshots",
    )
    calculation_date = models.DateField()
    rate_config = models.ForeignKey(
        InterestRateConfig,
        on_delete=models.PROTECT,
        related_name="consumption_snapshots",
    )
    version_number = models.CharField(max_length=40)
    effective_rate = models.DecimalField(max_digits=8, decimal_places=4)
    created_at = models.DateTimeField(default=timezone.now)

    objects = ImmutableInterestRateConsumptionQuerySet.as_manager()

    class Meta:
        db_table = "interest_rate_consumption_snapshots"
        constraints = [
            models.UniqueConstraint(
                fields=["consumer_kind", "consumer_reference_id"],
                name="uniq_interest_rate_consumer",
            )
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError(
                {"interest_rate_consumption": "Consumed rate snapshots are immutable."}
            )
        return super().save(*args, **kwargs)


class SourceBankAccountGovernance(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"

    source_bank_account_governance_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    bank_account = models.ForeignKey(
        "members.BankAccount",
        on_delete=models.PROTECT,
        related_name="source_bank_governance_records",
    )
    status = models.CharField(max_length=40, default=STATUS_ACTIVE, db_index=True)
    source_facts_digest = models.CharField(max_length=64)
    reason_digest = models.CharField(max_length=64)
    reason = models.TextField(max_length=500, null=True, blank=True)
    change_context_json = models.JSONField(null=True, blank=True)
    change_context_digest = models.CharField(max_length=64, blank=True, default="")
    request_id = models.CharField(max_length=255, unique=True)
    activated_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="activated_source_bank_accounts",
    )
    activated_at = models.DateTimeField(default=timezone.now, db_index=True)
    predecessor = models.OneToOneField(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="successor",
    )
    version_history = models.OneToOneField(
        VersionHistory,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="source_bank_governance",
    )
    deactivated_at = models.DateTimeField(null=True, blank=True, db_index=True)
    deactivation_version_history = models.OneToOneField(
        VersionHistory,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="source_bank_governance_deactivation",
    )
    deactivation_audit = models.OneToOneField(
        "identity.AuditLog",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="source_bank_governance_deactivation",
    )
    activation_audit = models.OneToOneField(
        "identity.AuditLog",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="source_bank_governance",
    )

    class Meta:
        db_table = "source_bank_account_governance"
        constraints = [
            models.CheckConstraint(
                check=models.Q(status__in=("active", "inactive")),
                name="source_bank_governance_status_valid",
            ),
            models.UniqueConstraint(
                fields=["status"],
                condition=models.Q(status="active"),
                name="uniq_active_source_bank_governance",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(
                        status="active",
                        version_history__isnull=False,
                        activation_audit__isnull=False,
                        deactivated_at__isnull=True,
                        deactivation_version_history__isnull=True,
                        deactivation_audit__isnull=True,
                    )
                    | models.Q(
                        status="inactive",
                        version_history__isnull=False,
                        activation_audit__isnull=False,
                        deactivated_at__isnull=False,
                        deactivation_version_history__isnull=False,
                        deactivation_audit__isnull=False,
                    )
                ),
                name="source_bank_governance_complete_evidence",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(deactivated_at__isnull=True)
                    | models.Q(deactivated_at__gte=models.F("activated_at"))
                ),
                name="source_bank_governance_time_order",
            ),
        ]
