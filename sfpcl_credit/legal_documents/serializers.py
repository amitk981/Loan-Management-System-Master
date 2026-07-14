"""HTTP request-shape adapters for legal-document routes.

The value objects live below the HTTP seam so direct module callers can cross the same strict
contract without any business module depending on this transport adapter.
"""

from sfpcl_credit.legal_documents.request_contracts import (
    LoanDocumentVerificationRequest,
    NotarisationRecordRequest,
    PowerOfAttorneyRequest,
    SignatureMismatchResolutionRequest,
    SignatureRecordRequest,
    StampDutyRecordRequest,
)

__all__ = [
    "LoanDocumentVerificationRequest",
    "NotarisationRecordRequest",
    "PowerOfAttorneyRequest",
    "SignatureMismatchResolutionRequest",
    "SignatureRecordRequest",
    "StampDutyRecordRequest",
]
