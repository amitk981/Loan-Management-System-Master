# Ralph Handoff

## Last Run
2026-07-10_213352_architecture_review

## Current Status

The due independent review covered `006E3`, `006F3`, `006G`, and `006H` from fixed point
`46442fe`. Production code was not changed. Epic 006 remains incomplete behind five corrective
slices.

- Critical: 006F3's committed packet says “Failed acceptance; do not commit or merge”; four
  PostgreSQL races were found and zero executed. 006G then merged with a fifth PostgreSQL-only race
  also unexecuted. 006F4 must execute all five twice with zero skips.
- High: migration 0005 downgrades non-draft legacy appraisals but the only revalidation path is
  draft-only; some review-pending/reviewed rows are permanently blocked, and returned-then-
  resubmitted latest reasons can miss backfill. 006E4/A-061 own conservative remediation.
- High: existing/returned workbench edits send the whole appraisal GET response on PATCH, including
  unknown response-only fields. Revalidation authority is wrong, action/status state is locally
  reconstructed, and static render tests never execute the container actions. 006H2 owns repair.
- High: the pending case UUID is lost on reload and submitted application/appraisal statuses are
  hard-coded in React because the server response/read does not provide them.
- Architecture: ADR-0005 assigns pending-case creation/read/enrichment to one approvals-owned deep
  module. 006G2 removes the concrete `credit -> approvals.models` dependency, adds the canonical
  state/case read, and envelopes malformed JSON.
- Visual: 006H replaced the approved staged workbench/checklist/calculator composition without
  screenshots. 006H3 restores prototype fidelity and requires host visual-regression evidence.

## Validation

All configured review-run gates passed: Django check, migration sync, 372 backend tests with five
PostgreSQL-only skips, 93% coverage (85% floor), frontend lint/typecheck, 126 tests, and build.
Review window, production diff, finding trace, and gate logs are under
`.ralph/runs/2026-07-10_213352_architecture_review/evidence/terminal-logs/`.

The five skipped tests are the open acceptance defect, not proof. 006F4 must run them through
`sfpcl_credit.config.postgres_test_settings`; connection/sandbox failure must fail that slice.

## Next Run

Run `006E4-legacy-appraisal-remediation-and-history-backfill`, then
`006F4-postgresql-credit-concurrency-acceptance`. Continue through 006G2, 006H2, and 006H3 before
the `006X` two-role tracer. Do not promote the current Epic 006 handoff as concurrency- or
visual-accepted.
