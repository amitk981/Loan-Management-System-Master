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
    authorisation_comments = models.CharField(max_length=2000, null=True, blank=True)
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
    bank_transfer_evidence_document = models.ForeignKey(
        "documents.DocumentFile",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="evidenced_disbursements",
    )
    transfer_success_action_id = models.UUIDField(null=True, blank=True, unique=True)
    transfer_success_actor_user = models.ForeignKey(
        "identity.User",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="successful_disbursement_transfers",
    )
    transfer_success_role_code = models.CharField(max_length=80, null=True, blank=True)
    transfer_success_team_codes_json = models.JSONField(null=True, blank=True)
    transfer_success_idempotency_key_digest = models.CharField(
        max_length=64, null=True, blank=True, unique=True
    )
    transfer_success_payload_digest = models.CharField(
        max_length=64, null=True, blank=True
    )
    transfer_success_evidence_digest = models.CharField(
        max_length=64, null=True, blank=True
    )
    transfer_success_request_id = models.CharField(
        max_length=255, null=True, blank=True
    )
    transfer_success_ip_address = models.CharField(
        max_length=80, null=True, blank=True
    )
    transfer_success_user_agent = models.TextField(null=True, blank=True)
    transfer_success_audit = models.OneToOneField(
        "identity.AuditLog",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="disbursement_transfer_success",
    )
    transfer_success_workflow_event = models.OneToOneField(
        "workflows.WorkflowEvent",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="disbursement_transfer_success",
    )
    transfer_success_loan_status_history = models.OneToOneField(
        "loans.LoanStatusHistory",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="disbursement_transfer_success",
    )
    disbursement_advice_communication = models.ForeignKey(
        "communications.Communication",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="advised_disbursements",
    )
    loan_register_updated_flag = models.BooleanField(default=False)
    register_update = models.OneToOneField(
        "LoanRegisterUpdate",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="owned_by_successful_disbursement",
    )
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
                        authorisation_comments__isnull=True,
                        checker_role_code__isnull=True,
                        checker_team_codes_json__isnull=True,
                        authorisation_action_id__isnull=True,
                        authorisation_evidence_digest__isnull=True,
                        authorisation_request_id__isnull=True,
                        authorisation_ip_address__isnull=True,
                        authorisation_user_agent__isnull=True,
                        authorisation_audit__isnull=True,
                        authorisation_workflow_event__isnull=True,
                    )
                    | Q(
                        authorisation_status__in=("approved", "rejected"),
                        authorised_by_user__isnull=False,
                        authorised_at__isnull=False,
                        authorisation_comments__isnull=False,
                        checker_role_code="chief_financial_controller",
                        checker_team_codes_json__isnull=False,
                        authorisation_action_id__isnull=False,
                        authorisation_evidence_digest__isnull=False,
                        authorisation_request_id__isnull=False,
                        authorisation_ip_address__isnull=False,
                        authorisation_user_agent__isnull=False,
                        authorisation_audit__isnull=False,
                        authorisation_workflow_event__isnull=False,
                    )
                )
                & (Q(authorisation_comments__isnull=True) | ~Q(authorisation_comments="")),
                name="disb_auth_terminal_evidence",
            ),
            models.CheckConstraint(
                check=(
                    Q(authorisation_status="approved")
                    | Q(
                        bank_transfer_status="pending",
                        bank_reference_number__isnull=True,
                        disbursed_at__isnull=True,
                        disbursement_advice_communication__isnull=True,
                        loan_register_updated_flag=False,
                    )
                ),
                name="disb_transfer_requires_approval",
            ),
            models.CheckConstraint(
                check=(
                    Q(
                        bank_transfer_status="successful",
                        authorisation_status="approved",
                        bank_reference_number__isnull=False,
                        disbursed_at__isnull=False,
                        bank_transfer_evidence_document__isnull=False,
                        transfer_success_action_id__isnull=False,
                        transfer_success_actor_user__isnull=False,
                        transfer_success_role_code__isnull=False,
                        transfer_success_team_codes_json__isnull=False,
                        transfer_success_idempotency_key_digest__isnull=False,
                        transfer_success_payload_digest__isnull=False,
                        transfer_success_evidence_digest__isnull=False,
                        transfer_success_request_id__isnull=False,
                        transfer_success_ip_address__isnull=False,
                        transfer_success_user_agent__isnull=False,
                        transfer_success_audit__isnull=False,
                        transfer_success_workflow_event__isnull=False,
                        transfer_success_loan_status_history__isnull=False,
                        loan_register_updated_flag=True,
                        register_update__isnull=False,
                    )
                    | Q(
                        bank_transfer_status__in=(
                            "pending",
                            "processing",
                            "failed",
                            "reversed",
                        ),
                        bank_transfer_evidence_document__isnull=True,
                        transfer_success_action_id__isnull=True,
                        transfer_success_actor_user__isnull=True,
                        transfer_success_role_code__isnull=True,
                        transfer_success_team_codes_json__isnull=True,
                        transfer_success_idempotency_key_digest__isnull=True,
                        transfer_success_payload_digest__isnull=True,
                        transfer_success_evidence_digest__isnull=True,
                        transfer_success_request_id__isnull=True,
                        transfer_success_ip_address__isnull=True,
                        transfer_success_user_agent__isnull=True,
                        transfer_success_audit__isnull=True,
                        transfer_success_workflow_event__isnull=True,
                        transfer_success_loan_status_history__isnull=True,
                        loan_register_updated_flag=False,
                        register_update__isnull=True,
                    )
                ),
                name="disb_success_evidence_complete",
            ),
            models.CheckConstraint(
                check=(
                    ~Q(bank_transfer_status="pending")
                    | Q(
                        bank_reference_number__isnull=True,
                        disbursed_at__isnull=True,
                        bank_transfer_evidence_document__isnull=True,
                    )
                ),
                name="disb_pending_has_no_transfer",
            ),
            models.UniqueConstraint(
                fields=["loan_account"],
                condition=Q(authorisation_status__in=("pending", "approved"))
                & Q(bank_transfer_status__in=("pending", "processing")),
                name="uniq_active_disb_account",
            ),
        ]


class BankTransfer(models.Model):
    bank_transfer_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    disbursement = models.OneToOneField(
        Disbursement, on_delete=models.PROTECT, related_name="bank_transfer"
    )
    loan_account = models.OneToOneField(
        "loans.LoanAccount",
        on_delete=models.PROTECT,
        related_name="successful_bank_transfer",
    )
    transfer_type = models.CharField(max_length=60, default="disbursement")
    related_entity_type = models.CharField(max_length=80, default="disbursement")
    related_entity_id = models.UUIDField(db_index=True)
    source_bank_account = models.ForeignKey(
        "members.BankAccount",
        on_delete=models.PROTECT,
        related_name="outgoing_bank_transfers",
    )
    destination_bank_account = models.ForeignKey(
        "members.BankAccount",
        on_delete=models.PROTECT,
        related_name="incoming_bank_transfers",
    )
    evidence_document = models.ForeignKey(
        "documents.DocumentFile",
        on_delete=models.PROTECT,
        related_name="evidenced_bank_transfers",
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    payment_method = models.CharField(max_length=60, default="manual")
    bank_reference_number = models.CharField(max_length=120)
    bank_reference_number_normalized = models.CharField(max_length=120, unique=True)
    bank_status = models.CharField(max_length=60, default="successful", db_index=True)
    initiated_at = models.DateTimeField()
    completed_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "bank_transfers"
        indexes = [
            models.Index(
                fields=["transfer_type", "related_entity_id"],
                name="idx_bank_transfer_related",
            ),
            models.Index(
                fields=["bank_status", "completed_at"],
                name="idx_bank_transfer_status",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(amount__gt=0), name="bank_transfer_amount_positive"
            ),
            models.CheckConstraint(
                check=Q(
                    transfer_type="disbursement",
                    related_entity_type="disbursement",
                    payment_method="manual",
                    bank_status="successful",
                ),
                name="bank_transfer_manual_success",
            ),
            models.CheckConstraint(
                check=Q(completed_at__gte=models.F("initiated_at")),
                name="bank_transfer_time_order",
            ),
            models.CheckConstraint(
                check=~Q(bank_reference_number="")
                & ~Q(bank_reference_number_normalized=""),
                name="bank_transfer_reference_present",
            ),
        ]


class LoanRegisterUpdate(models.Model):
    loan_register_update_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    disbursement = models.OneToOneField(
        Disbursement, on_delete=models.PROTECT, related_name="loan_register_update"
    )
    bank_transfer = models.OneToOneField(
        BankTransfer, on_delete=models.PROTECT, related_name="loan_register_update"
    )
    loan_account = models.ForeignKey(
        "loans.LoanAccount", on_delete=models.PROTECT,
        related_name="loan_register_updates",
    )
    loan_application = models.ForeignKey(
        "applications.LoanApplication", on_delete=models.PROTECT,
        related_name="loan_register_updates",
    )
    member = models.ForeignKey(
        "members.Member", on_delete=models.PROTECT,
        related_name="loan_register_updates",
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    bank_reference_digest = models.CharField(max_length=64)
    evidence_document = models.ForeignKey(
        "documents.DocumentFile", on_delete=models.PROTECT,
        related_name="loan_register_updates",
    )
    evidence_checksum_sha256 = models.CharField(max_length=128)
    transfer_action_id = models.UUIDField(unique=True)
    transfer_evidence_digest = models.CharField(max_length=64)
    transfer_audit = models.ForeignKey(
        "identity.AuditLog", on_delete=models.PROTECT,
        related_name="loan_register_updates",
    )
    transfer_workflow_event = models.ForeignKey(
        "workflows.WorkflowEvent", on_delete=models.PROTECT,
        related_name="loan_register_updates",
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "loan_register_updates"
        constraints = [
            models.CheckConstraint(
                check=Q(amount__gt=0), name="loan_register_amount_positive"
            ),
            models.CheckConstraint(
                check=~Q(bank_reference_digest="") & ~Q(evidence_checksum_sha256=""),
                name="loan_register_evidence_present",
            ),
        ]


class DisbursementAdviceIntent(models.Model):
    DELIVERY_PENDING = "pending"
    DELIVERY_SENT = "sent"
    advice_intent_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    disbursement = models.OneToOneField(
        Disbursement, on_delete=models.PROTECT, related_name="advice_intent"
    )
    bank_transfer = models.OneToOneField(
        BankTransfer, on_delete=models.PROTECT, related_name="advice_intent"
    )
    loan_account = models.ForeignKey(
        "loans.LoanAccount", on_delete=models.PROTECT,
        related_name="disbursement_advice_intents",
    )
    loan_application = models.ForeignKey(
        "applications.LoanApplication", on_delete=models.PROTECT,
        related_name="disbursement_advice_intents",
    )
    member = models.ForeignKey(
        "members.Member", on_delete=models.PROTECT,
        related_name="disbursement_advice_intents",
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    bank_reference_digest = models.CharField(max_length=64)
    evidence_document = models.ForeignKey(
        "documents.DocumentFile", on_delete=models.PROTECT,
        related_name="disbursement_advice_intents",
    )
    evidence_checksum_sha256 = models.CharField(max_length=128)
    transfer_action_id = models.UUIDField(unique=True)
    transfer_evidence_digest = models.CharField(max_length=64)
    transfer_audit = models.ForeignKey(
        "identity.AuditLog", on_delete=models.PROTECT,
        related_name="disbursement_advice_intents",
    )
    transfer_workflow_event = models.ForeignKey(
        "workflows.WorkflowEvent", on_delete=models.PROTECT,
        related_name="disbursement_advice_intents",
    )
    delivery_status = models.CharField(max_length=40, default=DELIVERY_PENDING)
    delivery_action_id = models.UUIDField(blank=True, null=True, unique=True)
    delivery_evidence_digest = models.CharField(max_length=64, blank=True, default="")
    delivery_audit = models.ForeignKey(
        "identity.AuditLog",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="delivered_disbursement_advice_intents",
    )
    delivery_workflow_event = models.ForeignKey(
        "workflows.WorkflowEvent",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="delivered_disbursement_advice_intents",
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "disbursement_advice_intents"
        constraints = [
            models.CheckConstraint(
                check=Q(amount__gt=0), name="advice_intent_amount_positive"
            ),
            models.CheckConstraint(
                check=Q(delivery_status__in=("pending", "sent")),
                name="advice_intent_status_valid",
            ),
            models.CheckConstraint(
                check=~Q(bank_reference_digest="") & ~Q(evidence_checksum_sha256=""),
                name="advice_intent_evidence_present",
            ),
            models.CheckConstraint(
                check=(
                    Q(
                        delivery_status="pending",
                        delivery_action_id__isnull=True,
                        delivery_evidence_digest="",
                        delivery_audit__isnull=True,
                        delivery_workflow_event__isnull=True,
                    )
                    | (
                        Q(
                            delivery_status="sent",
                            delivery_action_id__isnull=False,
                            delivery_audit__isnull=False,
                            delivery_workflow_event__isnull=False,
                        )
                        & ~Q(delivery_evidence_digest="")
                    )
                ),
                name="advice_intent_delivery_evidence_complete",
            ),
        ]


from sfpcl_credit.communications.models import (  # noqa: E402
    DisbursementAdviceDeliveryReceipt,
)
