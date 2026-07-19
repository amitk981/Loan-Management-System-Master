# API Response Examples

## Repayment schedule

`GET /api/v1/loan-accounts/{loan_account_id}/repayment-schedule/?page=1&page_size=20`

```json
{
  "success": true,
  "data": [
    {
      "repayment_schedule_id": "uuid",
      "installment_number": 1,
      "due_date": "2027-06-22",
      "principal_due": "200000.00",
      "interest_due": "10000.00",
      "charges_due": "0.00",
      "total_due": "210000.00",
      "paid_principal": "0.00",
      "paid_interest": "0.00",
      "paid_charges": "0.00",
      "amount_received": "0.00",
      "schedule_status": "pending",
      "extended_due_date": null,
      "created_at": "2026-07-19T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_count": 1,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  },
  "meta": {"request_id": null, "timestamp": "2026-07-19T10:00:01Z", "api_version": "v1"}
}
```

## Loan ledger

`GET /api/v1/loan-accounts/{loan_account_id}/ledger/?page=1&page_size=20`

```json
{
  "success": true,
  "data": [
    {
      "transaction_date": "2026-07-19",
      "transaction_type": "disbursement",
      "owner_reference": {"entity_type": "disbursement", "entity_id": "uuid"},
      "reference": "RBL-READ-UTR-001",
      "debit": "400000.00",
      "credit": "0.00",
      "principal_balance": "400000.00",
      "interest_balance": "0.00",
      "total_outstanding": "400000.00",
      "actor": {"user_id": "uuid", "display_name": "Transfer Authoriser"},
      "sap_status": "pending",
      "remarks": "Initial loan disbursement."
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_count": 1,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  },
  "meta": {"request_id": null, "timestamp": "2026-07-19T10:00:01Z", "api_version": "v1"}
}
```

The permanent executable examples are asserted by
`sfpcl_credit.tests.test_loan_schedule_ledger_api` and use generated UUIDs and synthetic financial
values only.
