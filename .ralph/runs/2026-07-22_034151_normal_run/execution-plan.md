# Execution Plan

Selected slice: 010N5-terminal-servicing-recurrence-owner-closure

## Boundary

- Preserve the grouped CR-015 recurrence contract for MIS, reminder delivery, and the servicing
  owner seam.
- Change only the staff direct-repayment transport boundary and substantive permanent tests needed
  by AC-E10-RR1 through AC-E10-RR4. Do not change business policy, styling, schemas, or protected
  Ralph files.
- Use the orchestrator-managed backend interpreter for every Django command and retain the exact
  five-test PostgreSQL acceptance class unchanged in count.

## TDD sequence

1. Add one frontend service regression proving a capture-only composite response is rejected after
   exactly one request, with no SAP/allocation request and no client-supplied allocation policy.
   Save the focused failing run as RED evidence.
2. Remove the capture-only compatibility coordinator and validate the exact composite response
   shape (`replayed`, `capture`, and non-null `allocation`) before returning it. Save the focused
   passing run as GREEN evidence.
3. Extend the same public-service matrix to malformed and failed responses, while retaining complete
   and replay success through one request.
4. Add backend public-command regressions for changed-payload conflict, transaction rollback at a
   forced allocation failure, and equal-key convergence. Keep the trusted reminder PostgreSQL class
   at exactly five tests. Run focused backend tests and retain logs.
5. Replay every exact review-probe command named by the terminal recurrence history, plus the current
   MIS/reminder focused commands and the trusted PostgreSQL class twice. Each retained current-run
   log must include the exact command, a positive pass signal, and `Exit code: 0`.
6. Run impacted frontend tests, typecheck, lint, and build; run Django check and migration-sync only
   (the orchestrator owns the complete backend suite/coverage). Run the exact review-closure
   validator until it prints PASS.

## Evidence and handoff

- Create `review-closure-evidence.md` with one finding row per inherited Finding ID/Root ID and one
  acceptance row per AC-E10-RR1 through AC-E10-RR4, using exact permanent selectors and distinct
  RED/GREEN evidence.
- Complete `risk-assessment.md`, `review-packet.md`, and `final-summary.md`; set the review result
  exactly to `Ready for independent validation` only after all focused gates and closure validation
  pass.
