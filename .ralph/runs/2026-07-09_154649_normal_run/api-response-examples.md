# API Response Examples — 004J Bank Account and Cancelled Cheque Profile Foundation

Focused test evidence:
- RED: `evidence/terminal-logs/tdd-red-member-bank-accounts.log`
- GREEN: `evidence/terminal-logs/tdd-green-member-bank-accounts-final.log`

## Create Bank Account

`POST /api/v1/members/{member_id}/bank-accounts/`

Request:

```json
{
  "account_holder_name": "Ramesh Patil",
  "account_number": "123456789012",
  "ifsc": "HDFC0001234",
  "bank_name": "HDFC Bank",
  "branch_name": "Nashik Road",
  "verification_status": "pending",
  "signature_verified_flag": null,
  "status": "active"
}
```

Success data shape:

```json
{
  "bank_account_id": "uuid",
  "owner_party_type": "member",
  "owner_party_id": "member-uuid",
  "account_holder_name": "Ramesh Patil",
  "account_number": {
    "masked": "********9012",
    "last4": "9012",
    "can_view_full": false
  },
  "ifsc": "HDFC0001234",
  "bank_name": "HDFC Bank",
  "branch_name": "Nashik Road",
  "verification_status": "pending",
  "cancelled_cheque_id": null,
  "signature_verified_flag": null,
  "status": "active",
  "created_at": "2026-07-09T00:00:00Z"
}
```

## Create Cancelled Cheque

`POST /api/v1/members/{member_id}/cancelled-cheques/`

Request:

```json
{
  "loan_application_id": null,
  "document_id": "uuid",
  "account_number": "987654324321",
  "ifsc": "SBIN0000456",
  "branch_name": "Lasalgaon",
  "verification_status": "pending",
  "signature_mismatch_flag": false
}
```

Success data shape:

```json
{
  "cancelled_cheque_id": "uuid",
  "loan_application_id": null,
  "member_id": "member-uuid",
  "document_id": "uuid",
  "account_number": {
    "masked": "********4321",
    "last4": "4321",
    "can_view_full": false
  },
  "ifsc": "SBIN0000456",
  "branch_name": "Lasalgaon",
  "verification_status": "pending",
  "signature_mismatch_flag": false,
  "created_at": "2026-07-09T00:00:00Z"
}
```

## Contract Notes

- Full account numbers are accepted only in create requests and are stored as protected token plus keyed hash and last four.
- Responses and audit metadata expose masked/last-four values only.
- `GET` endpoints require `members.member.read`; `POST` endpoints require `members.member.update` under A-034.
- No workflow events are written for list/create bank metadata actions.
