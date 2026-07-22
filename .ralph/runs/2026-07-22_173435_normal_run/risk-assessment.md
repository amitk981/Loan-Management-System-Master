# Risk Assessment

Risk level: High

- Selected slice: `011F-recovery-action-execution-shell`
- Mode: `normal_run`
- Manual review required: yes; independent Ralph validation owns the authoritative High-risk lane.

## High-risk surfaces and controls

- Financial integrity: completion locks the recovery action and delegates one verified amount to the
  canonical loan-balance owner in the same transaction. Exact replay returns retained evidence;
  changed/stale replay conflicts before a second balance mutation or success audit.
- Recovery authority: initiation/completion require Critical catalogue permissions, active Company
  Secretary role authority, canonical default-case scope, an exact terminal approval, and a matching
  usable security instrument. A-159 records the fail-closed authorised-user interpretation.
- Custody boundary: SH-4, CDSL, and blank-cheque state is validated through a security-owner façade;
  011F does not mutate custody, pledge, presentation, DP, bank, or share-sale state.
- Evidence/privacy: evidence must be a governed same-loan recovery document; retained interaction
  records include borrower-contact and grievance routing without sensitive payloads in audit logs.
- External integration: SAP stays explicitly `pending`; no external acceptance is fabricated.
- Frontend authority: S57 renders an executable row only when backend `available_actions` permits
  initiation/completion (completed history remains displayable); static role heuristics do not grant
  an action.
- Concurrency: PostgreSQL-only five-client initiation/completion and owner-rollback cases are declared
  under the exact trusted label. SQLite collected and skipped those three cases as designed.

## Residual risk

- Local Chrome launched and immediately closed before page creation. The exact trusted-browser spec
  exists, but the two requested screenshots were not fabricated and must be produced by trusted
  validation.
- Governance has not named a second “authorised recovery user” role. Execution remains CS-only plus
  Critical permission until an explicit governed configuration is delivered.
- External DP/bank/share-sale and SAP posting are intentionally outside this slice.

## Diff limits

- Product changed-line accounting: 1,997 lines, within the configured 2,000-line limit.
- One migration added, within the configured migration limit.
- Protected files and `docs/source/` were not modified.
