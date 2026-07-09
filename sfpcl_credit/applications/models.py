import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class LoanApplication(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_SUBMITTED = "submitted"
    STAGE_INITIAL = "initial_loan_request"
    COMPLETENESS_NOT_STARTED = "not_started"

    loan_application_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_reference_number = models.CharField(
        max_length=40, blank=True, null=True, unique=True
    )
    member = models.ForeignKey(
        "members.Member", on_delete=models.PROTECT, related_name="loan_applications"
    )
    borrower_type = models.CharField(max_length=60, db_index=True)
    application_channel = models.CharField(max_length=60, default="assisted_digital")
    application_date = models.DateField(default=timezone.localdate, db_index=True)
    received_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="received_loan_applications",
    )
    required_loan_amount = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    requested_tenure_months = models.PositiveIntegerField(blank=True, null=True)
    declared_purpose = models.TextField(blank=True)
    purpose_category = models.CharField(max_length=80, blank=True, db_index=True)
    loan_type_requested = models.CharField(max_length=60, blank=True)
    land_holding = models.ForeignKey(
        "members.LandHolding",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="loan_applications",
    )
    crop_plan = models.ForeignKey(
        "members.CropPlan",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="loan_applications",
    )
    bank_account = models.ForeignKey(
        "members.BankAccount",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="loan_applications",
    )
    cancelled_cheque = models.ForeignKey(
        "members.CancelledCheque",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="loan_applications",
    )
    borrower_request_notes = models.TextField(blank=True)
    current_stage = models.CharField(max_length=80, default=STAGE_INITIAL, db_index=True)
    application_status = models.CharField(max_length=80, default=STATUS_DRAFT, db_index=True)
    completeness_status = models.CharField(
        max_length=60, default=COMPLETENESS_NOT_STARTED, db_index=True
    )
    terms_acceptance_flag = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(blank=True, null=True)
    submitted_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="submitted_loan_applications",
    )
    created_at = models.DateTimeField(default=timezone.now)
    created_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="created_loan_applications",
    )
    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="updated_loan_applications",
    )

    class Meta:
        db_table = "loan_applications"
        indexes = [
            models.Index(fields=["application_status", "current_stage"], name="idx_loan_apps_status_stage"),
            models.Index(fields=["member"], name="idx_loan_apps_member"),
            models.Index(fields=["application_date"], name="idx_loan_apps_app_date"),
            models.Index(fields=["application_reference_number"], name="idx_loan_apps_reference"),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(required_loan_amount__isnull=True)
                    | models.Q(required_loan_amount__gt=0)
                ),
                name="loan_apps_positive_required_amount",
            ),
        ]

    def clean(self):
        super().clean()
        if self.required_loan_amount is not None and self.required_loan_amount <= 0:
            raise ValidationError(
                {"required_loan_amount": "Requested amount must be greater than zero."}
            )
        if self.application_status not in {self.STATUS_DRAFT, self.STATUS_SUBMITTED}:
            raise ValidationError({"application_status": "Unsupported application status."})
        if self.current_stage != self.STAGE_INITIAL:
            raise ValidationError({"current_stage": "Only initial loan request stage is supported."})
        if self.application_status == self.STATUS_SUBMITTED and self.submitted_at is None:
            raise ValidationError({"submitted_at": "Submitted applications require submitted_at."})

    def save(self, *args, **kwargs):
        if self.member_id and not self.borrower_type:
            self.borrower_type = self.member.member_type
        self.full_clean()
        return super().save(*args, **kwargs)
