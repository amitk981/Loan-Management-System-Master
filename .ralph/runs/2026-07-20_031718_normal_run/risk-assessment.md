# Risk Assessment

Risk level: Medium

- Selected slice: 010E-subsidiary-deduction-reconciliation
- Mode: normal_run
- Manual review required: independent Ralph validation required before integration.

## Financial and data-integrity controls

- Capture does not change balances, schedule paid amounts, allocation rows, or ledger rows. Only the
  existing 010C allocator may make the financial movement, after posted-SAP admission and the new
  subsidiary reconciliation/Treasury gates.
- Normalized transfer references are globally unique; normalized produce-payment references are
  unique per subsidiary UUID; receipt and subsidiary evidence are one-to-one. Capture, statement
  match, Treasury verification/exception, SAP posting, allocation, and ledger evidence remain
  distinct persisted facts.
- Capture and Treasury verification lock their authoritative rows. The declared two-test PostgreSQL
  acceptance class exercises same-request capture and concurrent verify/allocation replay; local
  SQLite collected exactly two tests and skipped their PostgreSQL-only bodies as designed.
- Exact idempotent capture, Treasury, SAP, and allocation replay retains one result/effect. Changed
  terminal requests conflict. Missing agreement, unclear narration, excess, wrong role/permission,
  and inaccessible identities do not move money.

## Security and privacy

- Mutation authority requires the existing finance permission, an active Credit Manager or Accounts
  Head role, and existing loan-object scope. Missing/inaccessible objects use nondisclosing `404`.
- Statement bytes, narration, raw transfer/produce references, and free-text remarks are not copied
  into subsidiary audit JSON. Audit evidence retains reference/remarks digests and governed object,
  actor, role, request, and timestamp identities.
- The API returns source-required reference values to the authorised mutation caller; no new list or
  broad read surface was added.

## Residual risks and assumptions

- A-144 records that the source calls `subsidiary_company_id` a foreign key but defines no canonical
  subsidiary-company registry. This slice therefore retains a required opaque UUID and does not
  claim company-master validation. Governance must provide a registry before an enforced FK can be
  introduced.
- SAP posting remains a retained manual system decision through the existing adapter boundary; this
  work does not claim an external SAP provider call.
- The orchestrator must run the declared PostgreSQL contention label and authoritative full backend
  coverage suite. No full suite or full coverage was run locally, per Ralph instructions.
- No frontend wiring was in scope, so there is no visual/browser risk or evidence requirement.
