# API Response Examples

## Direct receipt created

```json
{"success":true,"data":{"repayment_id":"uuid","loan_account_id":"uuid","repayment_source":"direct_farmer","amount_received":"100000.00","received_date":"2026-12-01","payment_method":"neft","bank_reference_number":"UTR-Direct-001","allocation_status":"pending","sap_posting":{"status":"pending","due_date":"2026-12-02","sap_entry_reference":null,"posted_at":null}},"meta":{"request_id":"req-repayment-001","timestamp":"<UTC>","api_version":"v1"}}
```

## Exact idempotency replay

```json
{"success":true,"data":{"idempotency_replayed":true,"original_response":"<retained receipt data>"},"meta":{"request_id":"req-repayment-001","timestamp":"<UTC>","api_version":"v1"}}
```

## Manual SAP posting recorded

```json
{"success":true,"data":{"repayment_id":"uuid","allocation_status":"pending","sap_posting":{"status":"posted","due_date":"2026-12-02","sap_entry_reference":"SAP-RCPT-123","posted_at":"2026-12-02T10:00:00Z"}},"meta":{"request_id":"req-repayment-posting-001","timestamp":"<UTC>","api_version":"v1"}}
```

These shapes are asserted through
`sfpcl_credit.tests.test_direct_repayment_posting_api.DirectRepaymentPostingApiTests`.
