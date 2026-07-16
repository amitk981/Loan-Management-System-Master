import uuid

from django.db import models
from django.db.models.functions import Lower, Trim
from django.utils import timezone


class SapCustomerProfileRequest(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_SENT = "sent"
    STATUS_COMPLETED = "completed"
    ACTIVE_STATUSES = (STATUS_DRAFT, STATUS_SENT)

    sap_customer_profile_request_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    loan_application = models.ForeignKey(
        "applications.LoanApplication", on_delete=models.PROTECT,
        related_name="sap_customer_profile_requests",
    )
    member = models.ForeignKey(
        "members.Member", on_delete=models.PROTECT,
        related_name="sap_customer_profile_requests",
    )
    request_status = models.CharField(max_length=60, default=STATUS_DRAFT, db_index=True)
    requested_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="requested_sap_profiles"
    )
    assigned_to_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="assigned_sap_profiles"
    )
    farmer_full_name = models.CharField(max_length=255)
    borrower_type = models.CharField(max_length=60)
    folio_number = models.CharField(max_length=100)
    aadhaar_number_encrypted = models.TextField(blank=True)
    pan_number_encrypted = models.TextField()
    address_text = models.TextField()
    email_id = models.EmailField(blank=True)
    mobile_number = models.CharField(max_length=20, blank=True)
    loan_application_number = models.CharField(max_length=40)
    sanctioned_amount = models.DecimalField(max_digits=18, decimal_places=2)
    sanction_date = models.DateField()
    bank_account_last4 = models.CharField(max_length=4, blank=True)
    ifsc = models.CharField(max_length=20, blank=True)
    excel_file = models.ForeignKey(
        "documents.DocumentFile", on_delete=models.PROTECT,
        related_name="sap_customer_profile_requests",
    )
    sanction_decision_id_snapshot = models.UUIDField(null=True, blank=True)
    sanction_approval_case_id_snapshot = models.UUIDField(null=True, blank=True)
    sent_remarks = models.TextField(blank=True)
    sent_communication = models.ForeignKey(
        "communications.Communication", null=True, blank=True, on_delete=models.PROTECT,
        related_name="sap_customer_profile_requests",
    )
    sent_task = models.ForeignKey(
        "communications.Notification", null=True, blank=True, on_delete=models.PROTECT,
        related_name="sap_customer_profile_requests",
    )
    sap_customer_code = models.ForeignKey(
        "SapCustomerCode", null=True, blank=True, on_delete=models.PROTECT,
        related_name="completed_profile_requests",
    )
    completion_reused_existing_code = models.BooleanField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "sap_customer_profile_requests"
        indexes = [
            models.Index(fields=["loan_application"], name="idx_sap_req_application"),
            models.Index(fields=["member"], name="idx_sap_req_member"),
            models.Index(fields=["assigned_to_user", "request_status"], name="idx_sap_req_assignee_status"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["loan_application"],
                condition=models.Q(request_status__in=("draft", "sent")),
                name="uniq_active_sap_request_app",
            ),
            models.CheckConstraint(
                check=models.Q(request_status__in=("draft", "sent", "completed")),
                name="sap_request_status_valid",
            ),
            models.CheckConstraint(
                check=models.Q(sanctioned_amount__gt=0),
                name="sap_request_amount_positive",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(
                        request_status="draft", sent_at__isnull=True,
                        sent_communication__isnull=True, sent_task__isnull=True,
                        completed_at__isnull=True, sap_customer_code__isnull=True,
                        completion_reused_existing_code__isnull=True,
                    )
                    | models.Q(
                        request_status="sent", sent_at__isnull=False,
                        sent_communication__isnull=False, sent_task__isnull=False,
                        completed_at__isnull=True, sap_customer_code__isnull=True,
                        completion_reused_existing_code__isnull=True,
                    )
                    | models.Q(
                        request_status="completed", sent_at__isnull=False,
                        sent_communication__isnull=False, sent_task__isnull=False,
                        completed_at__isnull=False, sap_customer_code__isnull=False,
                        completion_reused_existing_code__isnull=False,
                    )
                ),
                name="sap_request_lifecycle_evidence",
            ),
        ]


class SapCustomerCode(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"

    sap_customer_code_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    member = models.ForeignKey(
        "members.Member", on_delete=models.PROTECT, related_name="sap_customer_codes"
    )
    sap_customer_code = models.CharField(max_length=120, unique=True)
    sap_vendor_code = models.CharField(max_length=120, blank=True)
    created_for_loan_application = models.ForeignKey(
        "applications.LoanApplication", on_delete=models.PROTECT,
        related_name="created_sap_customer_codes",
    )
    created_by_user = models.ForeignKey(
        "identity.User", on_delete=models.PROTECT, related_name="created_sap_customer_codes"
    )
    created_at_sap = models.DateTimeField(null=True, blank=True)
    confirmation_document = models.ForeignKey(
        "documents.DocumentFile", null=True, blank=True, on_delete=models.PROTECT,
        related_name="confirmed_sap_customer_codes",
    )
    confirmation_notes = models.TextField(blank=True)
    status = models.CharField(max_length=40, default=STATUS_ACTIVE, db_index=True)

    class Meta:
        db_table = "sap_customer_codes"
        indexes = [models.Index(fields=["member", "status"], name="idx_sap_code_member_status")]
        constraints = [
            models.UniqueConstraint(
                fields=["member"], condition=models.Q(status="active"),
                name="uniq_active_sap_code_member",
            ),
            models.CheckConstraint(
                check=models.Q(status__in=("active", "inactive")),
                name="sap_customer_code_status_valid",
            ),
            models.CheckConstraint(
                check=~models.Q(sap_customer_code=""),
                name="sap_customer_code_not_blank",
            ),
            models.UniqueConstraint(
                Lower(Trim("sap_customer_code")), name="uniq_sap_customer_code_ci",
            ),
        ]
