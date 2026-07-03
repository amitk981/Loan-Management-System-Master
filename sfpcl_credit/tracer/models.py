import uuid

from django.db import models
from django.utils import timezone


class Member(models.Model):
    member_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=40, unique=True)
    display_name = models.CharField(max_length=200)
    status = models.CharField(max_length=40, default="active", db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "tracer_members"
        ordering = ["created_at"]


class LoanApplication(models.Model):
    loan_application_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    reference = models.CharField(max_length=40, unique=True)
    member = models.ForeignKey(
        Member, on_delete=models.PROTECT, related_name="loan_applications"
    )
    status = models.CharField(max_length=80, default="draft", db_index=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "tracer_loan_applications"
        ordering = ["created_at"]


class LoanAccount(models.Model):
    loan_account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=40, unique=True)
    member = models.ForeignKey(Member, on_delete=models.PROTECT, related_name="loan_accounts")
    application = models.OneToOneField(
        LoanApplication, on_delete=models.PROTECT, related_name="loan_account"
    )
    status = models.CharField(max_length=80, default="pending_disbursement", db_index=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "tracer_loan_accounts"
        ordering = ["created_at"]


class Repayment(models.Model):
    repayment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=40, unique=True)
    loan_account = models.ForeignKey(
        LoanAccount, on_delete=models.PROTECT, related_name="repayments"
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=40, default="posted", db_index=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "tracer_repayments"
        ordering = ["created_at"]


class WorkflowEvent(models.Model):
    workflow_event_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    workflow_name = models.CharField(max_length=100, db_index=True)
    entity_type = models.CharField(max_length=100, db_index=True)
    entity_id = models.UUIDField(db_index=True)
    from_state = models.CharField(max_length=100, blank=True, null=True)
    to_state = models.CharField(max_length=100, db_index=True)
    triggered_by_user = models.ForeignKey(
        "identity.User", blank=True, null=True, on_delete=models.PROTECT
    )
    trigger_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = "workflow_events"
        ordering = ["created_at"]
