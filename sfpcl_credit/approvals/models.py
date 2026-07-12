import uuid

from django.db import models
from django.utils import timezone


class ApprovalConfigurationLock(models.Model):
    lock_name = models.CharField(max_length=40, primary_key=True)

    class Meta:
        db_table = "approval_configuration_locks"


class ApprovalMatrixRule(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_SUPERSEDED = "superseded"

    approval_matrix_rule_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    decision_type = models.CharField(max_length=80, db_index=True)
    amount_min = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    amount_max = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    condition_code = models.CharField(max_length=120, null=True, blank=True, db_index=True)
    required_approver_roles_json = models.JSONField(default=list)
    required_director_count = models.PositiveSmallIntegerField(default=0)
    joint_approval_required_flag = models.BooleanField(default=True)
    register_required = models.CharField(max_length=100, null=True, blank=True)
    effective_from = models.DateField(db_index=True)
    effective_to = models.DateField(null=True, blank=True, db_index=True)
    status = models.CharField(max_length=40, default=STATUS_ACTIVE, db_index=True)
    version_number = models.CharField(max_length=40)

    class Meta:
        db_table = "approval_matrix_rules"
        ordering = ["decision_type", "condition_code", "amount_min", "effective_from"]
        indexes = [
            models.Index(
                fields=["decision_type", "condition_code", "status"],
                name="idx_matrix_route_status",
            )
        ]


class SanctionCommittee(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_SUPERSEDED = "superseded"

    sanction_committee_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    committee_name = models.CharField(max_length=150)
    cfo_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="cfo_committees"
    )
    director_1_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="director_1_committees"
    )
    director_2_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="director_2_committees"
    )
    board_meeting_reference = models.CharField(max_length=255)
    effective_from = models.DateField(db_index=True)
    effective_to = models.DateField(null=True, blank=True, db_index=True)
    status = models.CharField(max_length=40, default=STATUS_ACTIVE, db_index=True)
    version_number = models.CharField(max_length=40)

    class Meta:
        db_table = "sanction_committees"
        ordering = ["-effective_from", "-sanction_committee_id"]


class ApprovalCase(models.Model):
    TYPE_SANCTION = "sanction"
    STATUS_PENDING = "pending"

    approval_case_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    loan_application = models.OneToOneField(
        "applications.LoanApplication",
        on_delete=models.PROTECT,
        related_name="sanction_approval_case",
    )
    loan_appraisal_note = models.OneToOneField(
        "credit.LoanAppraisalNote",
        on_delete=models.PROTECT,
        related_name="sanction_approval_case",
    )
    approval_type = models.CharField(max_length=80, default=TYPE_SANCTION, db_index=True)
    current_status = models.CharField(max_length=60, default=STATUS_PENDING, db_index=True)
    exception_required_flag = models.BooleanField(default=False, db_index=True)
    submission_remarks = models.TextField()
    submitted_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="submitted_sanction_cases",
    )
    submitted_at = models.DateTimeField(default=timezone.now, db_index=True)
    workflow_event = models.OneToOneField(
        "workflows.WorkflowEvent",
        on_delete=models.PROTECT,
        related_name="sanction_approval_case",
        null=True,
    )

    class Meta:
        db_table = "approval_cases"
        indexes = [
            models.Index(
                fields=["approval_type", "current_status"],
                name="idx_approval_type_status",
            ),
            models.Index(
                fields=["exception_required_flag", "current_status"],
                name="idx_approval_exception",
            ),
        ]
