# Sanitized 009E API and Ledger Evidence

The focused API test executes this contract through Django's public HTTP boundary. Identifiers below
are deliberately synthetic; the assertions also prove encrypted account values/hashes never appear
in the response, audit, workflow, or CFC task.

## Request

```http
POST /api/v1/loan-accounts/11111111-1111-4111-8111-111111111111/disbursements/initiate/
Idempotency-Key: initiation-example-001
Content-Type: application/json

{
  "disbursement_amount": "400000.00",
  "borrower_bank_account_id": "22222222-2222-4222-8222-222222222222",
  "source_bank_account_id": "33333333-3333-4333-8333-333333333333",
  "final_verification_comments": "Final facts verified."
}
```

## Response

```json
{
  "success": true,
  "data": {
    "disbursement_id": "44444444-4444-4444-8444-444444444444",
    "initiation_status": "initiated",
    "authorisation_status": "pending",
    "bank_transfer_status": "pending"
  },
  "meta": {
    "request_id": "request-example-001",
    "timestamp": "2026-07-17T02:00:00Z",
    "api_version": "v1"
  }
}
```

## Safe retained ledger shape

```json
{
  "action": "disbursement.initiated",
  "entity_type": "disbursement",
  "loan_account_id": "11111111-1111-4111-8111-111111111111",
  "disbursement_amount": "400000.00",
  "initiation_status": "initiated",
  "authorisation_status": "pending",
  "bank_transfer_status": "pending",
  "payment_method": "manual",
  "maker_role_codes": ["senior_manager_finance"],
  "cfc_assignment_role_code": "chief_financial_controller",
  "readiness_digest": "64-character-sha256-digest",
  "idempotency_digest": "64-character-sha256-digest",
  "outcome": "initiated"
}
```

The exact retained ledger also includes safe borrower/source-bank ids and current SAP/readiness
evidence ids, but never account plaintext, PAN/Aadhaar, document URLs/capabilities, UTR, transfer,
funding, activation, register, advice, or borrower-notification truth.
