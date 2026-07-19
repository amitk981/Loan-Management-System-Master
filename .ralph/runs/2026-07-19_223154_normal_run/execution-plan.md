# Execution Plan

Selected slice: `010B-direct-repayment-posting`

## Delivery Boundary

Implement a backend-only repayment-capture module with two public mutation interfaces: capture a
confirmed direct RTGS/NEFT receipt for a serviceable loan, and mark its durable SAP-posting
obligation posted. Capture retains pending allocation and does not alter loan balances, schedules,
or ledger entries. Allocation, matching, subsidiary receipts, external SAP integration, reversal,
acknowledgement, and frontend work remain out of scope.

## Repository and Permission Checks

- Work only in the active Ralph worktree and current run folder.
- Product edits are limited to allowed `sfpcl_credit/**` paths plus the working API contract and
  current run evidence/artifacts.
- Do not edit orchestrator-owned state, progress, selected-slice status, protected paths, or
  `docs/source/**`.
- One migration maximum; no dependency changes.

## TDD Tracer Bullets

1. Add one public API test for a valid direct receipt and exact idempotency replay. Save the failing
   result, implement the minimum repayment model/module/view/route and SAP obligation, then save the
   passing result.
2. Add public behavior tests one cycle at a time for validation, unsupported methods, serviceable
   loan states, duplicate bank references, changed/cross-loan replays, permissions, and loan-object
   scope. Each rejection must prove no receipt, obligation, audit, schedule, ledger, or balance write.
3. Add the SAP-posted transition test: permission and nonblank SAP reference are required, the actor
   and timestamp are retained, repeat/invalid transitions conflict, and audit text excludes evidence
   content.
4. Add the declared PostgreSQL acceptance class with exactly two race tests: same idempotency key and
   same canonical bank reference. Each proves one receipt and one obligation under concurrent calls.

## Implementation Shape

- Keep policy, transaction boundaries, canonical reference/idempotency checks, object scope, audit,
  and obligation creation in one deep repayment-capture module interface.
- Keep HTTP parsing and domain-error mapping in thin views following existing response envelopes.
- Put receipt and obligation truth in the loans owner (the established servicing aggregate), with
  database uniqueness/check constraints and a single migration.
- Reuse existing permission/object-scope and audit modules; never log evidence contents.

## Verification and Evidence

- Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every backend command.
- Retain focused RED/GREEN logs under `evidence/terminal-logs/`, including exact selectors and exit
  codes.
- Run focused repayment tests, the declared PostgreSQL class where locally available, focused Epic
  009/010A regressions, `manage.py check`, and `makemigrations --check`. Do not run the complete
  backend suite or full coverage.
- Record API examples, migration/constraint proof, risk assessment, final summary, and a review
  packet whose Result is exactly `Ready for independent validation`.
