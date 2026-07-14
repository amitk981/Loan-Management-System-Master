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
