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
