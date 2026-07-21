# Execution Plan

Selected slice: `CR-015-epic-010-terminal-servicing-owner-finalizer`

1. Establish the current public seams, data constraints, and exact regression selectors for
   reminders, MIS generation, direct repayment, statement artifacts, and portal collections.
2. Add one permanent reminder owner regression and run it RED; implement the smallest retained
   delivery-claim/final-serviceability change and run it GREEN. Extend vertically through the five
   declared reminder race cases and 1/100/101 behavior.
3. Add one historical MIS cutoff regression and run it RED; retain cutoff-valid owner decisions and
   run it GREEN. Extend through the required before/cutoff/after mutable-source matrix and replay.
4. Add a backend composite direct-repayment command regression and run it RED; implement durable
   capture/SAP/allocation/response step ownership and run it GREEN. Add crash, conflict, and
   PostgreSQL concurrency cases, then replace the frontend three-call coordinator and verify its UI.
5. Add statement concurrency/privacy and portal pagination/projection regressions one at a time,
   completing each RED/GREEN cycle behind the existing process interfaces.
6. Create the exact five-test PostgreSQL acceptance class and replace touched cross-class setup
   borrowing with public builders. Run the declared class twice and retain both logs.
7. Run focused backend modules, Django check and migration sync; run impacted frontend tests,
   typecheck, lint, and build. Do not run the complete backend suite or coverage locally.
8. Produce closure evidence mapping every finding and acceptance ID to exact permanent tests and
   distinct RED/GREEN logs. Complete risk assessment, two-axis review, review packet, and final
   summary; run the mandatory closure validator until it prints `PASS`.

## Interface and testability notes

- Keep each owner as a deep module with a small public command/read interface; locking, retained
  decisions, step recovery, and provider coordination remain implementation details.
- Tests cross the same public service/API seams as production callers and assert observable retained
  effects rather than private helper calls.
- Reuse existing adapters and projections; introduce no hypothetical seam without a second adapter.
