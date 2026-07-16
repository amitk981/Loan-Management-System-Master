# Execution Plan

Selected slice: 009B3A-sap-model-owner-and-state-migration

## Scope and constraints

- Transfer only the Django model/state owner for the two existing SAP models from `finance` to
  `sap_workflow`; retain the exact physical table/column/index/constraint identities and every
  existing business row.
- Keep public HTTP routes and executable request/send/complete/read orchestration unchanged.
- Leave `finance.models` as a policy-free compatibility import whose names are the canonical
  `sap_workflow` classes.
- Use one reversible state-only migration, with no database operations, and preserve the
  `loans.LoanAccount.sap_customer_code` relation in both historical directions.

## TDD tracer bullets

1. RED: add an ownership/compatibility test asserting `sap_workflow` metadata ownership, unchanged
   Finance-era table/constraint identities, canonical legacy aliases, and the canonical loan FK.
   GREEN: move runtime model definitions to `sap_workflow`, replace Finance definitions with aliases,
   and repoint the runtime loan FK.
2. RED: add a migration-executor preservation test that creates pre-transfer request/code/loan rows,
   captures ids, foreign keys, ciphertext, checksums, digests, counts, and table names, migrates
   forward and backward, and compares the exact manifest with no duplicate facts.
   GREEN: add one reversible cross-app state operation that relocates both model states and rewrites
   only the historical relation targets; its database methods perform no SQL.
3. Add migration-graph/fresh-state and compatibility-policy probes, then run the focused SAP,
   loan-account, and readiness tests to ensure the public behavior is unchanged.
4. Run the declared PostgreSQL request/code race acceptance twice when the configured local service
   is available; retain honest logs if the coding sandbox cannot reach it.

## Verification and evidence

- Save failing and passing focused test output under `evidence/terminal-logs/`.
- Save a sanitized before/after identity manifest, migration graph, state-only operation proof, and
  compatibility proof under `evidence/`.
- Run Django check and migration sync plus impacted backend tests. No frontend files are in scope;
  frontend gates remain for the orchestrator's independent validation.
- Complete changed-files, risk, review, final summary, progress/state/handoff, and slice status only
  after focused verification is green.
