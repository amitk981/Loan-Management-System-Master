# Execution Plan

Selected slice: 010J2-reminder-eligibility-and-delivery-integrity-closure

## Public interface and module seam

Keep the existing monitoring reminder HTTP/module interface and make its implementation own the
complete retained decision and delivery lifecycle. Consume DPD and communications through their
public owners; do not expose new helper-level interfaces or move business rules into views.

## TDD tracer bullets

1. Add one public reminder API test proving calendar-anniversary eligibility (including a leap-year
   span) and retained decision evidence; run it RED, implement minimally, then run it GREEN.
2. Add one public send test proving a retained eligible reminder survives a newer still-overdue DPD
   pointer while current repayment/resolution cancels before provider execution; run RED/GREEN.
3. Add one public send test proving exact replay is stable and a changed/cross-reminder key maps to
   a zero-write 409 instead of escaping the communications owner; run RED/GREEN.
4. Add one public quarter-run test proving mixed loans return explicit created/skipped/failed rows
   without concealing earlier retained effects; run RED/GREEN.
5. Add the exact five-test PostgreSQL acceptance class covering AC-REM2-1 through AC-REM2-5 and run
   it twice against PostgreSQL when the configured local database permits it.

## Implementation and persistence

- Extend the retained reminder decision only with source-owned eligibility evidence required by the
  slice: first-unpaid date, cutoff, DPD policy/version, and calendar boundary evidence.
- Add at most one monitoring migration and preserve append-only DPD and communication evidence.
- Translate communications conflicts at the reminder seam and preserve one message/job effect.
- Return a bounded per-loan batch result with explicit outcome and reason for every candidate.

## Verification and evidence

- Save exact RED/GREEN commands and exit signals under `evidence/terminal-logs/`.
- Run focused monitoring reminder, DPD reverse-consumer, communications reverse-consumer,
  `manage.py check`, and `makemigrations --check`; do not run the complete backend suite.
- Run the exact review-closure validator until PASS.
- Complete `review-closure-evidence.md`, `risk-assessment.md`, `review-packet.md`, and
  `final-summary.md`, leaving the orchestrator-owned state/status/changed-files bookkeeping alone.
