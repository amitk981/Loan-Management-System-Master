# Execution Plan

Selected slice: `009J-loan-account-360-initial-view`

## Boundary

Implement only the authenticated Loan Account 360 account list and initial detail composition
(header, KPI row, and Summary tab). Preserve later prototype tabs and their 010M-owned fixtures,
but do not render or infer their repayment, schedule, interest, DPD, default, closure, or NOC facts
in the initial view. Add no model or migration.

## Implementation sequence

1. Add one public API behavior test for a genuinely lifecycle-created sanctioned account. Prove
   strict paginated list and nondisclosing detail return the exact zero-funded projection, stable
   decimals/nulls/timestamps, and no writes. Run it red and retain the output.
2. Implement a loans-owned read scope/creation projection and a process-level Loan Account 360
   coordinator. The coordinator may consume the disbursement owner's existing current post-transfer
   facade, keeping cross-module composition out of either model owner. Add strict list/detail views,
   routing, pagination/query validation, standard envelopes, and contract documentation. Run the
   tracer test green and retain the output.
3. Add one API behavior at a time for exact active/funded projection, evidence drift and duplicate/
   cross-object failure, and list/detail permission parity across source roles and scopes. Keep reads
   transactionally zero-write and run focused red/green cycles.
4. Add a typed frontend API boundary using the shared authenticated transport. Add Loan Account 360
   interaction/container tests for loading, empty, error/unauthorised, list navigation, sanctioned
   detail, active detail, server-exact money/status, and the mock/fixture ratchet. Run impacted tests
   red before wiring, then green.
5. Wire only the list/header/KPI/Summary paths in `LoanAccount360.tsx`, retaining the approved table,
   header, cards, badges, tabs, spacing, colours, typography, and responsive composition. Do not add
   client-owned money or status calculations. Update the prototype inventory/gap ledger if required.
6. Run focused backend tests with the mandated Ralph interpreter, backend check and migration sync;
   run impacted frontend tests plus full frontend typecheck, lint, test, and build. Do not run the
   complete backend suite or coverage locally.
7. Save sanitized API envelopes and terminal evidence, attempt the declared real-backend visual
   scenarios only within the sandbox's available browser capability, and never fabricate screenshots.
   Finish the run risk assessment, review packet with source-to-test traceability, and final summary.

## Expected files

- `sfpcl_credit/loans/modules/` read scope/creation projection
- `sfpcl_credit/processes/` cross-owner Loan Account 360 projection
- `sfpcl_credit/loans/views.py`, `sfpcl_credit/config/urls.py`
- `sfpcl_credit/tests/test_loan_account_reads_api.py`
- `sfpcl-lms/src/services/loanAccountsApi.ts`
- `sfpcl-lms/src/pages/loan-accounts/LoanAccount360.tsx` and focused tests
- `docs/working/API_CONTRACTS.md` and, only if the screen ledger requires it, prototype inventory/gap docs
- `.ralph/runs/2026-07-19_024941_normal_run/` evidence and review artifacts

## Primary risks and controls

- Financial/status drift: expose active/funded values only when the existing creation and exact
  009G3 post-transfer facades reconcile all owner ids and amounts; otherwise exclude the row/detail.
- Scope leakage: require an active persisted effective role plus `finance.loan_account.read`, apply
  the same canonical object predicate before list pagination and detail lookup, and make inaccessible
  ids indistinguishable from missing ids.
- Sensitive evidence leakage: whitelist display fields and test that UTR, bank, evidence, checksum,
  internal request/idempotency, contact, and provider identities never serialize.
- Prototype/mock expansion: reuse existing UI classes/components and leave 010M-owned later tabs
  untouched; add a source regression proving no new production fixture or initial-view calculation.
