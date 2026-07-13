"""Keep the approval selector's coherence projection aligned with credit facts."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from sfpcl_credit.approvals.models import ApprovalCase
from sfpcl_credit.approvals.modules.approval_case_projection import (
    refresh_approval_case_projection,
)


@receiver(post_save, sender="credit.LoanAppraisalNote")
def refresh_case_routing_coherence_after_appraisal_save(sender, instance, **kwargs):
    cases = (
        ApprovalCase.objects.select_related("loan_application", "loan_appraisal_note")
        .filter(loan_appraisal_note=instance)
    )
    for case in cases:
        refresh_approval_case_projection(case)
