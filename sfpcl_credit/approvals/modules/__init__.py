"""Public approvals-module interfaces."""
from sfpcl_credit.approvals.modules import approval_matrix_configuration
from sfpcl_credit.approvals.modules.approval_matrix import (
    AmbiguousApprovalRule,
    ApprovalMatrixProjection,
    InvalidApprovalFacts,
    NoEffectiveApprovalRule,
    resolve_approval_matrix,
)

__all__ = [
    "AmbiguousApprovalRule",
    "ApprovalMatrixProjection",
    "InvalidApprovalFacts",
    "NoEffectiveApprovalRule",
    "approval_matrix_configuration",
    "resolve_approval_matrix",
]
