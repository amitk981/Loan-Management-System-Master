import uuid

from django.db import models
from django.utils import timezone


class RecoveryDecisionQuerySet(models.QuerySet):
    FROZEN_FIELDS = frozenset(
        {
            "default_case",
            "default_case_id",
            "non_payment_note",
            "non_payment_note_id",
            "approval_case",
            "approval_case_id",
            "decision",
            "decision_reason",
            "status",
            "approval_evidence_json",
            "decided_by_user",
            "decided_by_user_id",
            "decided_by_role_code",
            "decided_at",
            "workflow_event",
            "workflow_event_id",
        }
    )

    def update(self, **kwargs):
        if self.FROZEN_FIELDS.intersection(kwargs):
            raise ValueError("Recovery Decision evidence is immutable.")
        return super().update(**kwargs)


class RecoveryDecision(models.Model):
    STATUS_APPROVED = "approved"

    recovery_decision_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    default_case = models.OneToOneField(
        "defaults.DefaultCase",
        on_delete=models.PROTECT,
        related_name="recovery_decision",
    )
    non_payment_note = models.OneToOneField(
        "defaults.NonPaymentNote",
        on_delete=models.PROTECT,
        related_name="recovery_decision",
    )
    approval_case = models.OneToOneField(
        "approvals.ApprovalCase",
        on_delete=models.PROTECT,
        related_name="recovery_decision",
    )
    decision = models.CharField(max_length=100, db_index=True)
    decision_reason = models.TextField()
    status = models.CharField(max_length=60, default=STATUS_APPROVED, db_index=True)
    approval_evidence_json = models.JSONField(default=dict)
    decided_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="recovery_decisions",
    )
    decided_by_role_code = models.CharField(max_length=100)
    decided_at = models.DateTimeField(default=timezone.now)
    workflow_event = models.OneToOneField(
        "workflows.WorkflowEvent",
        on_delete=models.PROTECT,
        related_name="recovery_decision",
    )

    objects = RecoveryDecisionQuerySet.as_manager()

    class Meta:
        db_table = "recovery_decisions"
        ordering = ["-decided_at", "-recovery_decision_id"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(status="approved"),
                name="recovery_decision_approved_only",
            ),
            models.CheckConstraint(
                check=~models.Q(decision="") & ~models.Q(decision_reason=""),
                name="recovery_decision_text_required",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            original = type(self).objects.get(pk=self.pk)
            changed = [
                field
                for field in RecoveryDecisionQuerySet.FROZEN_FIELDS
                if hasattr(self, field)
                and getattr(self, field) != getattr(original, field)
            ]
            if changed:
                raise ValueError("Recovery Decision evidence is immutable.")
        return super().save(*args, **kwargs)


class RecoveryActionQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValueError("Recovery Action history may change only through RecoveryWorkflow.")


class RecoveryAction(models.Model):
    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    TERMINAL_STATUSES = {STATUS_COMPLETED, STATUS_FAILED}

    recovery_action_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    recovery_decision = models.OneToOneField(
        RecoveryDecision,
        on_delete=models.PROTECT,
        related_name="recovery_action",
    )
    approval_case = models.ForeignKey(
        "approvals.ApprovalCase",
        on_delete=models.PROTECT,
        related_name="recovery_actions",
    )
    loan_account = models.ForeignKey(
        "loans.LoanAccount",
        on_delete=models.PROTECT,
        related_name="recovery_actions",
    )
    action_type = models.CharField(max_length=100, db_index=True)
    action_status = models.CharField(
        max_length=60, default=STATUS_PENDING, db_index=True
    )
    source_security_type = models.CharField(max_length=60)
    source_security_id = models.UUIDField()
    source_security_evidence_json = models.JSONField(default=dict)
    initiated_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="initiated_recovery_actions",
    )
    initiated_by_role_code = models.CharField(max_length=100)
    initiated_at = models.DateTimeField()
    initiation_evidence_document_ids_json = models.JSONField(default=list)
    initiation_remarks = models.TextField()
    interaction_log_json = models.JSONField(default=list)
    completed_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="completed_recovery_actions",
    )
    completed_at = models.DateTimeField(blank=True, null=True)
    amount_recovered = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    completion_evidence_document_ids_json = models.JSONField(default=list)
    completion_remarks = models.TextField(blank=True)
    failed_at = models.DateTimeField(blank=True, null=True)
    failure_reason = models.TextField(blank=True)
    ledger_posting_json = models.JSONField(default=dict)
    external_sap_status = models.CharField(max_length=60, default="pending")
    initiation_workflow_event = models.OneToOneField(
        "workflows.WorkflowEvent",
        on_delete=models.PROTECT,
        related_name="initiated_recovery_action",
    )
    completion_workflow_event = models.OneToOneField(
        "workflows.WorkflowEvent",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="completed_recovery_action",
    )
    created_at = models.DateTimeField(default=timezone.now)

    objects = RecoveryActionQuerySet.as_manager()

    class Meta:
        db_table = "recovery_actions"
        ordering = ["-initiated_at", "-recovery_action_id"]
        indexes = [
            models.Index(
                fields=["loan_account", "action_status"],
                name="idx_recovery_action_account",
            ),
            models.Index(
                fields=["source_security_type", "source_security_id"],
                name="idx_recovery_action_security",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(action_status__in=("pending", "completed", "failed")),
                name="recovery_action_status_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(amount_recovered__isnull=True)
                | models.Q(amount_recovered__gte=0),
                name="recovery_action_amount_nonnegative",
            ),
            models.CheckConstraint(
                check=models.Q(external_sap_status="pending"),
                name="recovery_action_sap_pending_only",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(
                        action_status="pending",
                        completed_by_user__isnull=True,
                        completed_at__isnull=True,
                        amount_recovered__isnull=True,
                        completion_workflow_event__isnull=True,
                        failed_at__isnull=True,
                        failure_reason="",
                        ledger_posting_json={},
                    )
                    | models.Q(
                        action_status="completed",
                        completed_by_user__isnull=False,
                        completed_at__isnull=False,
                        amount_recovered__isnull=False,
                        completion_workflow_event__isnull=False,
                        failed_at__isnull=True,
                        failure_reason="",
                    )
                    | models.Q(
                        action_status="failed",
                        completed_by_user__isnull=True,
                        completed_at__isnull=True,
                        amount_recovered__isnull=True,
                        completion_workflow_event__isnull=True,
                        failed_at__isnull=False,
                        ledger_posting_json={},
                    )
                ),
                name="recovery_action_terminal_evidence",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            original = type(self).objects.get(pk=self.pk)
            frozen = {
                "recovery_decision_id",
                "approval_case_id",
                "loan_account_id",
                "action_type",
                "source_security_type",
                "source_security_id",
                "source_security_evidence_json",
                "initiated_by_user_id",
                "initiated_by_role_code",
                "initiated_at",
                "initiation_evidence_document_ids_json",
                "initiation_remarks",
                "interaction_log_json",
                "initiation_workflow_event_id",
                "external_sap_status",
                "created_at",
            }
            if any(getattr(self, field) != getattr(original, field) for field in frozen):
                raise ValueError("Recovery Action initiation evidence is immutable.")
            if original.action_status in self.TERMINAL_STATUSES:
                concrete = {
                    field.attname for field in self._meta.concrete_fields
                }
                if any(
                    getattr(self, field) != getattr(original, field)
                    for field in concrete
                ):
                    raise ValueError("Terminal Recovery Action evidence is immutable.")
        return super().save(*args, **kwargs)
