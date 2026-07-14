import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


_RENDERER_PROVENANCE_FIELDS = frozenset(
    {
        "renderer_contract_version",
        "renderer_validated_document_id",
        "renderer_validated_checksum_sha256",
    }
)


class LoanDocumentQuerySet(models.QuerySet):
    def update(self, **kwargs):
        if _RENDERER_PROVENANCE_FIELDS.intersection(kwargs):
            raise ValidationError(
                {"renderer_provenance": "Renderer provenance is immutable."}
            )
        return super().update(**kwargs)

    def bulk_update(self, objs, fields, batch_size=None):
        if _RENDERER_PROVENANCE_FIELDS.intersection(fields):
            raise ValidationError(
                {"renderer_provenance": "Renderer provenance is immutable."}
            )
        return super().bulk_update(objs, fields, batch_size=batch_size)


class LoanDocument(models.Model):
    GENERATION_GENERATED = "generated"
    EXECUTION_PENDING = "pending"
    VERIFICATION_PENDING = "pending"
    RENDERER_CONTRACT_V1 = "legal-renderer-v1"
    RENDERER_CURRENT_VALIDATED = "current_validated"
    RENDERER_LEGACY_UNVERIFIED = "legacy_unverified"
    objects = LoanDocumentQuerySet.as_manager()

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
    renderer_contract_version = models.CharField(max_length=64, blank=True, null=True)
    renderer_validated_document_id = models.UUIDField(blank=True, null=True)
    renderer_validated_checksum_sha256 = models.CharField(
        max_length=128, blank=True, null=True
    )
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
    verification_remarks = models.TextField(blank=True, null=True)
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
            models.CheckConstraint(
                check=(
                    models.Q(
                        renderer_contract_version__isnull=True,
                        renderer_validated_document_id__isnull=True,
                        renderer_validated_checksum_sha256__isnull=True,
                    )
                    | models.Q(
                        renderer_contract_version__isnull=False,
                        renderer_validated_document_id__isnull=False,
                        renderer_validated_checksum_sha256__isnull=False,
                    )
                ),
                name="loan_document_renderer_provenance_complete",
            ),
        ]

    @property
    def renderer_validation_status(self):
        if (
            self.renderer_contract_version == self.RENDERER_CONTRACT_V1
            and self.renderer_validated_document_id == self.document_id
            and self.renderer_validated_checksum_sha256
            and self.document_id
            and self.document.checksum_sha256 == self.renderer_validated_checksum_sha256
        ):
            return self.RENDERER_CURRENT_VALIDATED
        return self.RENDERER_LEGACY_UNVERIFIED

    def save(self, *args, **kwargs):
        if not self._state.adding:
            update_fields = kwargs.get("update_fields")
            if update_fields is None or set(update_fields).intersection(
                _RENDERER_PROVENANCE_FIELDS
            ):
                retained = (
                    type(self)
                    .objects.filter(pk=self.pk)
                    .values(*_RENDERER_PROVENANCE_FIELDS)
                    .first()
                )
                if retained is not None and any(
                    retained[field] != getattr(self, field)
                    for field in _RENDERER_PROVENANCE_FIELDS
                ):
                    raise ValidationError(
                        {"renderer_provenance": "Renderer provenance is immutable."}
                    )
        return super().save(*args, **kwargs)


class StampDutyRecord(models.Model):
    STATUSES = {"pending", "adequate", "insufficient"}
    TYPES = {"physical", "electronic"}

    stamp_duty_record_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    loan_document = models.OneToOneField(
        LoanDocument, on_delete=models.PROTECT, related_name="stamp_duty_record"
    )
    stamp_paper_amount = models.DecimalField(max_digits=18, decimal_places=2)
    stamp_type = models.CharField(max_length=60)
    stamp_number = models.CharField(
        max_length=120, blank=True, null=True, db_index=True
    )
    stamp_purchase_date = models.DateField(blank=True, null=True)
    executed_date = models.DateField(blank=True, null=True)
    prepared_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="prepared_stamp_duty_records",
    )
    legacy_maker_attribution = models.BooleanField(default=False)
    verified_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="verified_stamp_duty_records",
    )
    status = models.CharField(max_length=60, db_index=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "stamp_duty_records"
        constraints = [
            models.CheckConstraint(
                check=models.Q(stamp_paper_amount__gte=0),
                name="stamp_amount_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(stamp_type__in=["physical", "electronic"]),
                name="stamp_type_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(status__in=["pending", "adequate", "insufficient"]),
                name="stamp_status_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(stamp_purchase_date__isnull=True)
                | models.Q(executed_date__isnull=True)
                | models.Q(stamp_purchase_date__lte=models.F("executed_date")),
                name="stamp_purchase_not_after_execution",
            ),
            models.CheckConstraint(
                check=~models.Q(status="adequate")
                | models.Q(executed_date__isnull=False, verified_by_user__isnull=False),
                name="adequate_stamp_has_execution_verifier",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(legacy_maker_attribution=True)
                    | ~models.Q(status__in=["adequate", "insufficient"])
                    | (
                        models.Q(
                            prepared_by_user__isnull=False,
                            verified_by_user__isnull=False,
                        )
                        & ~models.Q(prepared_by_user=models.F("verified_by_user"))
                    )
                ),
                name="stamp_verification_distinct_maker_checker",
            ),
        ]


class NotarisationRecord(models.Model):
    STATUSES = {"pending", "completed", "rejected"}

    notarisation_record_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    loan_document = models.OneToOneField(
        LoanDocument, on_delete=models.PROTECT, related_name="notarisation_record"
    )
    notary_name = models.CharField(max_length=255, blank=True, null=True)
    notary_registration_number = models.CharField(
        max_length=120, blank=True, null=True, db_index=True
    )
    notarised_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=60, db_index=True)
    evidence_document = models.ForeignKey(
        "documents.DocumentFile", blank=True, null=True, on_delete=models.PROTECT
    )
    prepared_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="prepared_notarisation_records",
    )
    legacy_maker_attribution = models.BooleanField(default=False)
    verified_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="verified_notarisation_records",
    )
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "notarisation_records"
        constraints = [
            models.CheckConstraint(
                check=models.Q(status__in=["pending", "completed", "rejected"]),
                name="notary_status_bounded",
            ),
            models.CheckConstraint(
                check=~models.Q(status="completed")
                | models.Q(
                    notary_name__isnull=False,
                    notary_registration_number__isnull=False,
                    notarised_date__isnull=False,
                    evidence_document__isnull=False,
                    verified_by_user__isnull=False,
                ),
                name="completed_notary_has_evidence_verifier",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(legacy_maker_attribution=True)
                    | ~models.Q(status__in=["completed", "rejected"])
                    | (
                        models.Q(
                            prepared_by_user__isnull=False,
                            verified_by_user__isnull=False,
                        )
                        & ~models.Q(prepared_by_user=models.F("verified_by_user"))
                    )
                ),
                name="notary_verification_distinct_maker_checker",
            ),
        ]


class SignatureRecord(models.Model):
    PARTY_TYPES = {"borrower", "nominee", "witness", "user"}
    METHODS = {"wet_ink", "digital", "scanned"}
    STATUSES = {"pending", "signed", "mismatch"}
    RESOLUTION_TYPES = {"bank_verification_letter", "borrower_declaration"}

    signature_record_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    loan_document = models.ForeignKey(
        LoanDocument, on_delete=models.PROTECT, related_name="signature_records"
    )
    signer_party_type = models.CharField(max_length=80)
    signer_party_id = models.UUIDField(blank=True, null=True, db_index=True)
    signer_name_snapshot = models.CharField(max_length=255)
    signature_method = models.CharField(max_length=60)
    signature_status = models.CharField(max_length=60, db_index=True)
    signature_mismatch_flag = models.BooleanField(default=False)
    mismatch_resolution_type = models.CharField(max_length=80, blank=True, null=True)
    mismatch_resolution_document = models.ForeignKey(
        "documents.DocumentFile",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="signature_mismatch_resolutions",
    )
    mismatch_resolution_remarks = models.TextField(blank=True, null=True)
    mismatch_resolution_workflow_event = models.OneToOneField(
        "workflows.WorkflowEvent",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="signature_mismatch_resolution",
    )
    signed_at = models.DateTimeField(blank=True, null=True)
    captured_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="captured_signature_records",
    )
    legacy_maker_attribution = models.BooleanField(default=False)
    verified_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="verified_signature_records",
    )
    verified_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "signature_records"
        indexes = [
            models.Index(
                fields=["loan_document", "signature_status"],
                name="idx_signature_doc_status",
            ),
            models.Index(
                fields=["signer_party_type", "signer_party_id"],
                name="idx_signature_signer",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["loan_document", "signer_party_type", "signer_party_id"],
                name="unique_signature_document_signer",
            ),
            models.UniqueConstraint(
                fields=["loan_document", "signer_party_type"],
                condition=models.Q(signer_party_id__isnull=True),
                name="unique_signature_null_signer",
            ),
            models.CheckConstraint(
                check=models.Q(
                    signer_party_type__in=["borrower", "nominee", "witness", "user"]
                ),
                name="signature_party_type_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(signature_method__in=["wet_ink", "digital", "scanned"]),
                name="signature_method_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(signature_status__in=["pending", "signed", "mismatch"]),
                name="signature_status_bounded",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(
                        mismatch_resolution_type__isnull=True,
                        mismatch_resolution_document__isnull=True,
                        mismatch_resolution_remarks__isnull=True,
                    )
                    | models.Q(
                        mismatch_resolution_type__in=[
                            "bank_verification_letter",
                            "borrower_declaration",
                        ],
                        mismatch_resolution_document__isnull=False,
                        signature_status="mismatch",
                        signature_mismatch_flag=True,
                        verified_by_user__isnull=False,
                        verified_at__isnull=False,
                    )
                ),
                name="signature_resolution_complete",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(legacy_maker_attribution=True)
                    | models.Q(mismatch_resolution_type__isnull=True)
                    | (
                        models.Q(
                            captured_by_user__isnull=False,
                            verified_by_user__isnull=False,
                        )
                        & ~models.Q(captured_by_user=models.F("verified_by_user"))
                    )
                ),
                name="signature_resolution_distinct_maker_checker",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(
                        signature_status="pending",
                        signed_at__isnull=True,
                        signature_mismatch_flag=False,
                        mismatch_resolution_type__isnull=True,
                    )
                    | models.Q(
                        signature_status="signed",
                        signed_at__isnull=False,
                        signature_mismatch_flag=False,
                    )
                    | models.Q(
                        signature_status="mismatch",
                        signature_mismatch_flag=True,
                    )
                ),
                name="signature_status_facts_consistent",
            ),
        ]


class DocumentChecklist(models.Model):
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_CS_APPROVED = "cs_approved"
    STATUS_CREDIT_APPROVED = "credit_approved"
    STATUS_SANCTION_APPROVED = "sanction_approved"
    STATUS_READY = "ready"
    STATUSES = {
        STATUS_IN_PROGRESS,
        STATUS_CS_APPROVED,
        STATUS_CREDIT_APPROVED,
        STATUS_SANCTION_APPROVED,
        STATUS_READY,
    }

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
    company_secretary_signature = models.ForeignKey(
        "ChecklistAction",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="company_secretary_checklists",
    )
    credit_manager_signature = models.ForeignKey(
        "ChecklistAction",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="credit_manager_checklists",
    )
    sanction_committee_signature = models.ForeignKey(
        "ChecklistAction",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="sanction_committee_checklists",
    )
    senior_manager_finance_signature = models.ForeignKey(
        "ChecklistAction",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="senior_manager_finance_checklists",
    )
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
                    checklist_status__in=[
                        "in_progress",
                        "cs_approved",
                        "credit_approved",
                        "sanction_approved",
                        "ready",
                    ]
                ),
                name="document_checklist_valid_status",
            ),
            models.CheckConstraint(
                check=models.Q(loan_account_id__isnull=True),
                name="checklist_account_requires_epic_009",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(credit_manager_signature_id__isnull=True)
                    | models.Q(company_secretary_signature_id__isnull=False)
                ),
                name="checklist_credit_requires_cs",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(sanction_committee_signature_id__isnull=True)
                    | models.Q(credit_manager_signature_id__isnull=False)
                ),
                name="checklist_sanction_requires_credit",
            ),
            models.CheckConstraint(
                check=models.Q(senior_manager_finance_signature_id__isnull=True),
                name="checklist_finance_requires_epic_009",
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
    stamp_status = models.CharField(max_length=60, blank=True, null=True, db_index=True)
    notarisation_status = models.CharField(
        max_length=60, blank=True, null=True, db_index=True
    )
    poa_execution_status = models.CharField(max_length=60, blank=True, null=True)
    poa_status = models.CharField(max_length=60, blank=True, null=True)

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
            errors["completion_status"] = (
                "Pending items cannot carry verification facts."
            )
        if (
            self.loan_document_id
            and self.document_checklist_id
            and self.loan_document.loan_application_id
            != self.document_checklist.loan_application_id
        ):
            errors["loan_document"] = (
                "Loan document must belong to the checklist application."
            )
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class ChecklistActionQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError({"checklist_action": "Checklist evidence is immutable."})

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValidationError({"checklist_action": "Checklist evidence is immutable."})

    def delete(self):
        raise ValidationError({"checklist_action": "Checklist evidence is immutable."})


class ChecklistAction(models.Model):
    TYPE_ITEM_COMPLETION = "item_completion"
    TYPE_COMPANY_SECRETARY_APPROVAL = "company_secretary_approval"
    TYPE_CREDIT_MANAGER_APPROVAL = "credit_manager_approval"
    TYPE_SANCTION_COMMITTEE_APPROVAL = "sanction_committee_approval"
    TYPE_DISBURSEMENT_SIGNATURE = "disbursement_signature"
    ACTION_TYPES = {
        TYPE_ITEM_COMPLETION,
        TYPE_COMPANY_SECRETARY_APPROVAL,
        TYPE_CREDIT_MANAGER_APPROVAL,
        TYPE_SANCTION_COMMITTEE_APPROVAL,
        TYPE_DISBURSEMENT_SIGNATURE,
    }

    checklist_action_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    document_checklist = models.ForeignKey(
        DocumentChecklist, on_delete=models.PROTECT, related_name="actions"
    )
    checklist_item = models.ForeignKey(
        ChecklistItem,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="completion_actions",
    )
    loan_document = models.ForeignKey(
        LoanDocument,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="checklist_actions",
    )
    action_type = models.CharField(max_length=80, db_index=True)
    meaning = models.CharField(max_length=255)
    comments = models.TextField(blank=True, null=True)
    actor_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="checklist_actions"
    )
    actor_user_name_snapshot = models.CharField(max_length=200)
    canonical_role_code = models.CharField(max_length=80)
    request_id = models.CharField(max_length=255, blank=True, null=True)
    workflow_event = models.OneToOneField(
        "workflows.WorkflowEvent",
        on_delete=models.PROTECT,
        related_name="checklist_action",
    )
    signed_at = models.DateTimeField(default=timezone.now)

    objects = ChecklistActionQuerySet.as_manager()

    class Meta:
        db_table = "checklist_actions"
        ordering = ["signed_at", "checklist_action_id"]
        indexes = [
            models.Index(
                fields=["document_checklist", "action_type"],
                name="idx_check_action_stage",
            )
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["checklist_item"],
                condition=models.Q(action_type="item_completion"),
                name="unique_checklist_item_completion",
            ),
            models.UniqueConstraint(
                fields=["document_checklist", "action_type"],
                condition=~models.Q(action_type="item_completion"),
                name="unique_checklist_approval_stage",
            ),
            models.CheckConstraint(
                check=models.Q(
                    action_type__in=[
                        "item_completion",
                        "company_secretary_approval",
                        "credit_manager_approval",
                        "sanction_committee_approval",
                        "disbursement_signature",
                    ]
                ),
                name="checklist_action_valid_type",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(
                        action_type="item_completion",
                        checklist_item__isnull=False,
                        loan_document__isnull=False,
                    )
                    | (
                        ~models.Q(action_type="item_completion")
                        & models.Q(
                            checklist_item__isnull=True,
                            loan_document__isnull=True,
                        )
                    )
                ),
                name="checklist_action_target_consistent",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(action_type="item_completion")
                    | (models.Q(comments__isnull=False) & ~models.Q(comments=""))
                ),
                name="checklist_approval_comments_required",
            ),
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError({"checklist_action": "Checklist evidence is immutable."})
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError({"checklist_action": "Checklist evidence is immutable."})
