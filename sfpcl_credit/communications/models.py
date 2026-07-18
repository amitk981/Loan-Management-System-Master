import uuid

from django.db import models
from django.utils import timezone


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


class CommunicationDeliveryOutbox(models.Model):
    DELIVERY_PENDING = "pending"
    DELIVERY_SENT = "sent"
    PROVENANCE_VERIFIED = "verified"
    PROVENANCE_LEGACY_PARTIAL = "legacy_partial"
    PROVENANCE_ORIGIN_FROZEN = "frozen_before_dispatch"
    PROVENANCE_ORIGIN_LEGACY_0005 = "legacy_0005"
    PROVENANCE_ORIGIN_AMBIGUOUS = "ambiguous_legacy"

    outbox_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    advice_intent = models.UUIDField(unique=True, db_column="advice_intent_id")
    communication_id = models.UUIDField(unique=True)
    idempotency_key = models.CharField(max_length=255, unique=True)
    channel = models.CharField(max_length=40)
    recipient_address = models.CharField(max_length=255)
    recipient_digest = models.CharField(max_length=64)
    content_template = models.ForeignKey(
        ContentTemplate,
        on_delete=models.PROTECT,
        related_name="delivery_outboxes",
        blank=True,
        null=True,
    )
    template_code_snapshot = models.CharField(max_length=120, blank=True, null=True)
    template_provenance_status = models.CharField(max_length=40)
    template_provenance_origin = models.CharField(max_length=40)
    template_name_snapshot = models.CharField(max_length=255, blank=True, null=True)
    template_type_snapshot = models.CharField(max_length=60, blank=True, null=True)
    template_language_code_snapshot = models.CharField(
        max_length=20, blank=True, null=True
    )
    template_audience_snapshot = models.CharField(max_length=80, blank=True, null=True)
    template_version_snapshot = models.CharField(max_length=40, blank=True, null=True)
    template_approval_status_snapshot = models.CharField(max_length=60, blank=True, null=True)
    template_effective_from_snapshot = models.DateField(blank=True, null=True)
    template_effective_to_snapshot = models.DateField(blank=True, null=True)
    template_variables_snapshot = models.JSONField(blank=True, null=True)
    subject_template_snapshot = models.CharField(max_length=255, blank=True, null=True)
    body_template_snapshot = models.TextField(blank=True, null=True)
    template_checksum_sha256 = models.CharField(max_length=64, blank=True, null=True)
    subject_snapshot = models.CharField(max_length=255)
    body_snapshot = models.TextField()
    payload_digest = models.CharField(max_length=64)
    related_entity_type = models.CharField(max_length=80)
    related_entity_id = models.UUIDField()
    delivery_status = models.CharField(max_length=40, default=DELIVERY_PENDING)
    provider_external_message_id = models.CharField(
        max_length=120, blank=True, null=True, unique=True
    )
    provider_delivery_status = models.CharField(max_length=40, blank=True, null=True)
    provider_accepted_at = models.DateTimeField(blank=True, null=True)
    accepted_provider_attempt = models.OneToOneField(
        "CommunicationProviderAttempt",
        on_delete=models.PROTECT,
        related_name="accepted_outbox",
        blank=True,
        null=True,
    )
    delivery_receipt = models.OneToOneField(
        "DisbursementAdviceDeliveryReceipt",
        on_delete=models.PROTECT,
        related_name="protected_outbox",
        blank=True,
        null=True,
    )
    final_communication = models.OneToOneField(
        Communication,
        on_delete=models.PROTECT,
        related_name="protected_delivery_outbox",
        blank=True,
        null=True,
    )
    portal_capability_version = models.PositiveIntegerField(default=0)
    portal_capability_expires_at = models.DateTimeField(blank=True, null=True)
    portal_capability_consumed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "communication_delivery_outboxes"
        indexes = [
            models.Index(fields=["related_entity_type", "related_entity_id"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    ~models.Q(idempotency_key="")
                    & ~models.Q(channel="")
                    & ~models.Q(recipient_address="")
                    & ~models.Q(recipient_digest="")
                    & models.Q(template_provenance_status__in=("verified", "legacy_partial"))
                    & ~models.Q(subject_snapshot="")
                    & ~models.Q(body_snapshot="")
                    & ~models.Q(payload_digest="")
                    & ~models.Q(related_entity_type="")
                    & models.Q(delivery_status__in=("pending", "sent"))
                ),
                name="communication_outbox_complete",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(
                        template_provenance_status="verified",
                        template_provenance_origin="frozen_before_dispatch",
                        content_template__isnull=False,
                        template_code_snapshot__isnull=False,
                        template_name_snapshot__isnull=False,
                        template_type_snapshot__isnull=False,
                        template_audience_snapshot__isnull=False,
                        template_version_snapshot__isnull=False,
                        template_approval_status_snapshot__isnull=False,
                        template_effective_from_snapshot__isnull=False,
                        template_variables_snapshot__isnull=False,
                        subject_template_snapshot__isnull=False,
                        body_template_snapshot__isnull=False,
                        template_checksum_sha256__isnull=False,
                    )
                    | models.Q(
                        template_provenance_status="legacy_partial",
                        template_provenance_origin__in=(
                            "legacy_0005",
                            "ambiguous_legacy",
                        ),
                        content_template__isnull=True,
                        template_code_snapshot__isnull=True,
                        template_name_snapshot__isnull=True,
                        template_type_snapshot__isnull=True,
                        template_language_code_snapshot__isnull=True,
                        template_audience_snapshot__isnull=True,
                        template_version_snapshot__isnull=True,
                        template_approval_status_snapshot__isnull=True,
                        template_effective_from_snapshot__isnull=True,
                        template_effective_to_snapshot__isnull=True,
                        template_variables_snapshot__isnull=True,
                        subject_template_snapshot__isnull=True,
                        body_template_snapshot__isnull=True,
                        template_checksum_sha256__isnull=True,
                    )
                ),
                name="communication_outbox_provenance_complete",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(
                        template_provenance_origin="legacy_0005",
                        template_provenance_status="legacy_partial",
                    )
                    | models.Q(
                        template_provenance_origin="frozen_before_dispatch",
                        template_provenance_status="verified",
                    )
                    | models.Q(
                        template_provenance_origin="ambiguous_legacy",
                        template_provenance_status="legacy_partial",
                    )
                ),
                name="communication_outbox_provenance_origin",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(delivery_receipt__isnull=True, final_communication__isnull=True)
                    | models.Q(delivery_receipt__isnull=False, final_communication__isnull=False)
                ),
                name="communication_outbox_final_chain_complete",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(
                        delivery_status="pending",
                        provider_external_message_id__isnull=True,
                        provider_delivery_status__isnull=True,
                        provider_accepted_at__isnull=True,
                        accepted_provider_attempt__isnull=True,
                    )
                    | (
                        models.Q(
                            delivery_status="sent",
                            provider_external_message_id__isnull=False,
                            provider_delivery_status__isnull=False,
                            provider_accepted_at__isnull=False,
                            accepted_provider_attempt__isnull=False,
                        )
                        & ~models.Q(provider_external_message_id="")
                        & ~models.Q(provider_delivery_status="")
                    )
                ),
                name="communication_outbox_provider_result_complete",
            ),
        ]


class CommunicationDeliveryJob(models.Model):
    KIND_GENERIC = "generic"
    KIND_ADVICE = "advice"
    STATUS_QUEUED = "queued"
    STATUS_RUNNING = "running"
    STATUS_RETRYING = "retrying"
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"
    STATUSES = {
        STATUS_QUEUED,
        STATUS_RUNNING,
        STATUS_RETRYING,
        STATUS_SENT,
        STATUS_FAILED,
    }

    communication_job_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    outbox = models.OneToOneField(
        CommunicationDeliveryOutbox,
        on_delete=models.PROTECT,
        related_name="delivery_job",
        blank=True,
        null=True,
    )
    communication_id = models.UUIDField(unique=True)
    advice_intent_id = models.UUIDField(blank=True, null=True, unique=True)
    job_kind = models.CharField(max_length=40)
    idempotency_key = models.CharField(max_length=255, unique=True)
    actor_id = models.UUIDField()
    actor_role_code = models.CharField(max_length=80)
    actor_team_codes = models.JSONField(default=list)
    request_id = models.CharField(max_length=255)
    ip_address = models.CharField(max_length=64, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    request_payload_digest = models.CharField(max_length=64)
    status = models.CharField(max_length=40, default=STATUS_QUEUED, db_index=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    max_attempts = models.PositiveSmallIntegerField(default=3)
    next_attempt_at = models.DateTimeField(default=timezone.now, db_index=True)
    last_failure_code = models.CharField(max_length=80, blank=True)
    provider_external_message_id = models.CharField(
        max_length=120, blank=True, null=True, unique=True
    )
    provider_delivery_status = models.CharField(max_length=40, blank=True, null=True)
    provider_accepted_at = models.DateTimeField(blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "communication_delivery_jobs"
        indexes = [models.Index(fields=["status", "next_attempt_at"])]
        constraints = [
            models.CheckConstraint(
                check=(
                    ~models.Q(idempotency_key="")
                    & ~models.Q(actor_role_code="")
                    & ~models.Q(request_id="")
                    & ~models.Q(request_payload_digest="")
                    & models.Q(
                        status__in=("queued", "running", "retrying", "sent", "failed")
                    )
                    & models.Q(max_attempts__gte=1)
                    & models.Q(attempts__lte=models.F("max_attempts"))
                    & (
                        models.Q(
                            job_kind="advice",
                            outbox__isnull=False,
                            advice_intent_id__isnull=False,
                        )
                        | models.Q(
                            job_kind="generic",
                            outbox__isnull=True,
                            advice_intent_id__isnull=True,
                        )
                    )
                ),
                name="communication_delivery_job_complete",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(
                        provider_external_message_id__isnull=True,
                        provider_delivery_status__isnull=True,
                        provider_accepted_at__isnull=True,
                    )
                    | (
                        models.Q(
                            job_kind="generic",
                            provider_external_message_id__isnull=False,
                            provider_delivery_status="sent",
                            provider_accepted_at__isnull=False,
                        )
                        & ~models.Q(provider_external_message_id="")
                    )
                ),
                name="communication_job_provider_result_complete",
            ),
        ]


class ImmutableProviderAttemptQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise TypeError("Provider-attempt evidence is immutable.")

    def delete(self):
        raise TypeError("Provider-attempt evidence is immutable.")


class CommunicationProviderAttempt(models.Model):
    OUTCOME_ACCEPTED = "accepted"
    OUTCOME_REJECTED = "rejected"

    provider_attempt_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    outbox = models.ForeignKey(
        CommunicationDeliveryOutbox,
        on_delete=models.PROTECT,
        related_name="provider_attempts",
    )
    advice_intent_id = models.UUIDField()
    communication_id = models.UUIDField()
    idempotency_key = models.CharField(max_length=255)
    payload_digest = models.CharField(max_length=64)
    adapter_kind = models.CharField(max_length=255)
    outcome = models.CharField(max_length=20)
    provider_external_message_id = models.CharField(
        max_length=120, blank=True, null=True, unique=True
    )
    provider_delivery_status = models.CharField(
        max_length=40, blank=True, null=True
    )
    provider_accepted_at = models.DateTimeField(blank=True, null=True)
    attempted_at = models.DateTimeField(default=timezone.now)
    evidence_digest = models.CharField(max_length=64)
    objects = ImmutableProviderAttemptQuerySet.as_manager()

    class Meta:
        db_table = "communication_provider_attempts"
        constraints = [
            models.UniqueConstraint(
                fields=["outbox"],
                condition=models.Q(outcome="accepted"),
                name="one_accepted_provider_attempt_per_outbox",
            ),
            models.CheckConstraint(
                check=(
                    ~models.Q(idempotency_key="")
                    & ~models.Q(payload_digest="")
                    & ~models.Q(adapter_kind="")
                    & ~models.Q(evidence_digest="")
                    & (
                        (
                            models.Q(
                                outcome="accepted",
                                provider_external_message_id__isnull=False,
                                provider_delivery_status="sent",
                                provider_accepted_at__isnull=False,
                            )
                            & ~models.Q(provider_external_message_id="")
                        )
                        | models.Q(
                            outcome="rejected",
                            provider_external_message_id__isnull=True,
                            provider_delivery_status__isnull=True,
                            provider_accepted_at__isnull=True,
                        )
                    )
                ),
                name="communication_provider_attempt_complete",
            ),
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("Provider-attempt evidence is immutable.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("Provider-attempt evidence is immutable.")


class DisbursementAdviceDeliveryReceipt(models.Model):
    delivery_receipt_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    advice_intent = models.UUIDField(unique=True, db_column="advice_intent_id")
    idempotency_key = models.CharField(max_length=255, unique=True)
    payload_digest = models.CharField(max_length=64)
    external_message_id = models.CharField(max_length=120, unique=True)
    delivery_status = models.CharField(max_length=40)
    accepted_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "disbursement_advice_delivery_receipts"
        constraints = [
            models.CheckConstraint(
                check=(
                    ~models.Q(idempotency_key="")
                    & ~models.Q(payload_digest="")
                    & ~models.Q(external_message_id="")
                    & models.Q(delivery_status="sent")
                ),
                name="advice_delivery_receipt_complete",
            ),
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
