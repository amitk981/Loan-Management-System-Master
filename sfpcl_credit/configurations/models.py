import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class RepaymentInstructionVersion(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_RETIRED = "retired"

    repayment_instruction_version_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    version = models.CharField(max_length=40, unique=True)
    beneficiary_name = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)
    account_number_last4 = models.CharField(max_length=4)
    ifsc = models.CharField(max_length=20)
    effective_from = models.DateField(db_index=True)
    effective_to = models.DateField(null=True, blank=True, db_index=True)
    status = models.CharField(max_length=20, default=STATUS_ACTIVE, db_index=True)
    approved_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="approved_repayment_instruction_versions",
    )
    approved_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "repayment_instruction_versions"
        constraints = [
            models.CheckConstraint(
                check=models.Q(status__in=("active", "retired")),
                name="repayment_instruction_status_valid",
            ),
            models.CheckConstraint(
                check=models.Q(effective_to__isnull=True)
                | models.Q(effective_to__gte=models.F("effective_from")),
                name="repayment_instruction_period_order",
            ),
            models.UniqueConstraint(
                fields=["status"],
                condition=models.Q(status="active"),
                name="uniq_active_repayment_instruction",
            ),
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError(
                {"repayment_instruction_version": "Approved versions are immutable."}
            )
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError(
            {"repayment_instruction_version": "Approved versions are retained."}
        )


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


class ImmutableApprovedInterestRateQuerySet(models.QuerySet):
    _ERROR = {"interest_rate_config": "Approved rate versions require the canonical rate owner."}

    def update(self, **kwargs):
        if self.filter(status="active").exists() or "status" in kwargs:
            raise ValidationError(self._ERROR)
        return super().update(**kwargs)

    def bulk_create(self, objs, *args, **kwargs):
        if any(row.status == "active" for row in objs):
            raise ValidationError(self._ERROR)
        return super().bulk_create(objs, *args, **kwargs)

    def bulk_update(self, objs, fields, batch_size=None):
        object_ids = [row.pk for row in objs if row.pk]
        if (
            "status" in fields
            or any(row.status == "active" for row in objs)
            or self.filter(pk__in=object_ids, status="active").exists()
        ):
            raise ValidationError(self._ERROR)
        return super().bulk_update(objs, fields, batch_size=batch_size)

    def delete(self):
        if self.filter(status="active").exists():
            raise ValidationError(self._ERROR)
        return super().delete()

    def _canonical_update(self, **kwargs):
        """Internal transition primitive; public callers use the rate-owner module."""
        return super().update(**kwargs)


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

    objects = ImmutableApprovedInterestRateQuerySet.as_manager()

    class Meta:
        db_table = "interest_rate_configs"
        base_manager_name = "objects"
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
            models.CheckConstraint(
                check=(
                    models.Q(
                        status="proposed",
                        approved_by_user__isnull=True,
                        activated_at__isnull=True,
                        activation_idempotency_key__isnull=True,
                        activation_payload_digest="",
                    )
                    | (
                        models.Q(
                            status="active",
                            approved_by_user__isnull=False,
                            activated_at__isnull=False,
                            activation_idempotency_key__isnull=False,
                            activation_payload_digest__regex=r"^[0-9a-f]{64}$",
                        )
                        & ~models.Q(activation_idempotency_key="")
                        & ~models.Q(approved_by_user=models.F("created_by_user"))
                    )
                ),
                name="rate_status_approval_coherent",
            ),
        ]

    def save(self, *args, **kwargs):
        if self._state.adding:
            if self.status == self.STATUS_ACTIVE:
                raise ValidationError(
                    {"interest_rate_config": "Activation must use the canonical rate owner."}
                )
        else:
            retained = type(self)._base_manager.get(pk=self.pk)
            if retained.status == self.STATUS_ACTIVE or self.status == self.STATUS_ACTIVE:
                raise ValidationError(
                    {"interest_rate_config": "Approved rate versions are immutable."}
                )
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.status == self.STATUS_ACTIVE:
            raise ValidationError(
                {"interest_rate_config": "Approved rate versions are immutable."}
            )
        return super().delete(*args, **kwargs)


class AppendOnlyInterestRateHistoryQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError({"interest_rate_history": "Rate history is append-only."})

    def delete(self):
        raise ValidationError({"interest_rate_history": "Rate history is append-only."})


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

    objects = AppendOnlyInterestRateHistoryQuerySet.as_manager()

    class Meta:
        db_table = "interest_rate_histories"
        ordering = ["effective_from", "interest_rate_history_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["loan_account", "rate_config"],
                name="uniq_loan_rate_config_history",
            )
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError({"interest_rate_history": "Rate history is append-only."})
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError({"interest_rate_history": "Rate history is append-only."})


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

    def delete(self, *args, **kwargs):
        raise ValidationError(
            {"interest_rate_consumption": "Consumed rate snapshots are immutable."}
        )


class ImmutableCurrentRateProjectionDecisionQuerySet(models.QuerySet):
    _ERROR = {"current_rate_projection": "Current-rate decisions require the canonical owner."}

    def create(self, **kwargs):
        raise ValidationError(self._ERROR)

    def bulk_create(self, objs, *args, **kwargs):
        raise ValidationError(self._ERROR)

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValidationError(self._ERROR)

    def update(self, **kwargs):
        raise ValidationError(
            {"current_rate_projection": "Current-rate decisions are immutable."}
        )

    def delete(self):
        raise ValidationError(
            {"current_rate_projection": "Current-rate decisions are immutable."}
        )

    def _canonical_create(self, **kwargs):
        row = self.model(**kwargs)
        row._canonical_write = True
        row.save(force_insert=True)
        return row


class CurrentRateProjectionDecision(models.Model):
    current_rate_projection_decision_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    loan_account = models.ForeignKey(
        "loans.LoanAccount",
        on_delete=models.PROTECT,
        related_name="current_rate_projection_decisions",
    )
    rate_config = models.ForeignKey(
        InterestRateConfig,
        on_delete=models.PROTECT,
        related_name="current_projection_decisions",
    )
    as_of_date = models.DateField(db_index=True)
    idempotency_key = models.CharField(max_length=255, unique=True)
    payload_digest = models.CharField(max_length=64)
    old_interest_rate = models.DecimalField(max_digits=8, decimal_places=4)
    current_interest_rate = models.DecimalField(max_digits=8, decimal_places=4)
    projection_changed = models.BooleanField()
    actor_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="current_rate_projection_decisions",
    )
    actor_type = models.CharField(max_length=20)
    invocation = models.CharField(max_length=40)
    actor_role_codes_json = models.JSONField(default=list)
    audit_log = models.OneToOneField(
        "identity.AuditLog",
        on_delete=models.PROTECT,
        related_name="current_rate_projection_decision",
    )
    created_at = models.DateTimeField(default=timezone.now)

    objects = ImmutableCurrentRateProjectionDecisionQuerySet.as_manager()

    class Meta:
        db_table = "current_rate_projection_decisions"
        constraints = [
            models.UniqueConstraint(
                fields=["loan_account", "rate_config"],
                name="uniq_current_rate_account_version",
            )
        ]
        indexes = [
            models.Index(
                fields=["as_of_date", "loan_account"],
                name="idx_current_rate_date_account",
            )
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding or not getattr(self, "_canonical_write", False):
            raise ValidationError(
                {"current_rate_projection": "Current-rate decisions are immutable."}
            )
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError(
            {"current_rate_projection": "Current-rate decisions are immutable."}
        )


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
