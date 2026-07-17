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


class DisbursementWorkflow:
    """Public owner for payment initiation and its later maker-checker lifecycle."""

    readiness = DisbursementReadinessModule
    initiate = staticmethod(_initiate)
    authorise = staticmethod(_authorise)


__all__ = [
    "DisbursementConflict",
    "DisbursementAuthorisationConflict",
    "DisbursementReadinessStale",
    "DisbursementWorkflow",
]
