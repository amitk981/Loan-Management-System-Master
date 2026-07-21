# Impact Analysis

Selected slice: `CR-015-epic-010-terminal-servicing-owner-finalizer`

## Demonstrated validation domain

Independent complete-suite validation found that a repeated direct SAP-posting request with the
same idempotency key now returns the retained successful outcome (`200`) instead of the established
endpoint-level duplicate conflict (`409`). The same validation run also lacked the two declared
five-test PostgreSQL acceptance executions and non-secret PostgreSQL environment evidence.

## Affected backend pieces

- `sfpcl_credit/loans/modules/direct_repayment_posting.py`: existing public SAP-posting behavior and
  its interaction with newly retained composite-command state.
- `sfpcl_credit/processes/direct_repayment_command.py`: composite direct-repayment replay owner; in
  blast radius only if it currently changes the legacy posting seam's idempotency interpretation.
- `sfpcl_credit/tests/test_direct_repayment_posting_api.py`: existing permanent regression for the
  exact failed endpoint response, permission, reference, and safe-audit contract.
- `sfpcl_credit/tests/test_epic010_terminal_owner_finalizer.py`: declared five-case PostgreSQL
  acceptance contract and composite command regression coverage.

No schema change is expected. If a model/migration change becomes necessary, stop and reassess the
bounded repair because that would exceed the demonstrated validation domain.

## Frontend impact

None. The failing behavior is a backend endpoint compatibility regression and missing acceptance
evidence. Existing frontend changes are preserved but not broadened in this repair.

## Blast radius and regression tests

- Legacy callers of the SAP-posting endpoint must continue receiving `409` on a duplicate posting.
- The composite direct-repayment command must still resume exact-key retries and return one complete
  retained financial outcome without a second capture, SAP decision, or allocation.
- Changed-key and cross-account payloads must still conflict without extra effects.
- Regression coverage: the exact failed API test, the direct-repayment API module, the terminal
  finalizer direct-repayment tests, and the declared PostgreSQL acceptance class twice.

## Scope controls

- Fix only the direct-repayment idempotency compatibility boundary and required PostgreSQL evidence.
- Do not change repayment allocation rules, permissions, UI behavior, reminder/MIS/statement logic,
  or the frozen slice contract.
- Do not edit protected files, orchestrator-owned state/progress/status facts, or historical evidence.
