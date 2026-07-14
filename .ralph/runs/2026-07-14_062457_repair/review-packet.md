# Review Packet: 2026-07-14_062457_repair

## Result

Repair complete and locally green; independent Ralph validation remains the commit gate.

## Slice

008A-document-template-model-and-versioning

## Demonstrated failure and fix

Both independent PostgreSQL runs failed before reaching a green acceptance verdict because the
returned-cycle approval path combined bare `select_for_update()` with nullable outer joins.
The tight single-test loop reproduced the exact `FOR UPDATE cannot be applied to the nullable side
of an outer join` error. Restricting the lock target to the `ApprovalCase` row made that exact test
green without changing the eager-loaded evidence.

Direct execution of 008A's declared PostgreSQL race then exposed the identical invalid lock shape on
the nullable template-file join. The same narrow correction locks only the predecessor
`DocumentTemplate`; the existing five-thread public API test proves one linked successor and one
audit/version-history evidence set. No new test was needed because both existing PostgreSQL tests
exercise the real public/business seams and failed before the fixes.

## Standards review

- The fixes follow the repository's existing PostgreSQL `select_for_update(of=("self",))` pattern.
- Transaction boundaries and lock order are unchanged; no broad exception handling, retry, fixture
  change, quality-gate weakening, schema change, dependency, or dead code was introduced.
- `git diff --check`, Django check, migration sync, full backend coverage, and every frontend gate
  pass. No `[DEBUG-...]` instrumentation exists in production code.
- The diagnosing-bugs workflow drove a fast deterministic red loop, ranked falsifiable hypotheses,
  minimal one-variable fixes, two PostgreSQL reruns per contract, and cleanup verification.

## Spec review and traceability

- Slice 008A requires one-winner concurrent successor creation and immutable historical evidence.
  `DocumentTemplateConcurrencyTests` now passes twice on PostgreSQL, proving five exact PATCH
  requests resolve to one successor, one audit event, and one shared version-history row.
- The retained approval concurrency gate requires returned-cycle resubmissions to serialize without
  duplicate cycle-two ledgers. `SanctionSubmissionConcurrencyTests` now passes, and the complete
  historical five-race command passes twice on PostgreSQL.
- API §26.3, data-model §16.2, the permission boundary, metadata-only file projection, and unresolved
  Annexure rules are untouched. Original 008A API/model/permission tests remain green.

## Validation

- PostgreSQL: exact failing sanction test green; historical five-race command green twice; 008A
  five-request successor race green twice.
- Backend: Django check and migration sync green; 700 tests pass with 20 expected SQLite skips;
  coverage is 93% against an 85% floor.
- Frontend: build, typecheck, lint, and 269 tests pass; no frontend file changed.
- Evidence: red/green, scoped, PostgreSQL, and full-gate summaries are under `evidence/terminal-logs/`.

## Recommended Next Action

Run full independent validation. If green, let the orchestrator commit/merge/push, then run the due
architecture review before starting sharpened 008B.
