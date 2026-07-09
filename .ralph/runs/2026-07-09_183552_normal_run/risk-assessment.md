# Risk Assessment

Selected slice: `005C-reference-number-generation-and-loan-request-register`

Risk level: Medium.

## Why

- Adds one database migration with two new tables: `system_sequences` and
  `loan_request_register_entries`.
- Adds a new mutating API action that changes loan application lifecycle state and writes audit and
  workflow events.
- Touches business identifiers (`LO...`) and register records, which must remain unique and
  auditable.

## Controls

- Source trigger verified before implementation: official reference generation happens after
  completeness check passes, not at draft creation or submit.
- Endpoint is narrow and permission-gated by source-backed
  `applications.loan_application.complete_check`.
- No broad register-management UI or admin permission was invented.
- Sequence generation and application/register creation run in one transaction.
- Draft, duplicate, and already-reference-generated attempts return standard invalid-state errors
  before register/audit/workflow side effects.
- Register and audit metadata exclude PAN, Aadhaar, full bank account numbers, token values, and
  hashes.
- A-037 records the only source ambiguity: `screen-spec.md` S12 names `Reference Generated`, while
  the data-model enum list omits the stored value.

## Gates

All required gates passed:
- backend check
- backend tests
- backend migrations sync
- backend coverage 96% with floor 85%
- frontend typecheck
- frontend lint
- frontend tests
- frontend build
- `git diff --check`

## Residual Risk

The real completeness-workbench/checklist evaluation is not implemented in 005C. This endpoint
represents the successful completeness-pass transition and must be called only by the future 005E
completeness workflow after 005D checklist records exist.
