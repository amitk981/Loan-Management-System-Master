import uuid

from django.db import models
from django.utils import timezone


class ImmutableClosureQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValueError("Loan Closure evidence is immutable.")

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValueError("Loan Closure evidence is immutable.")

    def delete(self):
        raise ValueError("Loan Closure evidence is immutable.")


class LoanClosure(models.Model):
    TYPE_FULL_REPAYMENT = "full_repayment"
    STAGE_FINANCIALLY_CLOSED = "financially_closed"

    loan_closure_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan_account = models.OneToOneField(
        "loans.LoanAccount", on_delete=models.PROTECT, related_name="loan_closure"
    )
    member = models.ForeignKey(
        "members.Member", on_delete=models.PROTECT, related_name="loan_closures"
    )
    closure_type = models.CharField(max_length=80, db_index=True)
    closure_stage = models.CharField(max_length=80, db_index=True)
    closure_notes = models.TextField()
    principal_paid_flag = models.BooleanField()
    interest_paid_flag = models.BooleanField()
    charges_paid_flag = models.BooleanField()
    total_outstanding_at_closure = models.DecimalField(max_digits=18, decimal_places=2)
    readiness_snapshot_json = models.JSONField()
    closed_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="closed_loans"
    )
    closed_by_role_code = models.CharField(max_length=100)
    closed_at = models.DateTimeField(default=timezone.now, db_index=True)
    idempotency_key_digest = models.CharField(max_length=64, unique=True)
    payload_digest = models.CharField(max_length=64)
    close_audit = models.OneToOneField(
        "identity.AuditLog", on_delete=models.PROTECT, related_name="loan_closure"
    )
    workflow_event = models.OneToOneField(
        "workflows.WorkflowEvent", on_delete=models.PROTECT, related_name="loan_closure"
    )

    objects = ImmutableClosureQuerySet.as_manager()

    class Meta:
        db_table = "loan_closures"
        constraints = [
            models.CheckConstraint(
                check=models.Q(closure_type="full_repayment"),
                name="loan_closure_full_repayment_only",
            ),
            models.CheckConstraint(
                check=models.Q(closure_stage="financially_closed"),
                name="loan_closure_financial_stage_only",
            ),
            models.CheckConstraint(
                check=models.Q(principal_paid_flag=True)
                & models.Q(interest_paid_flag=True)
                & models.Q(charges_paid_flag=True)
                & models.Q(total_outstanding_at_closure=0),
                name="loan_closure_zero_balance_only",
            ),
            models.CheckConstraint(
                check=~models.Q(closure_notes="") & ~models.Q(closed_by_role_code=""),
                name="loan_closure_text_required",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise ValueError("Loan Closure evidence is immutable.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Loan Closure evidence is immutable.")


class ClosureRequirement(models.Model):
    TYPE_NOC = "noc"
    TYPE_SECURITY_RETURN = "security_return"
    TYPE_ARCHIVE = "archive"
    STATUS_PENDING = "pending"
    STATUS_NOT_APPLICABLE = "not_applicable"

    closure_requirement_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    loan_closure = models.ForeignKey(
        LoanClosure, on_delete=models.PROTECT, related_name="requirements"
    )
    requirement_type = models.CharField(max_length=60, db_index=True)
    requirement_status = models.CharField(max_length=60, db_index=True)
    applicability_snapshot_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)

    objects = ImmutableClosureQuerySet.as_manager()

    class Meta:
        db_table = "closure_requirements"
        constraints = [
            models.UniqueConstraint(
                fields=["loan_closure", "requirement_type"],
                name="uniq_closure_requirement_type",
            ),
            models.CheckConstraint(
                check=models.Q(requirement_type__in=("noc", "security_return", "archive")),
                name="closure_requirement_type_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(requirement_status__in=("pending", "not_applicable")),
                name="closure_requirement_status_bounded",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise ValueError("Closure Requirement evidence is immutable until its owner slice.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Closure Requirement evidence is immutable until its owner slice.")
