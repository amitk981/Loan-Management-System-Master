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


class Communication(models.Model):
    CHANNEL_EMAIL = "email"
    CHANNEL_SMS = "sms"
    CHANNEL_PHONE = "phone"
    CHANNEL_COURIER = "courier"
    CHANNELS = {CHANNEL_EMAIL, CHANNEL_SMS, CHANNEL_PHONE, CHANNEL_COURIER}

    DELIVERY_PENDING = "pending"

    communication_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    related_entity_type = models.CharField(max_length=80)
    related_entity_id = models.UUIDField()
    recipient_party_type = models.CharField(max_length=80)
    recipient_party_id = models.UUIDField(blank=True, null=True)
    recipient_address = models.CharField(max_length=255, blank=True, null=True)
    channel = models.CharField(max_length=40)
    content_template = models.ForeignKey(
        ContentTemplate,
        on_delete=models.PROTECT,
        related_name="communications",
        blank=True,
        null=True,
    )
    subject_snapshot = models.CharField(max_length=255, blank=True, null=True)
    body_snapshot = models.TextField()
    sent_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="sent_communications",
        blank=True,
        null=True,
    )
    sent_at = models.DateTimeField(blank=True, null=True, db_index=True)
    delivery_status = models.CharField(
        max_length=40, default=DELIVERY_PENDING, db_index=True
    )
    acknowledgement_status = models.CharField(max_length=40, blank=True, null=True)
    external_message_id = models.CharField(max_length=120, blank=True, null=True)

    class Meta:
        db_table = "communications"
        ordering = ["communication_id"]
        indexes = [
            models.Index(fields=["related_entity_type", "related_entity_id"]),
        ]


class Notification(models.Model):
    SEVERITY_INFO = "info"
    SEVERITY_WARNING = "warning"
    SEVERITY_URGENT = "urgent"
    SEVERITIES = {SEVERITY_INFO, SEVERITY_WARNING, SEVERITY_URGENT}

    notification_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    communication = models.ForeignKey(
        Communication,
        on_delete=models.SET_NULL,
        related_name="notifications",
        blank=True,
        null=True,
    )
    notification_type = models.CharField(max_length=80, db_index=True)
    category = models.CharField(max_length=80, db_index=True)
    severity = models.CharField(max_length=20, default=SEVERITY_INFO, db_index=True)
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    related_entity_type = models.CharField(max_length=80, blank=True)
    related_entity_id = models.UUIDField(blank=True, null=True, db_index=True)
    action_label = models.CharField(max_length=80, blank=True)
    action_url = models.CharField(max_length=255, blank=True)
    sender_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="sent_notifications",
        blank=True,
        null=True,
    )
    recipient_user = models.ForeignKey(
        "identity.User",
        on_delete=models.CASCADE,
        related_name="notifications",
        blank=True,
        null=True,
    )
    recipient_role_code = models.CharField(max_length=80, blank=True, db_index=True)
    recipient_team_code = models.CharField(max_length=80, blank=True, db_index=True)
    read_at = models.DateTimeField(blank=True, null=True)
    read_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="read_notifications",
        blank=True,
        null=True,
    )
    read_state_version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at", "-notification_id"]
        indexes = [
            models.Index(fields=["recipient_user", "read_at"]),
            models.Index(fields=["recipient_role_code", "read_at"]),
            models.Index(fields=["recipient_team_code", "read_at"]),
        ]

    @property
    def read(self):
        return self.read_at is not None
