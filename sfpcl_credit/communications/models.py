import uuid

from django.db import models


class ContentTemplate(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_APPROVED = "approved"
    APPROVAL_STATUSES = {STATUS_DRAFT, STATUS_APPROVED}

    content_template_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    template_code = models.CharField(max_length=120, unique=True)
    template_name = models.CharField(max_length=255)
    template_type = models.CharField(max_length=60, db_index=True)
    language_code = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    audience = models.CharField(max_length=80, db_index=True)
    subject_template = models.CharField(max_length=255, blank=True, null=True)
    body_template = models.TextField()
    variables_json = models.JSONField(blank=True, null=True)
    approval_status = models.CharField(max_length=60, db_index=True)
    template_version = models.CharField(max_length=40)
    effective_from = models.DateField()
    effective_to = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "content_templates"
        ordering = ["template_code"]
