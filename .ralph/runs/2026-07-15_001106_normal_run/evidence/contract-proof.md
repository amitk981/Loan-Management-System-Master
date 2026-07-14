# 008I2 Contract Proof

## Public API examples

An assigned read-only approver with `security.package.read` receives the unchanged §6 envelope and
masked metadata from:

```http
GET /api/v1/loan-applications/{loan_application_id}/security-package/
Authorization: Bearer <assigned-approver-token>

200
{
  "success": true,
  "data": {
    "security_package_id": "uuid",
    "loan_application_id": "uuid",
    "security_status": "pending",
    "security_ready_flag": false,
    "power_of_attorney": null
  },
  "meta": {"request_id": null, "timestamp": "...", "api_version": "v1"}
}
```

The same read-only actor cannot refresh or mutate; authority is checked before the malformed body:

```http
POST /api/v1/loan-applications/{loan_application_id}/security-package/refresh/
{"unexpected":"must not parse"}

403
{"success":false,"error":{"code":"FORBIDDEN",...},"meta":{...}}
```

An otherwise valid Company Secretary activation using an adequate ₹499.99 stamp returns
`400 VALIDATION_ERROR` on `stamp_duty_record_id`; the PoA remains draft and audit, version, and
workflow success counts remain unchanged. ₹1.00 and ₹500.01 have the same result. Exactly ₹500.00
then activates through the retained §6.3 action response.

## Owner and dependency proof

- `create_poa.__module__` is
  `sfpcl_credit.security_instruments.modules.power_of_attorney`.
- The security owner AST contains neither a
  `legal_documents.modules.power_of_attorney` import nor `bind_security_owner`/`__getattr__`.
- `legal_documents.modules.power_of_attorney` contains only a documented policy-free compatibility
  import; sharpened 008I3 owns its removal with the remaining source dependency correction.
- Evidence: `terminal-logs/red-module-owner.log` and `terminal-logs/green-module-owner.log`.

## Retained persistence proof

`SecurityInstrumentOwnershipMigrationTests` migrates from the legal state into
`security_instruments.0001`, asserts the table set is identical, and confirms the retained
`security_packages`/`power_of_attorneys` names and activation evidence field. The final focused run
passed this regression without a new migration; `makemigrations --check --dry-run` returned
`No changes detected`.

## PostgreSQL proof

`postgres-poa-races-ledgers-run-1.log` and `run-2.log` each pass the five-worker changed-activation
and terminal-downgrade cases. The tests assert exactly one changed activation winner, the same
winner request across retained PoA, audit, version, consumed-document, and workflow identities,
and absence of every loser request from success evidence. All five downgrade attempts conflict and
leave audit/version/workflow counts unchanged.
