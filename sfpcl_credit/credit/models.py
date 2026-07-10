import uuid

from django.db import models
from django.utils import timezone


class EligibilityAssessment(models.Model):
    CHECK_PENDING = "pending"
    MEMBER_ACTIVE_PASS = "pass"
    MEMBER_ACTIVE_FAIL = "fail"
    MEMBER_ACTIVE_RELAXATION = "relaxation"
    MEMBER_ACTIVE_MANUAL_EVIDENCE_REQUIRED = "manual_evidence_required"
    OVERALL_ELIGIBLE = "eligible"
    OVERALL_INELIGIBLE = "ineligible"
    OVERALL_PENDING_MANUAL_EVIDENCE = "pending_manual_evidence"
    OVERALL_PENDING = "pending"

    eligibility_assessment_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    loan_application = models.OneToOneField(
        "applications.LoanApplication",
        on_delete=models.PROTECT,
        related_name="eligibility_assessment",
    )
    member_active_check = models.CharField(max_length=60)
    default_check = models.CharField(max_length=60, default=CHECK_PENDING)
    document_check = models.CharField(max_length=60, default=CHECK_PENDING)
    terms_acceptance_check = models.CharField(max_length=60, default=CHECK_PENDING)
    purpose_check = models.CharField(max_length=60, default=CHECK_PENDING)
    nominee_check = models.CharField(max_length=60, default=CHECK_PENDING)
    overall_result = models.CharField(max_length=60, db_index=True)
    assessment_notes = models.TextField(blank=True)
    assessed_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="eligibility_assessments",
    )
    assessed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "eligibility_assessments"
        indexes = [
            models.Index(fields=["overall_result"], name="idx_eligibility_result"),
            models.Index(fields=["assessed_at"], name="idx_eligibility_assessed_at"),
        ]


class LoanLimitAssessment(models.Model):
    loan_limit_assessment_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    loan_application = models.OneToOneField(
        "applications.LoanApplication",
        on_delete=models.PROTECT,
        related_name="loan_limit_assessment",
    )
    member = models.ForeignKey(
        "members.Member",
        on_delete=models.PROTECT,
        related_name="loan_limit_assessments",
    )
    shareholding = models.ForeignKey(
        "members.Shareholding",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="loan_limit_assessments",
    )
    number_of_shares = models.IntegerField()
    valuation_per_share = models.DecimalField(max_digits=18, decimal_places=2)
    share_limit_percentage = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        blank=True,
        null=True,
    )
    per_share_cap_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        null=True,
    )
    shareholding_based_limit_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
    )
    land_area_acres = models.DecimalField(max_digits=12, decimal_places=2)
    scale_of_finance_per_acre_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
    )
    land_based_limit_amount = models.DecimalField(max_digits=18, decimal_places=2)
    final_eligible_loan_amount = models.DecimalField(max_digits=18, decimal_places=2)
    requested_amount = models.DecimalField(max_digits=18, decimal_places=2)
    amount_within_limit_flag = models.BooleanField(db_index=True)
    exception_required_flag = models.BooleanField(db_index=True)
    calculation_rule_version = models.CharField(max_length=80)
    policy_config_id_snapshot = models.UUIDField(blank=True, null=True)
    policy_name_snapshot = models.CharField(max_length=255, blank=True)
    board_approval_reference_snapshot = models.CharField(max_length=255, blank=True)
    calculated_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="loan_limit_assessments",
    )
    calculated_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = "loan_limit_assessments"


class RiskAssessment(models.Model):
    risk_assessment_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    loan_application = models.OneToOneField(
        "applications.LoanApplication",
        on_delete=models.PROTECT,
        related_name="risk_assessment",
    )
    market_risk_rating = models.CharField(max_length=60)
    operational_risk_rating = models.CharField(max_length=60)
    borrower_risk_rating = models.CharField(max_length=60)
    overall_risk_rating = models.CharField(max_length=60, db_index=True)
    risk_mitigation_notes = models.TextField(blank=True)
    assessed_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="risk_assessments",
    )
    assessed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "risk_assessments"
        indexes = [
            models.Index(fields=["loan_application"], name="idx_risk_app"),
            models.Index(fields=["overall_risk_rating"], name="idx_risk_overall"),
        ]


class LoanAppraisalNote(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_REVIEW_PENDING = "review_pending"
    TAT_WITHIN = "within_tat"
    TAT_BREACHED = "breached"

    loan_appraisal_note_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    loan_application = models.OneToOneField(
        "applications.LoanApplication",
        on_delete=models.PROTECT,
        related_name="appraisal_note",
    )
    prepared_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="prepared_appraisal_notes",
    )
    reviewed_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="reviewed_appraisal_notes",
    )
    prepared_at = models.DateTimeField(default=timezone.now)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    tat_due_at = models.DateTimeField(db_index=True)
    tat_status = models.CharField(max_length=60, db_index=True)
    eligibility_assessment_id_snapshot = models.UUIDField()
    loan_limit_assessment_id_snapshot = models.UUIDField()
    eligibility_snapshot_json = models.JSONField(default=dict)
    loan_limit_snapshot_json = models.JSONField(default=dict)
    prerequisite_provenance = models.CharField(
        max_length=60,
        default="legacy_unverified",
        db_index=True,
    )
    borrower_summary = models.TextField()
    eligibility_summary = models.TextField()
    loan_limit_summary = models.TextField()
    recommended_amount = models.DecimalField(max_digits=18, decimal_places=2)
    recommended_tenure_months = models.PositiveIntegerField(blank=True, null=True)
    recommended_interest_type = models.CharField(max_length=60, blank=True)
    recommended_security_summary = models.TextField()
    repayment_capacity_notes = models.TextField()
    submission_remarks = models.TextField(blank=True)
    risk_assessment = models.OneToOneField(
        RiskAssessment,
        on_delete=models.PROTECT,
        related_name="appraisal_note",
    )
    recommendation = models.CharField(max_length=60, db_index=True)
    appraisal_status = models.CharField(max_length=60, default=STATUS_DRAFT, db_index=True)

    class Meta:
        db_table = "loan_appraisal_notes"
        indexes = [
            models.Index(fields=["tat_status", "tat_due_at"], name="idx_appraisal_tat"),
            models.Index(fields=["recommendation"], name="idx_appraisal_recommend"),
            models.Index(fields=["appraisal_status"], name="idx_appraisal_status"),
        ]
