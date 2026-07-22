import uuid

from django.db import models
from django.utils import timezone


class DefaultCase(models.Model):
    TRIGGER_MISSED_PRINCIPAL = "missed_principal_repayment"
    STATUS_GRACE_PERIOD_ACTIVE = "grace_period_active"
    STATUS_GRACE_PERIOD_EXPIRED = "grace_period_expired"
    STATUS_ASSESSMENT_IN_PROGRESS = "assessment_in_progress"
    STATUS_RESOLVED_BY_REPAYMENT = "resolved_by_repayment"

    default_case_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    loan_account = models.ForeignKey(
        "loans.LoanAccount", on_delete=models.PROTECT, related_name="default_cases"
    )
    member = models.ForeignKey(
        "members.Member", on_delete=models.PROTECT, related_name="default_cases"
    )
    repayment_schedule = models.ForeignKey(
        "loans.RepaymentSchedule",
        on_delete=models.PROTECT,
        related_name="default_cases",
    )
    trigger_event = models.CharField(max_length=80, db_index=True)
    scheduled_due_date = models.DateField(db_index=True)
    default_detected_at = models.DateTimeField(default=timezone.now)
    grace_period_start_date = models.DateField()
    grace_period_end_date = models.DateField(db_index=True)
    default_case_status = models.CharField(max_length=80, db_index=True)
    current_assessment = models.ForeignKey(
        "DefaultAssessment",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="current_for_cases",
    )
    reason = models.CharField(max_length=2000, blank=True)
    opened_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="opened_default_cases"
    )
    opening_audit = models.OneToOneField(
        "identity.AuditLog",
        on_delete=models.PROTECT,
        related_name="opened_default_case",
    )
    created_at = models.DateTimeField(default=timezone.now)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "default_cases"
        ordering = ["-default_detected_at", "-default_case_id"]
        indexes = [
            models.Index(
                fields=["member", "default_case_status"],
                name="idx_default_member_status",
            ),
            models.Index(
                fields=["loan_account", "default_case_status"],
                name="idx_default_loan_status",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["repayment_schedule", "trigger_event"],
                name="uniq_default_missed_obligation",
            ),
            models.CheckConstraint(
                check=models.Q(trigger_event="missed_principal_repayment"),
                name="default_trigger_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(
                    default_case_status__in=(
                        "open",
                        "grace_period_active",
                        "grace_period_expired",
                        "assessment_in_progress",
                        "extension_granted",
                        "extension_expired",
                        "non_payment_under_review",
                        "recovery_decision_pending",
                        "recovery_approved",
                        "recovery_in_progress",
                        "resolved_by_repayment",
                        "closed",
                    )
                ),
                name="default_status_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(grace_period_start_date=models.F("scheduled_due_date")),
                name="default_grace_starts_due",
            ),
            models.CheckConstraint(
                check=models.Q(grace_period_end_date__gt=models.F("grace_period_start_date")),
                name="default_grace_period_order",
            ),
        ]


class DefaultAssessment(models.Model):
    TYPE_POST_GRACE = "post_grace"
    TYPE_POST_EXTENSION = "post_extension"
    ASSESSMENT_TYPES = {TYPE_POST_GRACE, TYPE_POST_EXTENSION}
    CLASSIFICATIONS = {"intentional", "non_intentional", "unclear"}

    default_assessment_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    default_case = models.ForeignKey(
        DefaultCase, on_delete=models.PROTECT, related_name="assessments"
    )
    assessment_type = models.CharField(max_length=80)
    payment_failure_classification = models.CharField(max_length=80, db_index=True)
    reason_summary = models.TextField()
    evidence_document_ids_json = models.JSONField(default=list)
    borrower_interaction_summary = models.TextField(blank=True)
    assessed_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="default_assessments"
    )
    assessed_at = models.DateTimeField(default=timezone.now)
    recommended_action = models.CharField(max_length=100)

    class Meta:
        db_table = "default_assessments"
        ordering = ["-assessed_at", "-default_assessment_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["default_case", "assessment_type"],
                name="uniq_default_case_assessment_type",
            ),
            models.CheckConstraint(
                check=models.Q(assessment_type__in=("post_grace", "post_extension")),
                name="default_assessment_type_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(
                    payment_failure_classification__in=(
                        "intentional",
                        "non_intentional",
                        "unclear",
                    )
                ),
                name="default_classification_bounded",
            ),
            models.CheckConstraint(
                check=~models.Q(reason_summary="")
                & ~models.Q(recommended_action=""),
                name="default_assessment_text_required",
            ),
        ]
