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
