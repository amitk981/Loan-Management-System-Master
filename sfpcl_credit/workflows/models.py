import uuid

from django.db import models
from django.utils import timezone


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


def workflow_task_reference():
    return f"TSK-{uuid.uuid4().hex[:12].upper()}"


class WorkflowTask(models.Model):
    TYPE_COMPLETENESS_CHECK = "completeness_check"
    TYPE_APPRAISAL = "appraisal"
    TYPE_SANCTION = "sanction"
    TYPE_DOCUMENT_VERIFICATION = "document_verification"
    TYPE_SAP_SETUP = "sap_setup"
    TYPE_DISBURSEMENT = "disbursement"
    TYPE_REPAYMENT_POSTING = "repayment_posting"
    TYPE_DEFAULT_REVIEW = "default_review"
    TASK_TYPES = {
        TYPE_COMPLETENESS_CHECK,
        TYPE_APPRAISAL,
        TYPE_SANCTION,
        TYPE_DOCUMENT_VERIFICATION,
        TYPE_SAP_SETUP,
        TYPE_DISBURSEMENT,
        TYPE_REPAYMENT_POSTING,
        TYPE_DEFAULT_REVIEW,
    }

    PRIORITY_NORMAL = "normal"
    PRIORITY_HIGH = "high"
    PRIORITY_CRITICAL = "critical"
    PRIORITIES = {PRIORITY_NORMAL, PRIORITY_HIGH, PRIORITY_CRITICAL}

    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"
    STATUSES = {STATUS_OPEN, STATUS_CLOSED}

    workflow_task_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    task_reference = models.CharField(
        max_length=40, unique=True, default=workflow_task_reference
    )
    task_type = models.CharField(max_length=80, db_index=True)
    linked_entity_type = models.CharField(max_length=100, db_index=True)
    linked_entity_id = models.UUIDField(db_index=True)
    title = models.CharField(max_length=255)
    borrower_name = models.CharField(max_length=255, blank=True)
    borrower_type = models.CharField(max_length=80, blank=True, db_index=True)
    amount = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    special_case = models.BooleanField(default=False, db_index=True)
    exception_required = models.BooleanField(default=False, db_index=True)
    assigned_role_code = models.CharField(max_length=80, db_index=True)
    assigned_team_code = models.CharField(max_length=80, blank=True, db_index=True)
    assigned_to_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="assigned_workflow_tasks",
    )
    priority = models.CharField(
        max_length=20, default=PRIORITY_NORMAL, db_index=True
    )
    status = models.CharField(max_length=20, default=STATUS_OPEN, db_index=True)
    current_status = models.CharField(max_length=100, db_index=True)
    due_at = models.DateTimeField(blank=True, null=True, db_index=True)
    overdue_days = models.PositiveIntegerField(default=0)
    blocked = models.BooleanField(default=False, db_index=True)
    blocked_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "workflow_tasks"
        ordering = ["-priority", "due_at", "task_reference"]
        indexes = [
            models.Index(
                fields=["assigned_role_code", "status", "due_at"],
                name="idx_task_role_status_due",
            ),
            models.Index(
                fields=["assigned_to_user", "status", "due_at"],
                name="idx_task_user_status_due",
            ),
            models.Index(
                fields=["linked_entity_type", "linked_entity_id"],
                name="idx_task_linked_entity",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["linked_entity_type", "linked_entity_id", "task_type"],
                condition=models.Q(status="open"),
                name="uniq_open_workflow_task",
            ),
            models.CheckConstraint(
                check=models.Q(
                    task_type__in=(
                        "appraisal",
                        "completeness_check",
                        "default_review",
                        "disbursement",
                        "document_verification",
                        "repayment_posting",
                        "sanction",
                        "sap_setup",
                    )
                ),
                name="workflow_task_type_valid",
            ),
            models.CheckConstraint(
                check=models.Q(priority__in=("critical", "high", "normal")),
                name="workflow_task_priority_valid",
            ),
            models.CheckConstraint(
                check=models.Q(status__in=("closed", "open")),
                name="workflow_task_status_valid",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(status="open", closed_at__isnull=True)
                    | models.Q(status="closed", closed_at__isnull=False)
                ),
                name="workflow_task_closed_at_coherent",
            ),
        ]


class WorkflowTaskComment(models.Model):
    workflow_task_comment_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    task = models.ForeignKey(
        WorkflowTask, on_delete=models.PROTECT, related_name="comments"
    )
    author_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="workflow_task_comments"
    )
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = "workflow_task_comments"
        ordering = ["created_at", "workflow_task_comment_id"]
