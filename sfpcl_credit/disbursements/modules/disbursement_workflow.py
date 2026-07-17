from sfpcl_credit.disbursements.modules.disbursement_initiation import (
    DisbursementConflict,
    DisbursementReadinessStale,
    _initiate,
)
from sfpcl_credit.disbursements.modules.disbursement_authorisation import (
    DisbursementAuthorisationConflict,
    _authorise,
)
from sfpcl_credit.disbursements.modules.disbursement_readiness import (
    DisbursementReadinessModule,
)
from sfpcl_credit.disbursements.modules.disbursement_transfer_success import (
    DisbursementTransferConflict,
    DuplicateBankReference,
    _mark_transfer_successful,
)
from sfpcl_credit.disbursements.modules.disbursement_advice import (
    DisbursementAdviceConflict,
    DisbursementAdviceDeliveryFailed,
    _send_advice,
)


class DisbursementWorkflow:
    """Public owner for payment initiation and its later maker-checker lifecycle."""

    readiness = DisbursementReadinessModule
    initiate = staticmethod(_initiate)
    authorise = staticmethod(_authorise)
    mark_transfer_successful = staticmethod(_mark_transfer_successful)
    send_advice = staticmethod(_send_advice)


__all__ = [
    "DisbursementConflict",
    "DisbursementAuthorisationConflict",
    "DisbursementReadinessStale",
    "DisbursementTransferConflict",
    "DuplicateBankReference",
    "DisbursementAdviceConflict",
    "DisbursementAdviceDeliveryFailed",
    "DisbursementWorkflow",
]
