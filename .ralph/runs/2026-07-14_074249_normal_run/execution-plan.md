# Execution Plan

Selected slice: `007S-register-pattern-and-pagination-order-closure`

## Scope and constraints

- Change only the shared authenticated pagination boundary, S21 sanction workbench request
  ordering, S23/S25 approved register composition, approval-case selector/query ownership, their
  tests, declared browser specs, and Ralph evidence/state documentation.
- Preserve the API DTOs, routes, filters, immutable/null semantics, v2 historical visibility,
  malformed-v3 nondisclosure, and existing design classes/components.
- Do not modify protected files or `docs/source/`; do not create migrations or dependencies.

## Behaviour-first implementation

1. Add a table-driven shared-client test covering exact valid empty/first/middle/final pages and
   malformed remainder, excess-row, impossible page/total, and navigation combinations. Capture
   RED, make the smallest validator correction, and capture GREEN.
2. Add S21 component tests with controlled list/detail promises proving only the newest filter/page
   generation may set queue, total, selection, detail, decision, error, or empty state. Capture RED,
   add a single request-generation guard with atomic stale clearing, then capture GREEN.
3. Replace the S23/S25 four-column evidence-dense tables with the existing scan table plus selected
   row card/detail composition. Update component tests and valid pagination fixtures, including a
   null-safe legacy S23 row and no inferred download control. Keep all 007Q facts visible.
4. Add backend public-behaviour instrumentation proving the selector performs actor/type/status/
   assignment shaping, deterministic ordering, and page-query mechanics before engine validation,
   while canonical engine validation alone decides countable rows. Capture RED, move those query
   mechanics behind `approval_case_selector`, and capture GREEN using the mandated backend venv.
5. Update the three declared Playwright specs for delayed S21 ordering and the restored selected
   detail evidence. Consolidate screenshot-quality checks behind one helper and run Playwright
   collection; do not fabricate screenshots if Chromium is sandbox-blocked.

## Verification and closeout

- Run focused frontend/backend tests during each RED/GREEN cycle, then frontend test/typecheck/
  lint/build and backend check/migration-sync/full coverage gates.
- Run the applicable standards/spec review, record findings/fixes, and save all terminal output in
  `evidence/terminal-logs/`.
- Save `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`; update
  the Epic 007 digest, selected slice status, Ralph state/progress, and handoff.
- Sharpen the next one or two `Not Started` slices only from source material already opened, while
  respecting the 30-file/2,000-line run limits.
