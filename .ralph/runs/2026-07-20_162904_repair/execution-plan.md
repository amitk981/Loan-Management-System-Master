# Execution Plan

## Repair Boundary

Repair only the independently demonstrated backend coverage failure from run
`2026-07-20_153054_normal_run`: five SQLite test-database setup errors reporting that the
`witnesses` table lacks `verification_folio_number`. Preserve the existing 010I DPD implementation
and do not broaden product scope.

## Plan

1. Inspect the exact failing labels and schema setup path from the retained coverage log.
2. Build a fast deterministic reproduction that asserts the missing-column failure.
3. Compare the witness model, migrations, and any test migration-module overrides to identify the
   smallest candidate-owned cause.
4. Apply the minimal repair, then rerun the reproduction and the affected DPD-focused checks with
   `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
5. Run backend check and migration-sync checks; do not repeat the complete backend suite locally.
6. Save red/green evidence plus `risk-assessment.md`, `review-packet.md`, and `final-summary.md`, with
   the review result set exactly to `Ready for independent validation`.

## Outcome

- The standalone witness migration selector reproduced the retained missing-column failure exactly.
- Root cause: the new `monitoring` migration leaf was included when two historical migration tests
  projected old application state, which made the projected ORM state outrun the reversed schema.
- Both affected projection filters now exclude the downstream monitoring owner.
- All five originally failing tests, the eight focused DPD tests, Django check, migration sync, and
  diff hygiene are green. Full independent validation remains owned by the orchestrator.

## Permissions and Safety

- Read permissions from `.ralph/permissions.json` were checked before editing.
- Candidate code, tests, docs/working, and the current run folder are allowed paths.
- Protected files, `docs/source/`, orchestrator-owned state/progress/status facts, and git metadata
  will not be modified.
