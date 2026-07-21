# Borrower-safe response examples

These representative shapes are asserted by
`sfpcl_credit.tests.test_portal_loan_accounts_api.PortalLoanAccountsApiTests`.

```json
{
  "loan_account_id": "<own-account-uuid>",
  "loan_account_number": "LN-PORTAL-001",
  "status": "active",
  "principal_outstanding": "300000.00",
  "next_due_date": "2026-12-31",
  "next_due_amount": "100000.00"
}
```

```json
{
  "repayment_id": "<posted-repayment-uuid>",
  "receipt_date": "2026-12-01",
  "amount_received": "100000.00",
  "allocated_to_principal": "100000.00",
  "allocated_to_interest": "0.00",
  "payment_mode": "neft",
  "reference": "UTR-Direct-001",
  "acknowledgement": null,
  "status": "confirmed"
}
```

```json
{
  "available": true,
  "beneficiary_name": "SFPCL Collections",
  "bank_name": "Approved Bank",
  "account_number_masked": "********4321",
  "ifsc": "APPR0001234",
  "required_narration": "LN-PORTAL-001",
  "amount_due": "300000.00",
  "proof_submission_enabled": false
}
```

Internal actors, audit evidence, SAP notes/status, provider data, receipt remarks, full bank account
numbers, exception notes, pending/unmatched receipts, and foreign object identities are absent.
