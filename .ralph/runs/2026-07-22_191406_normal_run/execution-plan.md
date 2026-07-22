# Execution Plan

Selected slice: `011G-closure-readiness`

## Permission and scope check

- Product edits are limited to `sfpcl_credit/**`; run evidence is limited to
  `.ralph/runs/2026-07-22_191406_normal_run/**`.
- Do not edit protected Ralph configuration, scripts, source documents, state/progress, slice status,
  or mechanical handoff files.
- This is a backend/model/API slice with one migration and no frontend work.

## Implementation sequence

1. Inspect the canonical loan, repayment/ledger, interest, recovery, security, permission, audit,
   workflow-event, idempotency, and routing seams used by adjacent completed slices.
2. Add one public-behaviour test for server-derived readiness, run it RED, and save the terminal log.
   Add the minimum closure owner/model/module implementation to make it GREEN.
3. Add closure blocker behaviours one at a time (principal, interest/approved adjustment, charges,
   unresolved ledger/reconciliation, pending recovery, and applicable security tasks), keeping each
   cycle focused and saving representative RED/GREEN evidence.
4. Add the close API behaviour: full-repayment only, fresh locked re-evaluation, immutable balance/check
   snapshot, actor/time/type/notes, financial `closed` status, explicit NOC/security/archive requirements,
   status history, and safe audit/workflow evidence. Require critical permission and idempotency.
5. Add negative behaviours incrementally for unsupported type, scope/role denial, forged/stale client
   values, blockers, duplicate/change replay, and post-close mutation.
6. Add exactly three PostgreSQL acceptance tests for close-vs-repayment, close-vs-recovery, and duplicate
   close races, using the declared acceptance class and canonical public services.
7. Generate the migration; run focused closure/API/permission tests, the three-test PostgreSQL label when
   locally available, reverse-consumer tests, Django check, and migration consistency with the mandated
   Ralph Python interpreter. Do not run the complete backend suite.
8. Inspect targeted diffs and diff stats, update the working API contract if needed, and complete evidence,
   risk assessment, review packet, and final summary. Set the review result exactly to
   `Ready for independent validation` only after all focused checks are green.

## TDD evidence

Red and green command output will be retained under `evidence/terminal-logs/`; tests will exercise public
module/API interfaces rather than private implementation details.
