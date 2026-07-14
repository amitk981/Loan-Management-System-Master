import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


def generate_credit_sanction_register_entry_number():
    return f"CSR-{uuid.uuid4()}"


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
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_RETURNED = "returned_for_clarification"
    STATUS_BLOCKED_CONFLICT = "blocked_by_conflict"

    approval_case_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    loan_application = models.ForeignKey(
        "applications.LoanApplication",
        on_delete=models.PROTECT,
        related_name="sanction_approval_cases",
    )
    loan_appraisal_note = models.ForeignKey(
        "credit.LoanAppraisalNote",
        on_delete=models.PROTECT,
        related_name="sanction_approval_cases",
    )
    appraisal_review_decision = models.ForeignKey(
        "credit.AppraisalReviewDecision",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="sanction_approval_cases",
    )
    appraisal_revision = models.PositiveIntegerField(default=1)
    appraisal_facts_json = models.JSONField(default=dict, blank=True)
    cycle_number = models.PositiveIntegerField(default=1)
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
    excluded_approvers_json = models.JSONField(default=list, blank=True)
    general_meeting_evidence_required = models.BooleanField(default=False)
    general_meeting_approval = models.ForeignKey(
        "approvals.GeneralMeetingApproval",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="consuming_approval_cases",
    )
    conflict_block_reason = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    related_entity_type = models.CharField(max_length=80, blank=True)
    related_entity_id = models.UUIDField(null=True, blank=True, db_index=True)
    reason_for_approval = models.TextField(blank=True)
    reason_for_rejection = models.TextField(blank=True)
    exception_condition_code = models.CharField(max_length=120, blank=True)
    exception_reason = models.TextField(blank=True)
    matrix_projection_json = models.JSONField(default=dict, blank=True)
    committee_projection_json = models.JSONField(default=dict, blank=True)
    loan_limit_provenance_json = models.JSONField(default=dict, blank=True)
    decision_date = models.DateField(null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    closed_at = models.DateTimeField(null=True, blank=True)
    routing_snapshot_is_coherent = models.BooleanField(default=False, db_index=True)

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
            ),
            models.CheckConstraint(
                check=models.Q(cycle_number__gte=1),
                name="approval_case_cycle_positive",
            ),
            models.CheckConstraint(
                check=models.Q(appraisal_revision__gte=1),
                name="approval_case_appraisal_revision_positive",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(cycle_number=1)
                    | models.Q(appraisal_review_decision__isnull=False)
                ),
                name="approval_later_cycle_review_required",
            ),
            models.UniqueConstraint(
                fields=["loan_application", "cycle_number"],
                name="unique_application_approval_cycle",
            ),
            models.UniqueConstraint(
                fields=["loan_application"],
                condition=models.Q(current_status="pending"),
                name="unique_pending_application_approval_cycle",
            ),
        ]


class ApprovalCaseRequiredApprover(models.Model):
    approval_case_required_approver_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    approval_case = models.ForeignKey(
        ApprovalCase,
        on_delete=models.CASCADE,
        related_name="required_approver_index",
    )
    user_id = models.UUIDField(db_index=True)

    class Meta:
        db_table = "approval_case_required_approvers"
        constraints = [
            models.UniqueConstraint(
                fields=["approval_case", "user_id"],
                name="unique_case_required_approver",
            )
        ]


class ApprovalCaseReadScopeGrant(models.Model):
    SCOPE_LEGAL_READONLY = "legal_readonly"
    SCOPE_AUDIT_READONLY = "audit_readonly"
    SCOPE_MANAGEMENT_READONLY = "management_readonly"
    SCOPE_TYPES = (
        (SCOPE_LEGAL_READONLY, "Legal read-only"),
        (SCOPE_AUDIT_READONLY, "Audit read-only"),
        (SCOPE_MANAGEMENT_READONLY, "Management read-only"),
    )
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUSES = (
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"),
    )

    approval_case_read_scope_grant_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    role = models.ForeignKey(
        "identity.Role",
        on_delete=models.PROTECT,
        related_name="approval_case_read_scope_grants",
    )
    scope_type = models.CharField(max_length=40, choices=SCOPE_TYPES)
    status = models.CharField(
        max_length=20, choices=STATUSES, default=STATUS_ACTIVE, db_index=True
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "approval_case_read_scope_grants"
        indexes = [
            models.Index(
                fields=["role", "status", "scope_type"],
                name="idx_case_read_role_scope",
            )
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["role", "scope_type"],
                name="unique_case_read_role_scope",
            ),
            models.CheckConstraint(
                check=models.Q(
                    scope_type__in=[
                        "legal_readonly",
                        "audit_readonly",
                        "management_readonly",
                    ]
                ),
                name="case_read_scope_type_valid",
            ),
            models.CheckConstraint(
                check=models.Q(status__in=["active", "inactive"]),
                name="case_read_scope_status_valid",
            ),
        ]


class ApprovalConflictDeclaration(models.Model):
    CONFLICT_BORROWER = "borrower"
    CONFLICT_DIRECTOR_RELATIVE = "director_relative"
    CONFLICT_MATERIAL_INTEREST = "material_interest"
    CONFLICT_TYPES = (
        (CONFLICT_BORROWER, "Borrower"),
        (CONFLICT_DIRECTOR_RELATIVE, "Director relative"),
        (CONFLICT_MATERIAL_INTEREST, "Material interest"),
    )

    approval_conflict_declaration_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    loan_application = models.ForeignKey(
        "applications.LoanApplication",
        on_delete=models.PROTECT,
        related_name="approval_conflict_declarations",
    )
    user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="approval_conflict_declarations",
    )
    conflict_type = models.CharField(max_length=40, choices=CONFLICT_TYPES)
    reason = models.TextField()
    declared_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="recorded_approval_conflicts",
    )
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "approval_conflict_declarations"
        constraints = [
            models.UniqueConstraint(
                fields=["loan_application", "user", "conflict_type"],
                name="unique_application_user_conflict",
            ),
            models.CheckConstraint(
                check=models.Q(
                    conflict_type__in=[
                        "borrower",
                        "director_relative",
                        "material_interest",
                    ]
                ),
                name="approval_conflict_type_valid",
            ),
            models.CheckConstraint(
                check=models.Q(reason__regex=r"\S"),
                name="approval_conflict_reason_nonblank",
            ),
        ]
        indexes = [
            models.Index(
                fields=["loan_application", "is_active"],
                name="idx_conflict_app_active",
            )
        ]


class ApprovalAction(models.Model):
    approval_action_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    approval_case = models.ForeignKey(
        ApprovalCase, on_delete=models.PROTECT, related_name="actions"
    )
    approver_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="approval_actions"
    )
    approver_role_code = models.CharField(max_length=100, db_index=True)
    decision = models.CharField(max_length=60, db_index=True)
    comments = models.TextField(null=True, blank=True)
    acted_at = models.DateTimeField(default=timezone.now)
    digital_signature_id = models.UUIDField(null=True, blank=True)
    ip_address = models.CharField(max_length=80, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "approval_actions"
        ordering = ["acted_at", "approval_action_id"]
        indexes = [
            models.Index(
                fields=["approval_case", "decision"], name="idx_action_case_decision"
            )
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["approval_case", "approver_user"],
                name="unique_case_approver_action",
            ),
            models.CheckConstraint(
                check=models.Q(
                    decision__in=["approved", "rejected", "returned", "abstained"]
                ),
                name="approval_action_valid_decision",
            ),
        ]


class SanctionDecision(models.Model):
    sanction_decision_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    loan_application = models.OneToOneField(
        "applications.LoanApplication",
        on_delete=models.PROTECT,
        related_name="sanction_decision",
    )
    approval_case = models.OneToOneField(
        ApprovalCase, on_delete=models.PROTECT, related_name="sanction_decision"
    )
    decision = models.CharField(max_length=60, db_index=True)
    sanctioned_amount = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )
    sanctioned_tenure_months = models.PositiveIntegerField(null=True, blank=True)
    interest_rate_type = models.CharField(max_length=60)
    interest_rate_value = models.DecimalField(
        max_digits=8, decimal_places=4, null=True, blank=True
    )
    repayment_date = models.DateField(null=True, blank=True)
    penal_interest_rate = models.DecimalField(
        max_digits=8, decimal_places=4, null=True, blank=True
    )
    charges_json = models.JSONField(default=dict, blank=True)
    security_required_summary = models.TextField()
    conditions_precedent = models.TextField(blank=True)
    decision_reason = models.TextField()
    recorded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "sanction_decisions"
        indexes = [
            models.Index(fields=["decision", "recorded_at"], name="idx_sanction_decision_time")
        ]


class ImmutableRegisterQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError("Credit Sanction Register entries are immutable.")

    def delete(self):
        raise ValidationError("Credit Sanction Register entries are immutable.")


class CreditSanctionRegisterEntry(models.Model):
    DECISION_SANCTIONED = "sanctioned"
    DECISION_REJECTED = "rejected"
    DECISIONS = (
        (DECISION_SANCTIONED, "Sanctioned"),
        (DECISION_REJECTED, "Rejected"),
    )

    credit_sanction_register_entry_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    entry_number = models.CharField(
        max_length=40,
        unique=True,
        default=generate_credit_sanction_register_entry_number,
        editable=False,
    )
    approval_case = models.OneToOneField(
        ApprovalCase,
        on_delete=models.PROTECT,
        related_name="credit_sanction_register_entry",
    )
    loan_application = models.ForeignKey(
        "applications.LoanApplication",
        on_delete=models.PROTECT,
        related_name="credit_sanction_register_entries",
    )
    member = models.ForeignKey(
        "members.Member",
        on_delete=models.PROTECT,
        related_name="credit_sanction_register_entries",
    )
    sanction_decision = models.OneToOneField(
        SanctionDecision,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="credit_sanction_register_entry",
    )
    workflow_event = models.OneToOneField(
        "workflows.WorkflowEvent",
        on_delete=models.PROTECT,
        related_name="credit_sanction_register_entry",
    )
    application_number = models.CharField(max_length=40)
    borrower_name = models.CharField(max_length=255)
    borrower_type = models.CharField(max_length=60)
    requested_amount = models.DecimalField(max_digits=18, decimal_places=2)
    eligible_amount = models.DecimalField(max_digits=18, decimal_places=2)
    recommended_amount = models.DecimalField(max_digits=18, decimal_places=2)
    source_review_facts_json = models.JSONField(default=dict)
    terminal_facts_json = models.JSONField(default=dict)
    sanctioned_amount = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )
    authority_applied_summary = models.TextField()
    approver_names_json = models.JSONField(default=list)
    approver_decisions_json = models.JSONField(default=list)
    approval_date = models.DateField(db_index=True)
    decision = models.CharField(max_length=60, choices=DECISIONS, db_index=True)
    reasons = models.TextField()
    exception_reference_json = models.JSONField(null=True, blank=True)
    conflict_abstention_details_json = models.JSONField(default=list)
    general_meeting_approval_reference_json = models.JSONField(null=True, blank=True)
    communication_json = models.JSONField(null=True, blank=True)
    recorded_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="recorded_credit_sanction_register_entries",
    )
    recorded_at = models.DateTimeField(default=timezone.now, db_index=True)

    objects = ImmutableRegisterQuerySet.as_manager()

    class Meta:
        db_table = "credit_sanction_register_entries"
        ordering = ["-approval_date", "-recorded_at", "-credit_sanction_register_entry_id"]
        indexes = [
            models.Index(
                fields=["decision", "approval_date"],
                name="idx_sanction_register_decision",
            )
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(decision__in=["sanctioned", "rejected"]),
                name="sanction_register_valid_decision",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(decision="sanctioned", sanction_decision__isnull=False)
                    | models.Q(decision="rejected", sanction_decision__isnull=True)
                ),
                name="sanction_register_decision_link",
            ),
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError("Credit Sanction Register entries are immutable.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Credit Sanction Register entries are immutable.")


class ExceptionRegisterEntry(models.Model):
    TYPE_EXCEEDS_LOAN_LIMIT = "exceeds_loan_limit"
    TYPE_STAGE_BYPASS = "stage_bypass"
    TYPE_WAIVER = "waiver"
    EXCEPTION_TYPES = (
        (TYPE_EXCEEDS_LOAN_LIMIT, "Exceeds loan limit"),
        (TYPE_STAGE_BYPASS, "Stage bypass"),
        (TYPE_WAIVER, "Waiver"),
    )
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUSES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    )

    exception_register_entry_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    loan_application = models.ForeignKey(
        "applications.LoanApplication",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="exception_register_entries",
    )
    loan_account_id = models.UUIDField(null=True, blank=True, db_index=True)
    exception_type = models.CharField(
        max_length=100, choices=EXCEPTION_TYPES, db_index=True
    )
    description = models.TextField()
    business_reason = models.TextField()
    risk_assessment = models.TextField(null=True, blank=True)
    supporting_documents_json = models.JSONField(default=list)
    source_facts_json = models.JSONField(default=dict)
    approval_case = models.OneToOneField(
        ApprovalCase,
        on_delete=models.PROTECT,
        related_name="exception_register_entry",
    )
    status = models.CharField(
        max_length=60, choices=STATUSES, default=STATUS_PENDING, db_index=True
    )
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "exception_register_entries"
        ordering = ["-created_at", "-exception_register_entry_id"]
        indexes = [
            models.Index(
                fields=["exception_type", "status", "created_at"],
                name="idx_exception_type_status",
            )
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(
                    exception_type__in=[
                        "exceeds_loan_limit",
                        "stage_bypass",
                        "waiver",
                    ]
                ),
                name="exception_register_type_valid",
            ),
            models.CheckConstraint(
                check=models.Q(status__in=["pending", "approved", "rejected"]),
                name="exception_register_status_valid",
            ),
            models.CheckConstraint(
                check=models.Q(description__regex=r"\S"),
                name="exception_register_description_nonblank",
            ),
            models.CheckConstraint(
                check=models.Q(business_reason__regex=r"\S"),
                name="exception_register_reason_nonblank",
            ),
        ]


class GeneralMeetingApproval(models.Model):
    TYPE_DIRECTOR = "director"
    TYPE_DIRECTOR_RELATIVE = "director_relative"
    TYPE_COMMITTEE_MEMBER = "committee_member"
    RELATED_PARTY_TYPES = (
        (TYPE_DIRECTOR, "Director"),
        (TYPE_DIRECTOR_RELATIVE, "Director relative"),
        (TYPE_COMMITTEE_MEMBER, "Sanction Committee member"),
    )
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUSES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    )

    general_meeting_approval_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    loan_application = models.ForeignKey(
        "applications.LoanApplication",
        on_delete=models.PROTECT,
        related_name="general_meeting_approvals",
    )
    related_party_type = models.CharField(max_length=80, choices=RELATED_PARTY_TYPES)
    related_party_user = models.ForeignKey(
        "identity.User",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="related_general_meeting_approvals",
    )
    relationship_description = models.TextField()
    meeting_date = models.DateField()
    notice_document = models.ForeignKey(
        "documents.DocumentFile",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="general_meeting_notice_records",
    )
    minutes_document = models.ForeignKey(
        "documents.DocumentFile",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="general_meeting_minutes_records",
    )
    resolution_document = models.ForeignKey(
        "documents.DocumentFile",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="general_meeting_resolution_records",
    )
    approval_status = models.CharField(
        max_length=60, choices=STATUSES, db_index=True
    )
    recorded_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="recorded_general_meeting_approvals",
    )
    recorded_at = models.DateTimeField(default=timezone.now, db_index=True)
    supersedes = models.OneToOneField(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="superseded_by",
    )

    class Meta:
        db_table = "general_meeting_approvals"
        ordering = ["-recorded_at", "-general_meeting_approval_id"]
        indexes = [
            models.Index(
                fields=["loan_application", "recorded_at"],
                name="idx_gm_application_time",
            )
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(
                    related_party_type__in=[
                        "director",
                        "director_relative",
                        "committee_member",
                    ]
                ),
                name="gm_related_party_type_valid",
            ),
            models.CheckConstraint(
                check=models.Q(approval_status__in=["pending", "approved", "rejected"]),
                name="gm_approval_status_valid",
            ),
            models.CheckConstraint(
                check=models.Q(relationship_description__regex=r"\S"),
                name="gm_relationship_nonblank",
            ),
        ]
