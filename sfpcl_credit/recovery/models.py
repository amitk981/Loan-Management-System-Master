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
