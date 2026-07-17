from sfpcl_credit.disbursements.modules.current_disbursement_evidence import (
    resolve_current_disbursement_evidence,
)


def has_cfc_scope(*, actor_id, loan_account_id):
    """CFC scope exists only for the singular exact current initiation decision."""
    del actor_id  # authority is enforced by the calling loan/readiness boundary
    return (
        resolve_current_disbursement_evidence(loan_account_id=loan_account_id)
        is not None
    )
