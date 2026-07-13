# Execution Plan

Selected slice: 007D2-approval-action-boundary-and-postgresql-race-closure

1. Preserve the public approval interfaces while deepening their implementation: make collection,
   detail, and action responses use one history-aware projection; keep action validation and denial
   reasons aligned with the detail `available_actions` projection.
2. Work in TDD tracer-bullet cycles through public HTTP/module seams. First capture RED evidence for
   collection/detail/action history parity, then implement the minimum shared projection change.
3. Add independently named public POST denial and validation rows (stale, acted, excluded, closed,
   contradictory/unroutable, unassigned/read-only, per-action permission, and blank reject/return),
   asserting matching detail reasons and exact zero-write ledgers; fix only mismatches exposed.
4. Add invalid application/appraisal-state RED tests, then route owner-state mutations through the
   shared transition guard while retaining the application -> appraisal -> case lock order.
5. Add a communication-owned internal adapter contract and RED success/failure tests. Replace the
   direct approval-owned notification insert with one atomic pending Communication + linked team
   Notification + metadata-only communication audit; prove adapter failure rolls back all outcome
   writes.
6. Add authoritative PostgreSQL TransactionTestCase acceptance for (a) different remaining actors
   posting one version and (b) a final actor posting twice. Run both races twice and retain exact
   before/after ledgers proving one serial winner, stable loser, no deadlock, one actor action, one
   sanction, and one completion communication/notification.
7. Update the working API contract and Epic 007 digest, then run focused green tests, PostgreSQL
   race acceptance twice, backend checks/migration sync/full coverage, and all frontend quality
   gates. Save complete logs and API/ledger evidence in this run folder.
8. Review the diff against the selected slice and source references; stay below Ralph diff limits.
   Sharpen the next one or two Not Started slices using only source material already opened, then
   write changed-files, risk, review, summary, progress, state, handoff, and mark only 007D2 Complete.

No frontend production change or database migration is planned. If a failing behavioral test proves
either is necessary, reassess scope and record the source-backed reason before editing it.
