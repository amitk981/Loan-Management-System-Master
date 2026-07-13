import uuid

from django.db import models
from django.utils import timezone


class ApprovalConfigurationLock(models.Model):
    lock_name = models.CharField(max_length=40, primary_key=True)

    class Meta:
        db_table = "approval_configuration_locks"


class ApprovalConfigurationProposal(models.Model):
    TYPE_RULE_CREATE = "rule_create"
    TYPE_RULE_SUPERSEDE = "rule_supersede"
    TYPE_COMMITTEE_CREATE = "committee_create"
    TYPE_COMMITTEE_SUPERSEDE = "committee_supersede"
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    approval_configuration_proposal_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    proposal_type = models.CharField(max_length=40, db_index=True)
    target_entity_id = models.UUIDField(null=True, blank=True)
    payload_json = models.JSONField()
    reason = models.TextField()
    status = models.CharField(max_length=20, default=STATUS_PENDING, db_index=True)
    version = models.PositiveIntegerField(default=1)
    made_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="made_approval_configuration_proposals"
    )
    made_at = models.DateTimeField(default=timezone.now)
    decided_by_user = models.ForeignKey(
        "identity.User", null=True, blank=True, on_delete=models.PROTECT,
        related_name="decided_approval_configuration_proposals",
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    request_id = models.CharField(max_length=255, blank=True)
    request_ip = models.CharField(max_length=80, blank=True)
    request_user_agent = models.TextField(blank=True)

    class Meta:
        db_table = "approval_configuration_proposals"
        ordering = ["-made_at", "-approval_configuration_proposal_id"]
        indexes = [models.Index(fields=["status", "proposal_type"], name="idx_config_proposal_state")]
        constraints = [
            models.CheckConstraint(
                check=models.Q(status__in=["pending", "approved", "rejected"]),
                name="config_proposal_valid_status",
            ),
            models.CheckConstraint(check=models.Q(version__gte=1), name="config_proposal_version_positive"),
        ]


class ApprovalMatrixRule(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_SUPERSEDED = "superseded"
    STATUS_INACTIVE = "inactive"

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
        constraints = [
            models.CheckConstraint(
                check=models.Q(status__in=["active", "superseded", "inactive"]),
                name="approval_rule_valid_status",
            ),
            models.CheckConstraint(
                check=models.Q(effective_to__isnull=True) | models.Q(effective_to__gte=models.F("effective_from")),
                name="approval_rule_valid_dates",
            ),
            models.CheckConstraint(
                check=models.Q(amount_min__isnull=True) | models.Q(amount_max__isnull=True) | models.Q(amount_max__gte=models.F("amount_min")),
                name="approval_rule_valid_amounts",
            ),
        ]


class SanctionCommittee(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_SUPERSEDED = "superseded"
    STATUS_INACTIVE = "inactive"

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
        indexes = [models.Index(fields=["status", "effective_from", "effective_to"], name="idx_committee_effective")]
        constraints = [
            models.CheckConstraint(
                check=models.Q(status__in=["active", "superseded", "inactive"]),
                name="committee_valid_status",
            ),
            models.CheckConstraint(
                check=models.Q(effective_to__isnull=True) | models.Q(effective_to__gte=models.F("effective_from")),
                name="committee_valid_dates",
            ),
            models.CheckConstraint(
                check=~models.Q(cfo_user=models.F("director_1_user")) & ~models.Q(cfo_user=models.F("director_2_user")) & ~models.Q(director_1_user=models.F("director_2_user")),
                name="committee_distinct_members",
            ),
        ]


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
    approval_matrix_rule = models.ForeignKey(
        ApprovalMatrixRule, null=True, blank=True, on_delete=models.PROTECT,
        related_name="snapshotted_approval_cases",
    )
    approval_matrix_rule_version = models.CharField(max_length=40, blank=True)
    sanction_committee = models.ForeignKey(
        SanctionCommittee, null=True, blank=True, on_delete=models.PROTECT,
        related_name="snapshotted_approval_cases",
    )
    sanction_committee_version = models.CharField(max_length=40, blank=True)
    required_approvers_json = models.JSONField(default=dict, blank=True)
    decision_date = models.DateField(null=True, blank=True)
    version = models.PositiveIntegerField(default=1)

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
        constraints = [
            models.CheckConstraint(
                check=models.Q(version__gte=1), name="approval_case_version_positive"
            )
        ]
