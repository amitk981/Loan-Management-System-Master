# Execution Plan

Selected slice: `009C-loan-account-creation-from-sanctioned-application`

## Scope and interface

- Add the source-owned `loans` Django module with a small public
  `loans.modules.loan_account_lifecycle.create_loan_account(...)` interface and the exact
  `POST /api/v1/loan-applications/{loan_application_id}/create-loan-account/` HTTP interface.
- Persist one protected loan account, one immutable one-to-one terms package, and one append-only
  initial status history in one transaction. Initial status is `sanctioned`; every balance remains
  zero and this slice creates no readiness, schedule, disbursement, activation, or communication.
- Consume the active SAP linkage only through
  `SapCustomerProfileModule.get_customer_code_for_member(member_id)` and retain only its canonical
  identifiers after exact member/application coherence checks.
- Freeze terms only from the exact current terminal sanction, current application/member/nominee/
  shareholding facts, and current valid Term Sheet and Loan Agreement owner evidence. Missing
  governed source facts fail closed without guessed defaults.

## TDD tracer bullets

1. RED -> GREEN: public HTTP success with an explicitly persisted Critical permission creates the
   canonical account/terms/history/audit/workflow tuple and returns the safe standard envelope.
2. RED -> GREEN: exact replay returns retained identifiers with no new ledger rows; changed account
   number or sanction conflicts, and canonicalized duplicate numbers are database-blocked.
3. RED -> GREEN: permission, inactive actor, object scope, unknown payload, malformed values,
   inaccessible parent, stale/non-terminal sanction, missing term evidence, and incoherent SAP
   decisions are zero-write failures with stable envelopes.
4. RED -> GREEN: source-boundary and secret-scan tests prevent Finance/SAP internals or sensitive
   member/legal/security payloads from entering the loan module, responses, errors, and ledgers.
5. RED -> GREEN: a five-caller PostgreSQL race retains exactly one complete winner tuple and no
   loser audit/workflow/status evidence; run the declared race twice.

Each focused red and green command uses
`/Users/amitkallapa/LMS/.ralph/venv/bin/python` and is saved under
`evidence/terminal-logs/` before moving to the next behavior.

## Implementation and documentation

- Add one migration containing source §18.1, §18.2, and §18.4 constraints/indexes.
- Wire the new app and route without changing the role catalogue grant matrix.
- Update `docs/working/API_CONTRACTS.md`, the Epic 009 digest if newly extracted source facts are
  needed, and record only genuinely unstated decisions in `docs/working/ASSUMPTIONS.md`.
- Sharpen the next one or two Not Started slices using only the already-open Epic 009 sources.

## Verification and handoff

- Run focused tests throughout, Django check, migration drift, the full backend coverage gate,
  PostgreSQL acceptance twice, and all frontend build/typecheck/lint/test gates.
- Save sanitized API/evidence examples plus terminal logs, then complete `changed-files.txt`,
  `risk-assessment.md`, `review-packet.md`, and `final-summary.md`.
- Update the selected slice status/checklist, `.ralph/state.json`, `.ralph/progress.md`, and
  `docs/working/HANDOFF.md`. Do not run Git add, commit, or push.
