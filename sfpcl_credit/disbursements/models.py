import uuid

from django.db import models
from django.db.models import Q
from django.utils import timezone


class Disbursement(models.Model):
    INITIATED = "initiated"
    AUTHORISATION_PENDING = "pending"
    TRANSFER_PENDING = "pending"
    PAYMENT_METHOD_MANUAL = "manual"

    disbursement_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    loan_account = models.ForeignKey(
        "loans.LoanAccount", on_delete=models.PROTECT, related_name="disbursements"
    )
    loan_application = models.ForeignKey(
        "applications.LoanApplication",
        on_delete=models.PROTECT,
        related_name="disbursements",
    )
    member = models.ForeignKey(
        "members.Member", on_delete=models.PROTECT, related_name="disbursements"
    )
    disbursement_amount = models.DecimalField(max_digits=18, decimal_places=2)
    borrower_bank_account = models.ForeignKey(
        "members.BankAccount",
        on_delete=models.PROTECT,
        related_name="borrower_disbursements",
    )
    source_bank_account = models.ForeignKey(
        "members.BankAccount",
        on_delete=models.PROTECT,
        related_name="source_disbursements",
    )
    initiated_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="initiated_disbursements",
    )
    authorised_by_user = models.ForeignKey(
        "identity.User",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="authorised_disbursements",
    )
    authorised_at = models.DateTimeField(null=True, blank=True, db_index=True)
    authorisation_comments = models.TextField(null=True, blank=True)
    checker_role_code = models.CharField(max_length=80, null=True, blank=True)
    checker_team_codes_json = models.JSONField(null=True, blank=True)
    authorisation_action_id = models.UUIDField(null=True, blank=True, unique=True)
    authorisation_evidence_digest = models.CharField(
        max_length=64, null=True, blank=True
    )
    authorisation_request_id = models.CharField(max_length=255, null=True, blank=True)
    authorisation_ip_address = models.CharField(max_length=80, null=True, blank=True)
    authorisation_user_agent = models.TextField(null=True, blank=True)
    authorisation_audit = models.OneToOneField(
        "identity.AuditLog",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="disbursement_authorisation",
    )
    authorisation_workflow_event = models.OneToOneField(
        "workflows.WorkflowEvent",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="disbursement_authorisation",
    )
    initiation_status = models.CharField(max_length=60, default=INITIATED, db_index=True)
    authorisation_status = models.CharField(
        max_length=60, default=AUTHORISATION_PENDING, db_index=True
    )
    bank_transfer_status = models.CharField(
        max_length=60, default=TRANSFER_PENDING, db_index=True
    )
    payment_method = models.CharField(max_length=40, default=PAYMENT_METHOD_MANUAL)
    final_verification_comments = models.TextField()
    idempotency_key_digest = models.CharField(max_length=64, unique=True)
    payload_digest = models.CharField(max_length=64)
    readiness_digest = models.CharField(max_length=64)
    readiness_evidence_json = models.JSONField()
    maker_role_code = models.CharField(max_length=80)
    maker_team_codes_json = models.JSONField(default=list)
    initiated_at = models.DateTimeField(default=timezone.now, db_index=True)
    cfc_task = models.OneToOneField(
        "communications.Notification",
        on_delete=models.PROTECT,
        related_name="disbursement_initiation",
    )
    initiation_audit = models.OneToOneField(
        "identity.AuditLog",
        on_delete=models.PROTECT,
        related_name="disbursement_initiation",
    )
    initiation_workflow_event = models.OneToOneField(
        "workflows.WorkflowEvent",
        on_delete=models.PROTECT,
        related_name="disbursement_initiation",
    )
    bank_reference_number = models.CharField(
        max_length=120, null=True, blank=True, db_index=True
    )
    disbursed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    disbursement_advice_communication = models.ForeignKey(
        "communications.Communication",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="advised_disbursements",
    )
    loan_register_updated_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "disbursements"
        indexes = [
            models.Index(
                fields=["loan_account", "initiation_status"],
                name="idx_disb_account_status",
            ),
            models.Index(
                fields=["authorisation_status", "created_at"],
                name="idx_disb_auth_created",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(disbursement_amount__gt=0), name="disb_amount_positive"
            ),
            models.CheckConstraint(
                check=Q(initiation_status__in=("pending", "initiated")),
                name="disb_init_status_valid",
            ),
            models.CheckConstraint(
                check=Q(authorisation_status__in=("pending", "approved", "rejected")),
                name="disb_auth_status_valid",
            ),
            models.CheckConstraint(
                check=Q(
                    bank_transfer_status__in=(
                        "pending",
                        "processing",
                        "successful",
                        "failed",
                        "reversed",
                    )
                ),
                name="disb_transfer_status_valid",
            ),
            models.CheckConstraint(
                check=Q(payment_method="manual"),
                name="disb_method_manual",
            ),
            models.CheckConstraint(
                check=Q(authorised_by_user__isnull=True)
                | ~Q(authorised_by_user=models.F("initiated_by_user")),
                name="disb_maker_checker_distinct",
            ),
            models.CheckConstraint(
                check=(
                    Q(
                        authorisation_status="pending",
                        authorised_by_user__isnull=True,
                        authorised_at__isnull=True,
                        authorisation_action_id__isnull=True,
                        authorisation_audit__isnull=True,
                        authorisation_workflow_event__isnull=True,
                    )
                    | Q(
                        authorisation_status__in=("approved", "rejected"),
                        authorised_by_user__isnull=False,
                        authorised_at__isnull=False,
                        authorisation_action_id__isnull=False,
                        authorisation_audit__isnull=False,
                        authorisation_workflow_event__isnull=False,
                    )
                ),
                name="disb_auth_terminal_evidence",
            ),
            models.UniqueConstraint(
                fields=["loan_account"],
                condition=Q(authorisation_status__in=("pending", "approved"))
                & Q(bank_transfer_status__in=("pending", "processing")),
                name="uniq_active_disb_account",
            ),
        ]
