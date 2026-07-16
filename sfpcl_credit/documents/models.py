import uuid

from django.db import models
from django.utils import timezone


class DocumentFile(models.Model):
    SENSITIVITY_PUBLIC = "public"
    SENSITIVITY_INTERNAL = "internal"
    SENSITIVITY_CONFIDENTIAL = "confidential"
    SENSITIVITY_RESTRICTED = "restricted"
    SENSITIVITY_LEVELS = {
        SENSITIVITY_PUBLIC,
        SENSITIVITY_INTERNAL,
        SENSITIVITY_CONFIDENTIAL,
        SENSITIVITY_RESTRICTED,
    }

    document_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_name = models.CharField(max_length=255)
    file_extension = models.CharField(max_length=20, blank=True, null=True)
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    file_size_bytes = models.BigIntegerField(blank=True, null=True)
    storage_provider = models.CharField(max_length=80)
    storage_key = models.TextField()
    checksum_sha256 = models.CharField(max_length=128, blank=True, null=True)
    uploaded_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="uploaded_document_files",
    )
    uploaded_at = models.DateTimeField(default=timezone.now)
    sensitivity_level = models.CharField(max_length=60, db_index=True)
    retention_until_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "document_files"
        ordering = ["-uploaded_at", "-document_id"]

    def __str__(self):
        return self.file_name


class DocumentTemplateIdentity(models.Model):
    GLOBAL_VARIANT_KEY = "__global__"

    document_template_identity_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    document_type = models.CharField(max_length=100)
    borrower_variant_key = models.CharField(max_length=60)

    class Meta:
        db_table = "document_template_identities"
        constraints = [
            models.UniqueConstraint(
                fields=["document_type", "borrower_variant_key"],
                name="unique_document_template_identity",
            )
        ]


class DocumentTemplate(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_APPROVED = "approved"
    STATUS_RETIRED = "retired"
    APPROVAL_STATUSES = {STATUS_DRAFT, STATUS_APPROVED, STATUS_RETIRED}
    BORROWER_TYPES = {"individual_farmer", "fpc", "fpo"}

    document_template_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    template_code = models.CharField(max_length=120, unique=True)
    template_name = models.CharField(max_length=255)
    document_type = models.CharField(max_length=100, db_index=True)
    borrower_type = models.CharField(max_length=60, blank=True, null=True, db_index=True)
    template_version = models.CharField(max_length=40)
    template_file = models.ForeignKey(
        DocumentFile,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="document_templates",
    )
    merge_fields_json = models.JSONField(blank=True, null=True)
    approval_status = models.CharField(max_length=60, db_index=True)
    effective_from = models.DateField()
    effective_to = models.DateField(blank=True, null=True)
    supersedes = models.OneToOneField(
        "self",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="successor",
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "document_templates"
        ordering = ["-effective_from", "-created_at", "-document_template_id"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(effective_to__isnull=True)
                | models.Q(effective_to__gte=models.F("effective_from")),
                name="doc_template_effective_dates",
            ),
            models.CheckConstraint(
                check=models.Q(
                    approval_status__in=("draft", "approved", "retired")
                ),
                name="doc_template_approval_status",
            ),
            models.CheckConstraint(
                check=models.Q(borrower_type__isnull=True)
                | models.Q(
                    borrower_type__in=("individual_farmer", "fpc", "fpo")
                ),
                name="doc_template_borrower_type",
            ),
            models.UniqueConstraint(
                fields=["document_type", "borrower_type", "template_version"],
                name="unique_doc_template_variant_version",
            ),
        ]

    def __str__(self):
        return f"{self.template_code}:{self.template_version}"
