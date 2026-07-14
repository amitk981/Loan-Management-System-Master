import uuid

from django.db import models
from django.utils import timezone


class LoanDocument(models.Model):
    GENERATION_GENERATED = "generated"
    EXECUTION_PENDING = "pending"
    VERIFICATION_PENDING = "pending"

    loan_document_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    loan_application = models.ForeignKey(
        "applications.LoanApplication",
        on_delete=models.PROTECT,
        related_name="loan_documents",
    )
    loan_account_id = models.UUIDField(blank=True, null=True, db_index=True)
    document_type = models.CharField(max_length=100, db_index=True)
    document_category = models.CharField(max_length=80, db_index=True)
    party_required = models.CharField(max_length=80, blank=True, null=True)
    document_template = models.ForeignKey(
        "documents.DocumentTemplate",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="loan_documents",
    )
    document = models.ForeignKey(
        "documents.DocumentFile",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="generated_loan_documents",
    )
    output_format = models.CharField(max_length=20)
    generation_status = models.CharField(max_length=60, db_index=True)
    execution_status = models.CharField(max_length=60, db_index=True)
    verification_status = models.CharField(max_length=60, db_index=True)
    stamp_status = models.CharField(max_length=60, blank=True, null=True, db_index=True)
    notarisation_status = models.CharField(
        max_length=60, blank=True, null=True, db_index=True
    )
    custody_location = models.CharField(max_length=255, blank=True, null=True)
    retention_until_date = models.DateField(blank=True, null=True)
    verified_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="verified_loan_documents",
    )
    verified_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "loan_documents"
        ordering = ["-created_at", "-loan_document_id"]
        indexes = [
            models.Index(
                fields=["loan_application", "document_type"],
                name="idx_loan_doc_app_type",
            ),
            models.Index(
                fields=["document_category", "generation_status"],
                name="idx_loan_doc_cat_gen",
            ),
            models.Index(
                fields=["execution_status", "verification_status"],
                name="idx_loan_doc_exec_verify",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["loan_application", "document_template", "output_format"],
                name="unique_loan_doc_generation_replay",
            ),
            models.CheckConstraint(
                check=models.Q(loan_account_id__isnull=True),
                name="loan_document_account_requires_epic_009",
            ),
        ]


class DocumentChecklist(models.Model):
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_CS_APPROVED = "cs_approved"
    STATUS_READY = "ready"
    STATUSES = {STATUS_IN_PROGRESS, STATUS_CS_APPROVED, STATUS_READY}

    document_checklist_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    loan_application = models.OneToOneField(
        "applications.LoanApplication",
        on_delete=models.PROTECT,
        related_name="legal_document_checklist",
    )
    loan_account_id = models.UUIDField(blank=True, null=True)
    checklist_status = models.CharField(
        max_length=80, default=STATUS_IN_PROGRESS, db_index=True
    )
    company_secretary_signature_id = models.UUIDField(blank=True, null=True)
    credit_manager_signature_id = models.UUIDField(blank=True, null=True)
    sanction_committee_signature_id = models.UUIDField(blank=True, null=True)
    senior_manager_finance_signature_id = models.UUIDField(blank=True, null=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "document_checklists"
        ordering = ["created_at", "document_checklist_id"]
        indexes = [
            models.Index(
                fields=["loan_application", "checklist_status"],
                name="idx_doc_check_app_status",
            )
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(
                    checklist_status__in=["in_progress", "cs_approved", "ready"]
                ),
                name="document_checklist_valid_status",
            ),
            models.CheckConstraint(
                check=models.Q(loan_account_id__isnull=True),
                name="checklist_account_requires_epic_009",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(company_secretary_signature_id__isnull=True)
                    & models.Q(credit_manager_signature_id__isnull=True)
                    & models.Q(sanction_committee_signature_id__isnull=True)
                    & models.Q(senior_manager_finance_signature_id__isnull=True)
                ),
                name="checklist_signatures_require_008k",
            ),
        ]

    def clean(self):
        super().clean()
        if self.checklist_status not in self.STATUSES:
            from django.core.exceptions import ValidationError

            raise ValidationError({"checklist_status": "Unsupported checklist status."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class ChecklistItem(models.Model):
    STATUS_PENDING = "pending"
    STATUS_COMPLETE = "complete"
    STATUS_NOT_APPLICABLE = "not_applicable"
    STATUSES = {STATUS_PENDING, STATUS_COMPLETE, STATUS_NOT_APPLICABLE}
    ITEM_CODES = (
        "witness_pan_aadhaar",
        "cancelled_cheque",
        "blank_dated_cheque",
        "poa",
        "tri_party_agreement",
        "sh4",
        "cdsl_pledge",
        "term_sheet",
        "loan_agreement",
        "bank_verification_letter",
        "final_checklist",
    )

    checklist_item_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    document_checklist = models.ForeignKey(
        DocumentChecklist,
        on_delete=models.PROTECT,
        related_name="items",
    )
    loan_document = models.ForeignKey(
        LoanDocument,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="checklist_items",
    )
    item_code = models.CharField(max_length=120)
    item_label = models.CharField(max_length=255)
    display_order = models.PositiveSmallIntegerField()
    required_flag = models.BooleanField()
    applicable_flag = models.BooleanField()
    completion_status = models.CharField(max_length=60, db_index=True)
    applicability_source = models.CharField(max_length=160)
    applicability_blocker = models.CharField(max_length=160, blank=True, null=True)
    verified_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="verified_checklist_items",
    )
    verified_at = models.DateTimeField(blank=True, null=True)
    remarks = models.TextField(blank=True)

    class Meta:
        db_table = "checklist_items"
        ordering = ["display_order", "checklist_item_id"]
        indexes = [
            models.Index(
                fields=["document_checklist", "completion_status"],
                name="idx_check_item_list_status",
            )
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["document_checklist", "item_code"],
                name="unique_checklist_item_code",
            ),
            models.UniqueConstraint(
                fields=["document_checklist", "display_order"],
                name="unique_checklist_item_order",
            ),
            models.CheckConstraint(
                check=models.Q(
                    item_code__in=[
                        "witness_pan_aadhaar",
                        "cancelled_cheque",
                        "blank_dated_cheque",
                        "poa",
                        "tri_party_agreement",
                        "sh4",
                        "cdsl_pledge",
                        "term_sheet",
                        "loan_agreement",
                        "bank_verification_letter",
                        "final_checklist",
                    ]
                ),
                name="checklist_item_valid_code",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(
                        required_flag=True,
                        applicable_flag=True,
                        completion_status__in=["pending", "complete"],
                        applicability_blocker__isnull=True,
                    )
                    | models.Q(
                        required_flag=False,
                        applicable_flag=False,
                        completion_status="not_applicable",
                    )
                ),
                name="checklist_item_consistent_state",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(completion_status="complete")
                    | (
                        models.Q(verified_by_user__isnull=True)
                        & models.Q(verified_at__isnull=True)
                    )
                ),
                name="checklist_item_pending_unverified",
            ),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError

        super().clean()
        errors = {}
        if self.item_code not in self.ITEM_CODES:
            errors["item_code"] = "Unsupported checklist item code."
        if self.completion_status not in self.STATUSES:
            errors["completion_status"] = "Unsupported completion status."
        applicable_state = (
            self.required_flag
            and self.applicable_flag
            and self.completion_status in {self.STATUS_PENDING, self.STATUS_COMPLETE}
            and not self.applicability_blocker
        )
        inapplicable_state = (
            not self.required_flag
            and not self.applicable_flag
            and self.completion_status == self.STATUS_NOT_APPLICABLE
        )
        if not (applicable_state or inapplicable_state):
            errors["applicable_flag"] = "Checklist applicability state is inconsistent."
        if self.completion_status != self.STATUS_COMPLETE and (
            self.verified_by_user_id is not None or self.verified_at is not None
        ):
            errors["completion_status"] = "Pending items cannot carry verification facts."
        if (
            self.loan_document_id
            and self.document_checklist_id
            and self.loan_document.loan_application_id
            != self.document_checklist.loan_application_id
        ):
            errors["loan_document"] = "Loan document must belong to the checklist application."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
