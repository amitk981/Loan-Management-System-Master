import uuid

from django.db import models
from django.utils import timezone


class ImmutableClosureQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValueError("Loan Closure evidence is immutable.")

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValueError("Loan Closure evidence is immutable.")

    def delete(self):
        raise ValueError("Loan Closure evidence is immutable.")


class LoanClosure(models.Model):
    TYPE_FULL_REPAYMENT = "full_repayment"
    STAGE_FINANCIALLY_CLOSED = "financially_closed"

    loan_closure_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan_account = models.OneToOneField(
        "loans.LoanAccount", on_delete=models.PROTECT, related_name="loan_closure"
    )
    member = models.ForeignKey(
        "members.Member", on_delete=models.PROTECT, related_name="loan_closures"
    )
    closure_type = models.CharField(max_length=80, db_index=True)
    closure_stage = models.CharField(max_length=80, db_index=True)
    closure_notes = models.TextField()
    principal_paid_flag = models.BooleanField()
    interest_paid_flag = models.BooleanField()
    charges_paid_flag = models.BooleanField()
    total_outstanding_at_closure = models.DecimalField(max_digits=18, decimal_places=2)
    readiness_snapshot_json = models.JSONField()
    closed_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="closed_loans"
    )
    closed_by_role_code = models.CharField(max_length=100)
    closed_at = models.DateTimeField(default=timezone.now, db_index=True)
    idempotency_key_digest = models.CharField(max_length=64, unique=True)
    payload_digest = models.CharField(max_length=64)
    close_audit = models.OneToOneField(
        "identity.AuditLog", on_delete=models.PROTECT, related_name="loan_closure"
    )
    workflow_event = models.OneToOneField(
        "workflows.WorkflowEvent", on_delete=models.PROTECT, related_name="loan_closure"
    )

    objects = ImmutableClosureQuerySet.as_manager()

    class Meta:
        db_table = "loan_closures"
        constraints = [
            models.CheckConstraint(
                check=models.Q(closure_type="full_repayment"),
                name="loan_closure_full_repayment_only",
            ),
            models.CheckConstraint(
                check=models.Q(closure_stage="financially_closed"),
                name="loan_closure_financial_stage_only",
            ),
            models.CheckConstraint(
                check=models.Q(principal_paid_flag=True)
                & models.Q(interest_paid_flag=True)
                & models.Q(charges_paid_flag=True)
                & models.Q(total_outstanding_at_closure=0),
                name="loan_closure_zero_balance_only",
            ),
            models.CheckConstraint(
                check=~models.Q(closure_notes="") & ~models.Q(closed_by_role_code=""),
                name="loan_closure_text_required",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise ValueError("Loan Closure evidence is immutable.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Loan Closure evidence is immutable.")


class ClosureRequirement(models.Model):
    TYPE_NOC = "noc"
    TYPE_SECURITY_RETURN = "security_return"
    TYPE_ARCHIVE = "archive"
    STATUS_PENDING = "pending"
    STATUS_NOT_APPLICABLE = "not_applicable"
    STATUS_COMPLETED = "completed"

    closure_requirement_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    loan_closure = models.ForeignKey(
        LoanClosure, on_delete=models.PROTECT, related_name="requirements"
    )
    requirement_type = models.CharField(max_length=60, db_index=True)
    requirement_status = models.CharField(max_length=60, db_index=True)
    applicability_snapshot_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)

    objects = ImmutableClosureQuerySet.as_manager()

    class Meta:
        db_table = "closure_requirements"
        constraints = [
            models.UniqueConstraint(
                fields=["loan_closure", "requirement_type"],
                name="uniq_closure_requirement_type",
            ),
            models.CheckConstraint(
                check=models.Q(requirement_type__in=("noc", "security_return", "archive")),
                name="closure_requirement_type_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(
                    requirement_status__in=("pending", "not_applicable", "completed")
                ),
                name="closure_requirement_status_bounded",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise ValueError("Closure Requirement evidence is immutable until its owner slice.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Closure Requirement evidence is immutable until its owner slice.")

    @classmethod
    def complete_noc_requirement(cls, *, loan_closure_id):
        """The NOC owner is the sole controlled pending-to-completed transition."""
        return models.QuerySet.update(
            cls.objects.filter(
                loan_closure_id=loan_closure_id,
                requirement_type=cls.TYPE_NOC,
                requirement_status=cls.STATUS_PENDING,
            ),
            requirement_status=cls.STATUS_COMPLETED,
        )

    @classmethod
    def complete_security_return_requirement(cls, *, loan_closure_id):
        return models.QuerySet.update(
            cls.objects.filter(
                loan_closure_id=loan_closure_id,
                requirement_type=cls.TYPE_SECURITY_RETURN,
                requirement_status=cls.STATUS_PENDING,
            ),
            requirement_status=cls.STATUS_COMPLETED,
        )


class ImmutableNocQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValueError("NOC evidence is immutable.")

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValueError("NOC evidence is immutable.")

    def delete(self):
        raise ValueError("NOC evidence is immutable.")


class NocRecord(models.Model):
    DELIVERY_EMAIL = "email"
    DELIVERY_QUEUED = "queued"
    DELIVERY_SENT = "sent"
    DELIVERY_FAILED = "failed"

    noc_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan_closure = models.OneToOneField(
        LoanClosure, on_delete=models.PROTECT, related_name="noc"
    )
    loan_account = models.ForeignKey(
        "loans.LoanAccount", on_delete=models.PROTECT, related_name="nocs"
    )
    member = models.ForeignKey(
        "members.Member", on_delete=models.PROTECT, related_name="nocs"
    )
    loan_document = models.OneToOneField(
        "legal_documents.LoanDocument", on_delete=models.PROTECT, related_name="noc"
    )
    document = models.OneToOneField(
        "documents.DocumentFile", on_delete=models.PROTECT, related_name="noc"
    )
    generation_audit = models.OneToOneField(
        "identity.AuditLog", on_delete=models.PROTECT, related_name="generated_noc"
    )
    document_template_id_snapshot = models.UUIDField()
    document_template_version_snapshot = models.CharField(max_length=40)
    renderer_contract_version_snapshot = models.CharField(max_length=64)
    document_checksum_sha256_snapshot = models.CharField(max_length=128)
    merge_values_sha256_snapshot = models.CharField(max_length=64)
    issued_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="issued_nocs"
    )
    issued_by_role_code = models.CharField(max_length=100)
    issued_at = models.DateTimeField(default=timezone.now, db_index=True)
    signatory_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="signed_nocs"
    )
    signatory_role_code = models.CharField(max_length=100)
    signatory_name_snapshot = models.CharField(max_length=200)
    delivery_mode = models.CharField(max_length=60)
    delivery_status = models.CharField(max_length=60)
    recipient_address = models.CharField(max_length=255)
    communication = models.OneToOneField(
        "communications.Communication", on_delete=models.PROTECT, related_name="noc"
    )
    communication_job = models.OneToOneField(
        "communications.CommunicationDeliveryJob",
        on_delete=models.PROTECT,
        related_name="noc",
    )
    borrower_name_snapshot = models.CharField(max_length=255)
    loan_account_number_snapshot = models.CharField(max_length=80)
    application_reference_snapshot = models.CharField(max_length=40)
    disbursed_amount_snapshot = models.DecimalField(max_digits=18, decimal_places=2)
    full_repayment_at_snapshot = models.DateTimeField()
    idempotency_key_digest = models.CharField(max_length=64, unique=True)
    payload_digest = models.CharField(max_length=64)
    issue_audit = models.OneToOneField(
        "identity.AuditLog", on_delete=models.PROTECT, related_name="noc_issue"
    )
    issue_workflow_event = models.OneToOneField(
        "workflows.WorkflowEvent", on_delete=models.PROTECT, related_name="noc_issue"
    )

    objects = ImmutableNocQuerySet.as_manager()

    class Meta:
        db_table = "nocs"
        constraints = [
            models.CheckConstraint(
                check=models.Q(delivery_mode="email"), name="noc_delivery_mode_email"
            ),
            models.CheckConstraint(
                check=models.Q(delivery_status__in=("queued", "sent", "failed")),
                name="noc_delivery_status_bounded",
            ),
            models.CheckConstraint(
                check=~models.Q(issued_by_role_code="")
                & ~models.Q(signatory_role_code="")
                & ~models.Q(signatory_name_snapshot="")
                & ~models.Q(recipient_address="")
                & ~models.Q(borrower_name_snapshot="")
                & ~models.Q(loan_account_number_snapshot="")
                & ~models.Q(application_reference_snapshot=""),
                name="noc_required_text_complete",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise ValueError("NOC evidence is immutable.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("NOC evidence is immutable.")

    @classmethod
    def synchronize_delivery_status(cls, *, noc_id, delivery_status):
        if delivery_status not in {
            cls.DELIVERY_QUEUED,
            cls.DELIVERY_SENT,
            cls.DELIVERY_FAILED,
        }:
            raise ValueError("Unsupported NOC delivery status.")
        return models.QuerySet.update(
            cls.objects.filter(pk=noc_id).exclude(delivery_status=delivery_status),
            delivery_status=delivery_status,
        )


class ImmutableSecurityReturnQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValueError("Security Return evidence changes only through its owner module.")

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValueError("Security Return evidence changes only through its owner module.")

    def delete(self):
        raise ValueError("Security Return evidence is retained.")


class SecurityReturn(models.Model):
    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "completed"

    security_return_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    loan_closure = models.OneToOneField(
        LoanClosure, on_delete=models.PROTECT, related_name="security_return"
    )
    security_package = models.ForeignKey(
        "security_instruments.SecurityPackage",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="security_returns",
    )
    return_status = models.CharField(max_length=40, db_index=True)
    version = models.PositiveIntegerField(default=0)
    recorded_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="recorded_security_returns"
    )
    recorded_by_role_code = models.CharField(max_length=100)
    recorded_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(blank=True, null=True)
    acknowledgement_document = models.ForeignKey(
        "documents.DocumentFile",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="security_return_acknowledgements",
    )
    idempotency_key_digest = models.CharField(max_length=64, unique=True)
    payload_digest = models.CharField(max_length=64)
    record_audit = models.OneToOneField(
        "identity.AuditLog", on_delete=models.PROTECT, related_name="security_return_record"
    )

    objects = ImmutableSecurityReturnQuerySet.as_manager()

    class Meta:
        db_table = "security_returns"
        constraints = [
            models.CheckConstraint(
                check=models.Q(return_status__in=("pending", "completed")),
                name="security_return_status_bounded",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(return_status="pending", completed_at__isnull=True)
                    | models.Q(return_status="completed", completed_at__isnull=False)
                ),
                name="security_return_completion_consistent",
            ),
            models.CheckConstraint(
                check=~models.Q(recorded_by_role_code=""),
                name="security_return_role_required",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise ValueError("Security Return evidence changes only through its owner module.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Security Return evidence is retained.")


class SecurityReturnItem(models.Model):
    TYPES = ("sh4", "blank_cheque", "poa", "cdsl")
    STATUSES = (
        "not_applicable",
        "pending",
        "returned",
        "released",
        "rejected",
        "completed",
    )

    security_return_item_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    security_return = models.ForeignKey(
        SecurityReturn, on_delete=models.PROTECT, related_name="items"
    )
    item_type = models.CharField(max_length=40)
    item_status = models.CharField(max_length=40, db_index=True)
    source_item_id = models.UUIDField(blank=True, null=True)
    custody_location = models.CharField(max_length=255, blank=True, null=True)
    returned_released_by_user = models.ForeignKey(
        "identity.User",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="security_return_items_released",
    )
    returned_released_to = models.CharField(max_length=255, blank=True, null=True)
    returned_released_at = models.DateTimeField(blank=True, null=True)
    pending_reason = models.TextField(blank=True, null=True)
    acknowledgement_document = models.ForeignKey(
        "documents.DocumentFile",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="security_return_item_acknowledgements",
    )
    psn = models.CharField(max_length=120, blank=True, null=True)
    urf_document = models.ForeignKey(
        "documents.DocumentFile",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="security_return_urfs",
    )
    urf_date = models.DateField(blank=True, null=True)
    unpledge_type = models.CharField(max_length=20, blank=True, null=True)
    pledgor_dp_submitted_at = models.DateTimeField(blank=True, null=True)
    pledgee_dp_acted_at = models.DateTimeField(blank=True, null=True)
    pledgee_dp_outcome = models.CharField(max_length=20, blank=True, null=True)
    auto_unpledge_flag = models.BooleanField(blank=True, null=True)
    completion_evidence_document = models.ForeignKey(
        "documents.DocumentFile",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="security_return_completion_evidence",
    )
    completed_at = models.DateTimeField(blank=True, null=True)
    transition_audit = models.OneToOneField(
        "identity.AuditLog",
        on_delete=models.PROTECT,
        related_name="security_return_item_transition",
    )

    objects = ImmutableSecurityReturnQuerySet.as_manager()

    class Meta:
        db_table = "security_return_items"
        constraints = [
            models.UniqueConstraint(
                fields=["security_return", "item_type"],
                name="uniq_security_return_item_type",
            ),
            models.CheckConstraint(
                check=models.Q(item_type__in=("sh4", "blank_cheque", "poa", "cdsl")),
                name="security_return_item_type_bounded",
            ),
            models.CheckConstraint(
                check=models.Q(
                    item_status__in=(
                        "not_applicable",
                        "pending",
                        "returned",
                        "released",
                        "rejected",
                        "completed",
                    )
                ),
                name="security_return_item_status_bounded",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise ValueError(
                "Security Return item evidence changes only through its owner module."
            )
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Security Return item evidence is retained.")


class SecurityReturnRequest(models.Model):
    security_return_request_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    security_return = models.ForeignKey(
        SecurityReturn, on_delete=models.PROTECT, related_name="requests"
    )
    idempotency_key_digest = models.CharField(max_length=64, unique=True)
    payload_digest = models.CharField(max_length=64)
    resulting_version = models.PositiveIntegerField()
    created_at = models.DateTimeField(default=timezone.now)

    objects = ImmutableSecurityReturnQuerySet.as_manager()

    class Meta:
        db_table = "security_return_requests"

    def save(self, *args, **kwargs):
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise ValueError("Security Return request evidence is immutable.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Security Return request evidence is retained.")
