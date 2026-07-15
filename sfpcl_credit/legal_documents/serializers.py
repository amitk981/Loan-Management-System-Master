"""HTTP request-shape adapters for legal-document routes.

The value objects live below the HTTP seam so direct module callers can cross the same strict
contract without any business module depending on this transport adapter.
"""

from sfpcl_credit.legal_documents.request_contracts import (
    ChecklistApprovalRequest,
    ChecklistItemCompletionRequest,
    LoanDocumentVerificationRequest,
    NotarisationRecordRequest,
    SignatureMismatchResolutionRequest,
    SignatureRecordRequest,
    StampDutyRecordRequest,
)

__all__ = [
    "ChecklistApprovalRequest",
    "ChecklistItemCompletionRequest",
    "LoanDocumentVerificationRequest",
    "NotarisationRecordRequest",
    "SignatureMismatchResolutionRequest",
    "SignatureRecordRequest",
    "StampDutyRecordRequest",
]
