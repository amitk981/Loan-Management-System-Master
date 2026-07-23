import uuid

from django.db import models
from django.utils import timezone


class ComplianceControl(models.Model):
    TYPE_PREVENTIVE = "preventive"
    TYPE_DETECTIVE = "detective"
    TYPES = {TYPE_PREVENTIVE, TYPE_DETECTIVE}

    FREQUENCY_MONTHLY = "monthly"
    FREQUENCY_QUARTERLY = "quarterly"
    FREQUENCY_ANNUAL = "annual"
    FREQUENCY_ONGOING = "ongoing"
    FREQUENCIES = {
        FREQUENCY_MONTHLY,
        FREQUENCY_QUARTERLY,
        FREQUENCY_ANNUAL,
        FREQUENCY_ONGOING,
    }

    STATUS_ACTIVE = "active"
    STATUS_DISABLED = "disabled"
    STATUSES = {STATUS_ACTIVE, STATUS_DISABLED}

    compliance_control_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    control_code = models.CharField(max_length=120, unique=True)
    control_name = models.CharField(max_length=255)
    control_area = models.CharField(max_length=100, db_index=True)
    legal_basis = models.TextField()
    control_type = models.CharField(max_length=60)
    frequency = models.CharField(max_length=60, db_index=True)
    owner_role_code = models.CharField(max_length=100)
    owner_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="owned_compliance_controls"
    )
    reviewer_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="reviewed_compliance_controls"
    )
    first_due_date = models.DateField(db_index=True)
    evidence_required = models.TextField()
    risk_if_missed = models.TextField()
    status = models.CharField(max_length=40, default=STATUS_ACTIVE, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "compliance_controls"
        ordering = ["control_code"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(control_type__in=("preventive", "detective")),
                name="compliance_control_type_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(frequency__in=("monthly", "quarterly", "annual", "ongoing")),
                name="compliance_control_frequency_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(status__in=("active", "disabled")),
                name="compliance_control_status_bounded",
            ),
            models.CheckConstraint(
                check=~models.Q(owner_user=models.F("reviewer_user")),
                name="compliance_control_maker_checker",
            ),
        ]


class ComplianceTask(models.Model):
    STATUS_DUE = "due"
    STATUS_OVERDUE = "overdue"
    STATUS_EVIDENCE_SUBMITTED = "evidence_submitted"
    STATUS_COMPLETED = "completed"
    STATUSES = {STATUS_DUE, STATUS_OVERDUE, STATUS_EVIDENCE_SUBMITTED, STATUS_COMPLETED}

    compliance_task_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    control = models.ForeignKey(
        ComplianceControl, on_delete=models.PROTECT, related_name="tasks"
    )
    task_period = models.CharField(max_length=40, db_index=True)
    due_date = models.DateField(db_index=True)
    assigned_to_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="assigned_compliance_tasks"
    )
    reviewer_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="compliance_tasks_to_review"
    )
    task_status = models.CharField(max_length=60, db_index=True)
    remarks = models.TextField(blank=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    current_evidence = models.ForeignKey(
        "ComplianceEvidence", blank=True, null=True, on_delete=models.PROTECT,
        related_name="current_for_tasks",
    )
    due_notification = models.OneToOneField(
        "communications.Notification", blank=True, null=True, on_delete=models.PROTECT,
        related_name="compliance_due_task",
    )
    overdue_notification = models.OneToOneField(
        "communications.Notification", blank=True, null=True, on_delete=models.PROTECT,
        related_name="compliance_overdue_task",
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "compliance_tasks"
        ordering = ["due_date", "compliance_task_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["control", "task_period"], name="uniq_compliance_control_period"
            ),
            models.CheckConstraint(
                check=models.Q(
                    task_status__in=("due", "overdue", "evidence_submitted", "completed")
                ),
                name="compliance_task_status_bounded",
            ),
            models.CheckConstraint(
                check=~models.Q(assigned_to_user=models.F("reviewer_user")),
                name="compliance_task_maker_checker",
            ),
        ]
        indexes = [models.Index(fields=["task_status", "due_date"])]


class ComplianceEvidence(models.Model):
    REVIEW_PENDING = "pending"
    REVIEW_ACCEPTED = "accepted"
    REVIEW_REJECTED = "rejected"
    REVIEW_STATUSES = {REVIEW_PENDING, REVIEW_ACCEPTED, REVIEW_REJECTED}

    compliance_evidence_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    task = models.ForeignKey(
        ComplianceTask, on_delete=models.PROTECT, related_name="evidence_submissions"
    )
    evidence_type = models.CharField(max_length=100, db_index=True)
    document = models.ForeignKey(
        "documents.DocumentFile", on_delete=models.PROTECT, related_name="compliance_evidence"
    )
    summary = models.TextField()
    source_owner = models.CharField(max_length=80)
    source_entity_type = models.CharField(max_length=100)
    source_entity_id = models.UUIDField()
    source_period = models.CharField(max_length=40, db_index=True)
    submitted_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="submitted_compliance_evidence"
    )
    submitted_at = models.DateTimeField(default=timezone.now)
    review_status = models.CharField(max_length=60, default=REVIEW_PENDING, db_index=True)
    reviewed_by_user = models.ForeignKey(
        "identity.User", blank=True, null=True, on_delete=models.PROTECT,
        related_name="reviewed_compliance_evidence",
    )
    reviewed_at = models.DateTimeField(blank=True, null=True)
    review_comments = models.TextField(blank=True)

    class Meta:
        db_table = "compliance_evidence"
        ordering = ["submitted_at", "compliance_evidence_id"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(review_status__in=("pending", "accepted", "rejected")),
                name="compliance_evidence_review_bounded",
            )
        ]

    def save(self, *args, **kwargs):
        if self.pk:
            previous = type(self).objects.filter(pk=self.pk).values_list(
                "review_status", flat=True
            ).first()
            if previous == self.REVIEW_ACCEPTED:
                raise ValueError("Accepted compliance evidence is immutable.")
        return super().save(*args, **kwargs)


class ComplianceEvidenceReview(models.Model):
    compliance_evidence_review_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    evidence = models.ForeignKey(
        ComplianceEvidence, on_delete=models.PROTECT, related_name="review_history"
    )
    decision = models.CharField(max_length=60)
    comments = models.TextField()
    reviewed_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="compliance_evidence_reviews"
    )
    reviewed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "compliance_evidence_reviews"
        constraints = [
            models.CheckConstraint(
                check=models.Q(decision__in=("accepted", "rejected")),
                name="compliance_evidence_review_decision_bounded",
            )
        ]


class ComplianceControlVersion(models.Model):
    compliance_control_version_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    control = models.ForeignKey(
        ComplianceControl, on_delete=models.PROTECT, related_name="versions"
    )
    version_number = models.PositiveIntegerField()
    snapshot_json = models.JSONField()
    change_reason = models.TextField()
    effective_from = models.DateField()
    changed_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="compliance_control_versions"
    )
    changed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "compliance_control_versions"
        constraints = [
            models.UniqueConstraint(
                fields=["control", "version_number"], name="uniq_compliance_control_version"
            )
        ]


class KYCReview(models.Model):
    TYPE_ONBOARDING = "onboarding"
    TYPE_REKYC = "rekyc"
    REVIEW_TYPES = {TYPE_ONBOARDING, TYPE_REKYC}

    STATUS_PENDING = "pending"
    STATUS_WARNING = "warning"
    STATUS_DUE = "due"
    STATUS_OVERDUE = "overdue"
    STATUS_COMPLETED = "completed"
    STATUSES = {
        STATUS_PENDING,
        STATUS_WARNING,
        STATUS_DUE,
        STATUS_OVERDUE,
        STATUS_COMPLETED,
    }

    kyc_review_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    member = models.ForeignKey(
        "members.Member", on_delete=models.PROTECT, related_name="kyc_reviews"
    )
    kyc_profile = models.ForeignKey(
        "members.KycProfile", on_delete=models.PROTECT, related_name="compliance_reviews"
    )
    review_type = models.CharField(max_length=80, default=TYPE_REKYC, db_index=True)
    cycle_key = models.CharField(max_length=80)
    source_verified_at = models.DateTimeField()
    due_date = models.DateField(db_index=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    completion_verified_at = models.DateTimeField(blank=True, null=True)
    kyc_status_before = models.CharField(max_length=60)
    kyc_status_after = models.CharField(max_length=60, blank=True, null=True)
    reviewed_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="completed_kyc_reviews",
    )
    status = models.CharField(max_length=60, db_index=True)
    completeness_snapshot_json = models.JSONField(default=dict)
    completion_evidence_json = models.JSONField(default=list)
    task = models.OneToOneField(
        ComplianceTask, on_delete=models.PROTECT, related_name="kyc_review"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "kyc_reviews"
        ordering = ["due_date", "kyc_review_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["member", "cycle_key"], name="uniq_kyc_review_member_cycle"
            ),
            models.CheckConstraint(
                check=models.Q(review_type__in=("onboarding", "rekyc")),
                name="kyc_review_type_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(
                    status__in=("pending", "warning", "due", "overdue", "completed")
                ),
                name="kyc_review_status_bounded",
            ),
        ]
        indexes = [
            models.Index(fields=["status", "due_date"], name="idx_kyc_review_status_due"),
            models.Index(fields=["member", "due_date"], name="idx_kyc_review_member_due"),
        ]

    def save(self, *args, **kwargs):
        if self.pk:
            protected_fields = (
                "member_id",
                "kyc_profile_id",
                "review_type",
                "cycle_key",
                "source_verified_at",
                "due_date",
                "completed_at",
                "completion_verified_at",
                "kyc_status_before",
                "kyc_status_after",
                "reviewed_by_user_id",
                "status",
                "completeness_snapshot_json",
                "completion_evidence_json",
                "task_id",
            )
            previous = type(self).objects.filter(pk=self.pk).values(*protected_fields).first()
            if previous and any(
                previous[field] != getattr(self, field) for field in protected_fields
            ):
                raise ValueError("Retained KYC review facts are immutable.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Retained KYC reviews cannot be deleted.")


class MoneyLendingLawReview(models.Model):
    money_lending_law_review_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    financial_year = models.CharField(max_length=20, db_index=True)
    state = models.CharField(max_length=100, db_index=True)
    applicability = models.CharField(max_length=40)
    exemption_applicable_flag = models.BooleanField()
    legal_opinion_document = models.ForeignKey(
        "documents.DocumentFile", on_delete=models.PROTECT,
        related_name="money_lending_legal_opinions",
    )
    board_note_document = models.ForeignKey(
        "documents.DocumentFile", on_delete=models.PROTECT,
        related_name="money_lending_board_notes",
    )
    task = models.OneToOneField(
        ComplianceTask, on_delete=models.PROTECT, related_name="money_lending_review"
    )
    evidence = models.OneToOneField(
        ComplianceEvidence, on_delete=models.PROTECT, related_name="money_lending_review"
    )
    reviewed_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="money_lending_reviews"
    )
    reviewed_at = models.DateTimeField(default=timezone.now)
    remarks = models.TextField(blank=True)

    class Meta:
        db_table = "money_lending_law_reviews"
        constraints = [
            models.UniqueConstraint(
                fields=["financial_year", "state"], name="uniq_money_lending_year_state"
            ),
            models.CheckConstraint(
                check=models.Q(applicability__in=("applicable", "exempt")),
                name="money_lending_applicability_bounded",
            ),
        ]


class Section186Tracker(models.Model):
    FROZEN_FIELDS = (
        "financial_year",
        "quarter",
        "paid_up_capital_amount",
        "free_reserves_amount",
        "securities_premium_amount",
        "limit_60_percent_basis_amount",
        "limit_100_percent_basis_amount",
        "applicable_limit_amount",
        "total_loans_exposure_amount",
        "headroom_amount",
        "within_limit_flag",
        "special_resolution_required_flag",
        "task_id",
        "evidence_id",
        "prepared_by_user_id",
        "reviewer_user_id",
        "prepared_at",
        "input_snapshot_json",
        "result_snapshot_json",
        "reviewer_snapshot_json",
        "evidence_snapshot_json",
    )
    section_186_tracker_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    financial_year = models.CharField(max_length=20, db_index=True)
    quarter = models.CharField(max_length=10, db_index=True)
    paid_up_capital_amount = models.DecimalField(max_digits=18, decimal_places=2)
    free_reserves_amount = models.DecimalField(max_digits=18, decimal_places=2)
    securities_premium_amount = models.DecimalField(max_digits=18, decimal_places=2)
    limit_60_percent_basis_amount = models.DecimalField(max_digits=18, decimal_places=2)
    limit_100_percent_basis_amount = models.DecimalField(max_digits=18, decimal_places=2)
    applicable_limit_amount = models.DecimalField(max_digits=18, decimal_places=2)
    total_loans_exposure_amount = models.DecimalField(max_digits=18, decimal_places=2)
    headroom_amount = models.DecimalField(max_digits=18, decimal_places=2)
    within_limit_flag = models.BooleanField(db_index=True)
    special_resolution_required_flag = models.BooleanField()
    task = models.OneToOneField(
        ComplianceTask, on_delete=models.PROTECT, related_name="section_186_tracker"
    )
    evidence = models.ForeignKey(
        ComplianceEvidence, on_delete=models.PROTECT, related_name="section_186_trackers"
    )
    prepared_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="prepared_section_186_trackers"
    )
    reviewer_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="section_186_trackers_to_review"
    )
    prepared_at = models.DateTimeField(default=timezone.now)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    submitted_for_review_at = models.DateTimeField(blank=True, null=True)
    review_decision = models.CharField(max_length=40, blank=True)
    review_comments = models.TextField(blank=True)
    presented_to_board_flag = models.BooleanField(default=False)
    board_document = models.ForeignKey(
        "documents.DocumentFile", blank=True, null=True, on_delete=models.PROTECT,
        related_name="section_186_board_reviews",
    )
    board_evidence_snapshot_json = models.JSONField(default=dict)
    input_snapshot_json = models.JSONField()
    result_snapshot_json = models.JSONField()
    reviewer_snapshot_json = models.JSONField()
    evidence_snapshot_json = models.JSONField()

    class Meta:
        db_table = "section_186_trackers"
        ordering = ["financial_year", "quarter"]
        constraints = [
            models.UniqueConstraint(
                fields=["financial_year", "quarter"],
                name="uniq_section_186_period",
            ),
            models.CheckConstraint(
                check=models.Q(
                    review_decision__in=("", "accepted", "rejected")
                ),
                name="section_186_review_bounded",
            ),
            models.CheckConstraint(
                check=~models.Q(prepared_by_user=models.F("reviewer_user")),
                name="section_186_maker_checker",
            ),
        ]

    def save(self, *args, **kwargs):
        _reject_frozen_statutory_changes(self, self.FROZEN_FIELDS)
        _reject_final_review_changes(self)
        return super().save(*args, **kwargs)


class NbfcPrincipalBusinessTest(models.Model):
    FROZEN_FIELDS = (
        "financial_year",
        "quarter",
        "financial_assets_amount",
        "total_assets_amount",
        "financial_asset_ratio",
        "financial_income_amount",
        "gross_income_amount",
        "financial_income_ratio",
        "early_warning_threshold_ratio",
        "registration_triggered_flag",
        "one_ratio_above_statutory_flag",
        "early_warning_flag",
        "task_id",
        "evidence_id",
        "prepared_by_user_id",
        "reviewer_user_id",
        "prepared_at",
        "input_snapshot_json",
        "result_snapshot_json",
        "reviewer_snapshot_json",
        "evidence_snapshot_json",
    )
    nbfc_principal_test_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    financial_year = models.CharField(max_length=20, db_index=True)
    quarter = models.CharField(max_length=10, db_index=True)
    financial_assets_amount = models.DecimalField(max_digits=18, decimal_places=2)
    total_assets_amount = models.DecimalField(max_digits=18, decimal_places=2)
    financial_asset_ratio = models.DecimalField(max_digits=8, decimal_places=4)
    financial_income_amount = models.DecimalField(max_digits=18, decimal_places=2)
    gross_income_amount = models.DecimalField(max_digits=18, decimal_places=2)
    financial_income_ratio = models.DecimalField(max_digits=8, decimal_places=4)
    early_warning_threshold_ratio = models.DecimalField(max_digits=6, decimal_places=4)
    registration_triggered_flag = models.BooleanField(db_index=True)
    one_ratio_above_statutory_flag = models.BooleanField(default=False)
    early_warning_flag = models.BooleanField()
    presented_to_board_flag = models.BooleanField(default=False)
    task = models.OneToOneField(
        ComplianceTask, on_delete=models.PROTECT, related_name="nbfc_principal_test"
    )
    evidence = models.ForeignKey(
        ComplianceEvidence, on_delete=models.PROTECT, related_name="nbfc_principal_tests"
    )
    prepared_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="prepared_nbfc_principal_tests"
    )
    reviewer_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="nbfc_principal_tests_to_review"
    )
    prepared_at = models.DateTimeField(default=timezone.now)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    submitted_for_review_at = models.DateTimeField(blank=True, null=True)
    review_decision = models.CharField(max_length=40, blank=True)
    review_comments = models.TextField(blank=True)
    board_document = models.ForeignKey(
        "documents.DocumentFile", blank=True, null=True, on_delete=models.PROTECT,
        related_name="nbfc_board_reviews",
    )
    board_evidence_snapshot_json = models.JSONField(default=dict)
    input_snapshot_json = models.JSONField()
    result_snapshot_json = models.JSONField()
    reviewer_snapshot_json = models.JSONField()
    evidence_snapshot_json = models.JSONField()

    class Meta:
        db_table = "nbfc_principal_tests"
        ordering = ["financial_year", "quarter"]
        constraints = [
            models.UniqueConstraint(
                fields=["financial_year", "quarter"],
                name="uniq_nbfc_principal_period",
            ),
            models.CheckConstraint(
                check=models.Q(review_decision__in=("", "accepted", "rejected")),
                name="nbfc_principal_review_bounded",
            ),
            models.CheckConstraint(
                check=~models.Q(prepared_by_user=models.F("reviewer_user")),
                name="nbfc_principal_maker_checker",
            ),
        ]

    def save(self, *args, **kwargs):
        _reject_frozen_statutory_changes(self, self.FROZEN_FIELDS)
        _reject_final_review_changes(self)
        return super().save(*args, **kwargs)


class Grievance(models.Model):
    STATUS_OPEN = "open"
    STATUS_INVESTIGATING = "investigating"
    STATUS_ESCALATED = "escalated"
    STATUS_RESOLVED = "resolved"
    STATUSES = {
        STATUS_OPEN,
        STATUS_INVESTIGATING,
        STATUS_ESCALATED,
        STATUS_RESOLVED,
    }
    CATEGORIES = {
        "application_issue",
        "document_issue",
        "approval_delay",
        "disbursement_delay",
        "interest_charge_dispute",
        "repayment_adjustment_issue",
        "recovery_conduct_issue",
        "noc_closure_delay",
        "kyc_data_correction_issue",
        "other",
    }
    CHANNELS = {"portal", "form", "phone"}

    grievance_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    grievance_reference = models.CharField(max_length=40, unique=True)
    idempotency_key = models.CharField(max_length=255, unique=True)
    request_digest = models.CharField(max_length=64)
    member = models.ForeignKey(
        "members.Member", on_delete=models.PROTECT, related_name="grievances"
    )
    loan_account = models.ForeignKey(
        "loans.LoanAccount",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="grievances",
    )
    loan_application = models.ForeignKey(
        "applications.LoanApplication",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="grievances",
    )
    default_case = models.ForeignKey(
        "defaults.DefaultCase",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="grievances",
    )
    recovery_action = models.ForeignKey(
        "recovery.RecoveryAction",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="grievances",
    )
    grievance_category = models.CharField(max_length=100, db_index=True)
    description = models.TextField()
    received_date = models.DateField(db_index=True)
    received_channel = models.CharField(max_length=60)
    assigned_to_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="assigned_grievances",
    )
    resolution_due_date = models.DateField(db_index=True)
    status = models.CharField(max_length=60, default=STATUS_OPEN, db_index=True)
    internal_notes = models.TextField(blank=True)
    resolution_summary = models.TextField(blank=True)
    resolution_idempotency_key = models.CharField(
        max_length=255, blank=True, null=True, unique=True
    )
    resolution_request_digest = models.CharField(max_length=64, blank=True)
    resolution_document = models.ForeignKey(
        "documents.DocumentFile",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="resolved_grievances",
    )
    closed_at = models.DateTimeField(blank=True, null=True)
    resolved_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="resolved_grievances",
    )
    borrower_informed_at = models.DateTimeField(blank=True, null=True)
    borrower_acknowledged_at = models.DateTimeField(blank=True, null=True)
    borrower_acknowledgement = models.TextField(blank=True)
    notice_communication = models.OneToOneField(
        "communications.Communication",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="grievance_notice",
    )
    escalation_count = models.PositiveIntegerField(default=0)
    last_escalated_at = models.DateTimeField(blank=True, null=True)
    created_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="created_grievances",
    )
    created_by_role_code = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    supporting_documents = models.ManyToManyField(
        "documents.DocumentFile",
        through="GrievanceDocument",
        related_name="supporting_grievances",
    )

    class Meta:
        db_table = "grievances"
        ordering = ["-received_date", "-created_at", "-grievance_id"]
        indexes = [
            models.Index(
                fields=["member", "status"], name="idx_grievance_member_status"
            ),
            models.Index(
                fields=["assigned_to_user", "status"],
                name="idx_grievance_owner_status",
            ),
            models.Index(
                fields=["status", "resolution_due_date"],
                name="idx_grievance_status_due",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(status__in=("open", "investigating", "escalated", "resolved")),
                name="grievance_status_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(
                    grievance_category__in=(
                        "application_issue",
                        "document_issue",
                        "approval_delay",
                        "disbursement_delay",
                        "interest_charge_dispute",
                        "repayment_adjustment_issue",
                        "recovery_conduct_issue",
                        "noc_closure_delay",
                        "kyc_data_correction_issue",
                        "other",
                    )
                ),
                name="grievance_category_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(received_channel__in=("portal", "form", "phone")),
                name="grievance_channel_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(resolution_due_date__gte=models.F("received_date")),
                name="grievance_due_after_received",
            ),
            models.CheckConstraint(
                check=~models.Q(description=""),
                name="grievance_description_required",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(
                        status="resolved",
                        closed_at__isnull=False,
                        resolved_by_user__isnull=False,
                    )
                    & ~models.Q(resolution_summary="")
                )
                | (
                    ~models.Q(status="resolved")
                    & models.Q(
                        closed_at__isnull=True,
                        resolved_by_user__isnull=True,
                        resolution_summary="",
                    )
                ),
                name="grievance_resolution_complete",
            ),
        ]

    def delete(self, *args, **kwargs):
        raise ValueError("Grievance records cannot be deleted.")


class GrievanceDocument(models.Model):
    PURPOSE_SUPPORTING = "supporting"
    PURPOSE_RESOLUTION = "resolution"

    grievance_document_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    grievance = models.ForeignKey(
        Grievance, on_delete=models.PROTECT, related_name="document_links"
    )
    document = models.ForeignKey(
        "documents.DocumentFile",
        on_delete=models.PROTECT,
        related_name="grievance_links",
    )
    member = models.ForeignKey(
        "members.Member",
        on_delete=models.PROTECT,
        related_name="grievance_document_links",
    )
    purpose = models.CharField(max_length=40)
    linked_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="linked_grievance_documents",
    )
    linked_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "grievance_documents"
        constraints = [
            models.UniqueConstraint(
                fields=["grievance", "document", "purpose"],
                name="uniq_grievance_document_purpose",
            ),
            models.CheckConstraint(
                check=models.Q(purpose__in=("supporting", "resolution")),
                name="grievance_document_purpose_bounded",
            ),
        ]


class GrievanceHistory(models.Model):
    grievance_history_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    grievance = models.ForeignKey(
        Grievance, on_delete=models.PROTECT, related_name="history"
    )
    sequence = models.PositiveIntegerField()
    event_type = models.CharField(max_length=80)
    previous_status = models.CharField(max_length=60, blank=True)
    new_status = models.CharField(max_length=60)
    note = models.TextField(blank=True)
    actor_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="grievance_history_events",
    )
    actor_role_code = models.CharField(max_length=100)
    evidence_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "grievance_history"
        ordering = ["sequence", "grievance_history_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["grievance", "sequence"],
                name="uniq_grievance_history_sequence",
            ),
            models.CheckConstraint(
                check=models.Q(
                    new_status__in=("open", "investigating", "escalated", "resolved")
                ),
                name="grievance_history_status_bounded",
            ),
        ]


def _reject_frozen_statutory_changes(instance, frozen_fields):
    if not instance.pk:
        return
    previous = type(instance).objects.filter(pk=instance.pk).values(*frozen_fields).first()
    if previous is None:
        return
    if any(previous[field] != getattr(instance, field) for field in frozen_fields):
        raise ValueError("Retained statutory calculation facts are immutable.")


def _reject_final_review_changes(instance):
    if not instance.pk:
        return
    fields = (
        "submitted_for_review_at", "review_decision", "review_comments", "reviewed_at",
        "presented_to_board_flag", "board_document_id", "board_evidence_snapshot_json",
    )
    previous = type(instance).objects.filter(pk=instance.pk).values(*fields).first()
    if previous and previous["reviewed_at"] is not None:
        if any(previous[field] != getattr(instance, field) for field in fields):
            raise ValueError("Retained statutory final review is immutable.")
