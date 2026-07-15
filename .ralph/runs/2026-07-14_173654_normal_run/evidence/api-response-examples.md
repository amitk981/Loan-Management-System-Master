# 008F API Response Examples

These metadata-only examples are the response shapes asserted by
`sfpcl_credit.tests.test_power_of_attorney_api`.

## Package refresh / read

```json
{
  "success": true,
  "data": {
    "security_package_id": "uuid",
    "loan_application_id": "uuid",
    "loan_account_id": null,
    "security_status": "pending",
    "physical_share_security_required_flag": false,
    "demat_pledge_required_flag": false,
    "poa_required_flag": true,
    "blank_cheque_required_flag": false,
    "cancelled_cheque_required_flag": false,
    "security_ready_flag": false,
    "power_of_attorney": null
  },
  "meta": {"request_id": "req-package-create", "api_version": "v1"}
}
```

## Active Power of Attorney

```json
{
  "success": true,
  "data": {
    "power_of_attorney_id": "uuid",
    "security_package_id": "uuid",
    "borrower_member_id": "uuid",
    "nominee_id": "uuid",
    "attorney_user_id": "uuid",
    "purpose_summary": "Authorise Company Secretary to initiate sale of shares on default.",
    "loan_document_id": "uuid",
    "stamp_duty_record_id": "uuid",
    "notarisation_record_id": "uuid",
    "execution_status": "executed",
    "effective_from": "2026-07-14",
    "status": "active",
    "prepared_by_user_id": "uuid",
    "verified_by_user_id": "uuid"
  },
  "meta": {"request_id": "req-poa-active", "api_version": "v1"}
}
```

Neither response includes storage keys, download URLs, invocation/release actions, checklist
completion, package completion, or disbursement readiness.
