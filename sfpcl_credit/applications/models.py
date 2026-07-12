import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class LoanApplication(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_SUBMITTED = "submitted"
    STATUS_INCOMPLETE_RETURNED = "incomplete_returned"
    STATUS_REFERENCE_GENERATED = "reference_generated"
    STATUS_SUBMITTED_TO_SANCTION = "submitted_to_sanction_committee"
    STAGE_INITIAL = "initial_loan_request"
    STAGE_CREDIT_ASSESSMENT = "credit_assessment"
    COMPLETENESS_NOT_STARTED = "not_started"
    COMPLETENESS_INCOMPLETE = "incomplete"
    COMPLETENESS_COMPLETE = "complete"

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
    nominee = models.ForeignKey(
        "members.Nominee",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="selected_for_loan_applications",
    )
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
        if self.application_status not in {
            self.STATUS_DRAFT,
            self.STATUS_SUBMITTED,
            self.STATUS_INCOMPLETE_RETURNED,
            self.STATUS_REFERENCE_GENERATED,
            self.STATUS_SUBMITTED_TO_SANCTION,
        }:
            raise ValidationError({"application_status": "Unsupported application status."})
        if self.current_stage not in {self.STAGE_INITIAL, self.STAGE_CREDIT_ASSESSMENT}:
            raise ValidationError({"current_stage": "Unsupported current stage."})
        if self.application_status == self.STATUS_SUBMITTED and self.submitted_at is None:
            raise ValidationError({"submitted_at": "Submitted applications require submitted_at."})
        if self.application_status == self.STATUS_REFERENCE_GENERATED:
            if self.application_reference_number is None:
                raise ValidationError(
                    {
                        "application_reference_number": (
                            "Reference generated applications require a reference number."
                        )
                    }
                )
            if self.current_stage != self.STAGE_CREDIT_ASSESSMENT:
                raise ValidationError(
                    {"current_stage": "Reference generated applications move to credit assessment."}
                )
            if self.completeness_status != self.COMPLETENESS_COMPLETE:
                raise ValidationError(
                    {"completeness_status": "Reference generation requires complete status."}
                )

    def save(self, *args, **kwargs):
        if self.member_id and not self.borrower_type:
            self.borrower_type = self.member.member_type
        self.full_clean()
        return super().save(*args, **kwargs)


class Witness(models.Model):
    VERIFICATION_STATUSES = {"pending", "verified", "rejected"}

    witness_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan_application = models.ForeignKey(
        LoanApplication,
        on_delete=models.PROTECT,
        related_name="witnesses",
        db_index=False,
    )
    member = models.ForeignKey(
        "members.Member",
        on_delete=models.PROTECT,
        related_name="application_witnesses",
    )
    witness_name = models.CharField(max_length=255)
    address = models.CharField(max_length=500, blank=True, default="")
    mobile = models.CharField(max_length=20, blank=True, default="")
    pan_encrypted = models.TextField()
    pan_hash = models.CharField(max_length=128)
    aadhaar_encrypted = models.TextField()
    aadhaar_hash = models.CharField(max_length=128)
    verification_shareholding = models.ForeignKey(
        "members.Shareholding",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="verified_witnesses",
    )
    verification_folio_number = models.CharField(max_length=100, blank=True, null=True)
    shareholder_verified_flag = models.BooleanField(default=False)
    verification_status = models.CharField(max_length=60, default="pending", db_index=True)
    verified_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="verified_witnesses",
    )
    verified_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by_user = models.ForeignKey(
        "identity.User", blank=True, null=True, on_delete=models.PROTECT,
        related_name="updated_witnesses",
    )
    version = models.PositiveIntegerField(default=1, db_default=1)

    class Meta:
        db_table = "witnesses"
        indexes = [
            models.Index(fields=["loan_application"], name="idx_witnesses_application"),
            models.Index(fields=["pan_hash"], name="idx_witnesses_pan_hash"),
            models.Index(fields=["aadhaar_hash"], name="idx_witnesses_aadhaar_hash"),
        ]

    def clean(self):
        super().clean()
        if self.verification_status not in self.VERIFICATION_STATUSES:
            raise ValidationError({"verification_status": "Unsupported verification status."})
        if self.shareholder_verified_flag and self.verification_status != "verified":
            raise ValidationError(
                {"verification_status": "Verified shareholders require verified status."}
            )
        if self.verification_status == "verified" and (
            not self.shareholder_verified_flag
            or self.verified_by_user_id is None
            or self.verified_at is None
        ):
            raise ValidationError(
                {"verification_status": "Verified status requires complete verification metadata."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class WitnessChangeHistory(models.Model):
    witness_change_history_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    witness = models.ForeignKey(Witness, on_delete=models.PROTECT, related_name="change_history")
    actor_user = models.ForeignKey("identity.User", on_delete=models.PROTECT, related_name="witness_changes")
    witness_version = models.PositiveIntegerField()
    changed_fields = models.JSONField(default=list)
    old_value_json = models.JSONField(default=dict)
    new_value_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "witness_change_history"
        ordering = ["created_at", "witness_change_history_id"]


class SystemSequence(models.Model):
    system_sequence_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sequence_code = models.CharField(max_length=80, unique=True)
    prefix = models.CharField(max_length=20)
    current_value = models.BigIntegerField(default=0)
    padding_length = models.PositiveIntegerField(default=8)
    last_generated_value = models.CharField(max_length=80, blank=True, null=True)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "system_sequences"

    def next_value(self):
        self.current_value += 1
        self.last_generated_value = f"{self.prefix}{self.current_value:0{self.padding_length}d}"
        self.updated_at = timezone.now()
        self.save(update_fields=["current_value", "last_generated_value", "updated_at"])
        return self.last_generated_value


class LoanRequestRegisterEntry(models.Model):
    STATUS_REFERENCE_GENERATED = "reference_generated"

    loan_request_register_entry_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    loan_application = models.OneToOneField(
        LoanApplication,
        on_delete=models.PROTECT,
        related_name="loan_request_register_entry",
    )
    application_reference_number = models.CharField(max_length=40, db_index=True)
    member = models.ForeignKey(
        "members.Member",
        on_delete=models.PROTECT,
        related_name="loan_request_register_entries",
    )
    date_received = models.DateField(db_index=True)
    reference_generated_date = models.DateField(db_index=True)
    received_channel = models.CharField(max_length=60)
    received_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="received_loan_request_register_entries",
    )
    register_status = models.CharField(
        max_length=60,
        default=STATUS_REFERENCE_GENERATED,
        db_index=True,
    )
    requested_amount = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    declared_purpose = models.TextField(blank=True)
    purpose_category = models.CharField(max_length=80, blank=True, db_index=True)
    borrower_name = models.CharField(max_length=255, blank=True)
    folio_number = models.CharField(max_length=120, blank=True)
    member_type = models.CharField(max_length=60, blank=True)
    current_stage = models.CharField(max_length=80, blank=True, db_index=True)
    current_owner_role = models.CharField(max_length=120, blank=True)
    eligibility_status = models.CharField(max_length=60, default="pending", db_index=True)
    sanction_status = models.CharField(max_length=60, default="pending", db_index=True)
    documentation_status = models.CharField(max_length=60, default="pending", db_index=True)
    disbursement_status = models.CharField(max_length=60, default="pending", db_index=True)
    original_copy_reference = models.CharField(max_length=255, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "loan_request_register_entries"
        indexes = [
            models.Index(
                fields=["register_status", "current_stage"],
                name="idx_lrr_status_stage",
            ),
            models.Index(fields=["date_received"], name="idx_lrr_date_received"),
            models.Index(
                fields=["reference_generated_date"],
                name="idx_lrr_ref_gen_date",
            ),
        ]


class ApplicationDocument(models.Model):
    SUBMISSION_PENDING = "pending"
    SUBMISSION_SUBMITTED = "submitted"
    VERIFICATION_PENDING = "pending"
    VERIFICATION_VERIFIED = "verified"
    VERIFICATION_REJECTED = "rejected"
    PARTY_TYPES = {"borrower", "nominee", "witness"}

    application_document_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    loan_application = models.ForeignKey(
        LoanApplication,
        on_delete=models.PROTECT,
        related_name="application_documents",
    )
    document_type = models.CharField(max_length=80, db_index=True)
    party_type = models.CharField(max_length=40, db_index=True)
    party_id = models.UUIDField(blank=True, null=True, db_index=True)
    document_file = models.ForeignKey(
        "documents.DocumentFile",
        on_delete=models.PROTECT,
        related_name="application_documents",
    )
    required_flag = models.BooleanField(default=True)
    submission_status = models.CharField(
        max_length=40,
        default=SUBMISSION_SUBMITTED,
        db_index=True,
    )
    verification_status = models.CharField(
        max_length=40,
        default=VERIFICATION_PENDING,
        db_index=True,
    )
    verified_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="verified_application_documents",
    )
    verified_at = models.DateTimeField(blank=True, null=True)
    remarks = models.TextField(blank=True)
    version_number = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)
    created_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="created_application_documents",
    )
    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="updated_application_documents",
    )

    class Meta:
        db_table = "application_documents"
        ordering = [
            "loan_application_id",
            "document_type",
            "party_type",
            "party_id",
            "version_number",
        ]
        indexes = [
            models.Index(
                fields=["loan_application", "document_type"],
                name="idx_app_docs_app_type",
            ),
            models.Index(
                fields=["loan_application", "submission_status", "verification_status"],
                name="idx_app_docs_statuses",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "loan_application",
                    "document_type",
                    "party_type",
                    "party_id",
                    "version_number",
                ],
                name="unique_app_doc_party_version",
            ),
        ]

    def clean(self):
        super().clean()
        errors = {}
        if self.party_type not in self.PARTY_TYPES:
            errors["party_type"] = "Unsupported party type."
        if self.submission_status not in {
            self.SUBMISSION_PENDING,
            self.SUBMISSION_SUBMITTED,
        }:
            errors["submission_status"] = "Unsupported submission status."
        if self.verification_status not in {
            self.VERIFICATION_PENDING,
            self.VERIFICATION_VERIFIED,
            self.VERIFICATION_REJECTED,
        }:
            errors["verification_status"] = "Unsupported verification status."
        if self.verification_status in {
            self.VERIFICATION_VERIFIED,
            self.VERIFICATION_REJECTED,
        } and (self.verified_by_user_id is None or self.verified_at is None):
            errors["verified_by_user"] = "Verified or rejected documents require verifier facts."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class ApplicationDeficiency(models.Model):
    TYPE_MISSING_DOCUMENT = "missing_document"
    TYPE_NOT_VERIFIED = "not_verified"
    STATUS_OPEN = "open"
    STATUS_RESOLVED = "resolved"
    STATUS_REJECTED = "rejected"

    deficiency_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan_application = models.ForeignKey(
        LoanApplication,
        on_delete=models.PROTECT,
        related_name="deficiencies",
    )
    item_code = models.CharField(max_length=100, db_index=True)
    deficiency_type = models.CharField(max_length=100, db_index=True)
    source_reason_code = models.CharField(max_length=80, db_index=True)
    description = models.TextField()
    remarks = models.TextField(blank=True)
    resolution_status = models.CharField(max_length=60, default=STATUS_OPEN, db_index=True)
    raised_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="raised_application_deficiencies",
    )
    raised_at = models.DateTimeField(default=timezone.now, db_index=True)
    resolved_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="resolved_application_deficiencies",
    )
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolution_notes = models.TextField(blank=True)
    communication_mode = models.CharField(max_length=40, blank=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "deficiencies"
        ordering = ["loan_application_id", "item_code", "raised_at", "deficiency_id"]
        indexes = [
            models.Index(
                fields=["loan_application", "resolution_status"],
                name="idx_def_app_status",
            ),
            models.Index(fields=["loan_application", "item_code"], name="idx_def_app_item"),
        ]

    def clean(self):
        super().clean()
        errors = {}
        if self.deficiency_type not in {self.TYPE_MISSING_DOCUMENT, self.TYPE_NOT_VERIFIED}:
            errors["deficiency_type"] = "Unsupported deficiency type."
        if self.resolution_status not in {
            self.STATUS_OPEN,
            self.STATUS_RESOLVED,
            self.STATUS_REJECTED,
        }:
            errors["resolution_status"] = "Unsupported resolution status."
        if self.resolution_status == self.STATUS_RESOLVED and (
            self.resolved_by_user_id is None or self.resolved_at is None
        ):
            errors["resolved_by_user"] = "Resolved deficiencies require resolver facts."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class RejectionNote(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_SENT = "sent"
    REJECTION_STAGES = {"completeness", "credit_assessment", "sanction_committee"}
    REASON_CATEGORIES = {
        "missing_document",
        "eligibility",
        "default",
        "purpose_mismatch",
        "limit_issue",
        "committee_rejection",
        "other",
    }
    COMMUNICATION_MODES = {"email", "courier", "hard_copy", "sms_summary"}

    rejection_note_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan_application = models.OneToOneField(
        LoanApplication,
        on_delete=models.PROTECT,
        related_name="rejection_note",
    )
    rejection_stage = models.CharField(max_length=80, db_index=True)
    rejection_reason_category = models.CharField(max_length=100, db_index=True)
    detailed_reason = models.TextField()
    reapply_allowed_flag = models.BooleanField(default=True)
    note_status = models.CharField(max_length=40, default=STATUS_DRAFT, db_index=True)
    prepared_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="prepared_rejection_notes",
    )
    approved_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="approved_rejection_notes",
    )
    communication_mode = models.CharField(max_length=60)
    communication_id = models.UUIDField(blank=True, null=True)
    sent_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="sent_rejection_notes",
    )
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(blank=True, null=True)
    updated_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="updated_rejection_notes",
    )

    class Meta:
        db_table = "rejection_notes"
        ordering = ["loan_application_id", "created_at", "rejection_note_id"]
        indexes = [
            models.Index(
                fields=["loan_application", "note_status"],
                name="idx_rej_note_app_status",
            ),
            models.Index(fields=["rejection_stage"], name="idx_rej_note_stage"),
            models.Index(fields=["rejection_reason_category"], name="idx_rej_note_reason"),
        ]

    def clean(self):
        super().clean()
        errors = {}
        if self.rejection_stage not in self.REJECTION_STAGES:
            errors["rejection_stage"] = "Unsupported rejection stage."
        if self.rejection_reason_category not in self.REASON_CATEGORIES:
            errors["rejection_reason_category"] = "Unsupported rejection reason category."
        if not self.detailed_reason.strip():
            errors["detailed_reason"] = "This field is required."
        if self.communication_mode not in self.COMMUNICATION_MODES:
            errors["communication_mode"] = "Unsupported communication mode."
        if self.note_status not in {self.STATUS_DRAFT, self.STATUS_SENT}:
            errors["note_status"] = "Unsupported rejection note status."
        if self.note_status == self.STATUS_SENT and (
            self.sent_by_user_id is None or self.sent_at is None
        ):
            errors["sent_by_user"] = "Sent rejection notes require sender facts."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
