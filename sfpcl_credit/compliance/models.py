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
