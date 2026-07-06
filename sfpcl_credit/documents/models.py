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
