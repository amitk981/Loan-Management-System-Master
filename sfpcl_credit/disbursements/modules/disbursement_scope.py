from sfpcl_credit.disbursements.models import Disbursement


def has_cfc_scope(*, actor_id, loan_account_id):
    return Disbursement.objects.filter(
        loan_account_id=loan_account_id,
        initiation_status=Disbursement.INITIATED,
        authorisation_status=Disbursement.AUTHORISATION_PENDING,
        bank_transfer_status=Disbursement.TRANSFER_PENDING,
        cfc_task__recipient_role_code="chief_financial_controller",
    ).exists()
