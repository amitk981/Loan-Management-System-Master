# API Contract Examples

Identifiers below are illustrative UUIDs; executable assertions are in
`sfpcl_credit/tests/test_power_of_attorney_api.py`.

## Refresh package

`POST /api/v1/loan-applications/11111111-1111-4111-8111-111111111111/security-package/refresh/`

```json
{}
```

Successful `data` contains the stable package/application ids, `security_status: "pending"`,
`poa_required_flag: true`, `security_ready_flag: false`, and `power_of_attorney: null`. Exact replay
returns the same data without new audit/version/workflow rows. Status-only or stale-cycle scope
returns a nondisclosing authorization error and creates nothing.

## Prepare PoA draft

`POST /api/v1/security-packages/22222222-2222-4222-8222-222222222222/power-of-attorney/`

```json
{
  "borrower_member_id": "33333333-3333-4333-8333-333333333333",
  "nominee_id": "44444444-4444-4444-8444-444444444444",
  "attorney_user_id": "55555555-5555-4555-8555-555555555555",
  "purpose_summary": "Authorise the Company Secretary to initiate sale of shares on default.",
  "loan_document_id": "66666666-6666-4666-8666-666666666666",
  "stamp_duty_record_id": "77777777-7777-4777-8777-777777777777",
  "notarisation_record_id": "88888888-8888-4888-8888-888888888888",
  "execution_status": "pending",
  "effective_from": null,
  "status": "draft"
}
```

Only Compliance can create/change the draft. The response retains the Compliance
`prepared_by_user_id`, null verifier, and no activation evidence.

## Activate exact retained draft

PATCH sends the same retained facts with `execution_status: "executed"`, an ISO effective date,
and `status: "active"`. Success and exact replay return this §6.3 `data` shape:

```json
{
  "entity_type": "power_of_attorney",
  "entity_id": "99999999-9999-4999-8999-999999999999",
  "previous_status": "draft",
  "new_status": "active",
  "workflow_event_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
  "available_actions": []
}
```

Changed activation or downgrade returns `409 CONFLICT` with zero success writes. A retained legacy
active PoA is readable with `legacy_activation_evidence: true`, but PATCH conflicts under A-112
because it has no truthful durable activation action identity.
