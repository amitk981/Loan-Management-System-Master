# Tri-party verification API evidence

Request exercised by `TriPartyAgreementApiTests.test_company_secretary_verifies_applicable_current_signed_agreement`:

```http
POST /api/v1/loan-documents/8ecf0000-0000-4000-8000-000000000001/verify/
X-Request-ID: req-tri-party-verify
Content-Type: application/json

{
  "verification_status": "verified",
  "remarks": "Borrower and nominee execution verified."
}
```

Contract response (UUID/timestamp illustrative; exact shape asserted by the test):

```json
{
  "success": true,
  "data": {
    "loan_document_id": "8ecf0000-0000-4000-8000-000000000001",
    "loan_application_id": "8ecf0000-0000-4000-8000-000000000002",
    "document_type": "tri_party_agreement",
    "verification_status": "verified",
    "verified_by_user_id": "8ecf0000-0000-4000-8000-000000000003",
    "verified_at": "2026-07-14T13:00:00Z",
    "remarks": "Borrower and nominee execution verified."
  },
  "meta": {
    "request_id": "req-tri-party-verify",
    "timestamp": "2026-07-14T13:00:00Z",
    "api_version": "v1"
  }
}
```

The same test proves the exact current-renderer document retained two distinct canonical signed
rows, the frozen subsidiary route was true, one attributable audit/version/workflow transition was
written, and checklist completion/verifier/remarks remained unchanged. The replay/read test proves
exact replay is zero-write and both loan-document and checklist reads expose verification metadata
without changing package or readiness facts.
