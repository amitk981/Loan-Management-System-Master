import uuid

from django.db import models
from django.utils import timezone


class ApprovalCase(models.Model):
    TYPE_SANCTION = "sanction"
    STATUS_PENDING = "pending"

    approval_case_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    loan_application = models.OneToOneField(
        "applications.LoanApplication",
        on_delete=models.PROTECT,
        related_name="sanction_approval_case",
    )
    loan_appraisal_note = models.OneToOneField(
        "credit.LoanAppraisalNote",
        on_delete=models.PROTECT,
        related_name="sanction_approval_case",
    )
    approval_type = models.CharField(max_length=80, default=TYPE_SANCTION, db_index=True)
    current_status = models.CharField(max_length=60, default=STATUS_PENDING, db_index=True)
    exception_required_flag = models.BooleanField(default=False, db_index=True)
    submission_remarks = models.TextField()
    submitted_by_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="submitted_sanction_cases",
    )
    submitted_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = "approval_cases"
        indexes = [
            models.Index(
                fields=["approval_type", "current_status"],
                name="idx_approval_type_status",
            ),
            models.Index(
                fields=["exception_required_flag", "current_status"],
                name="idx_approval_exception",
            ),
        ]
