# Execution Plan

Selected slice: `005I3-application-nominee-selection-contract`

## Outcome

Make one existing adult member nominee an explicit, application-owned fact across staff and member
portal draft flows. Detail responses expose only safe nominee metadata, submission/completeness and
normal eligibility depend on the stored selection, and eligibility no longer chooses a reverse-linked
nominee by ordering.

## Permission And Scope Check

- Product edits are limited to `sfpcl_credit/**` and `sfpcl-lms/src/**`, both allowed by
  `.ralph/permissions.json`.
- Contract, digest, assumption, handoff, progress, slice, and run-evidence edits are limited to
  allowed `docs/working/**`, `docs/slices/**`, `.ralph/state.json`, `.ralph/progress.md`, and
  `.ralph/runs/**` paths.
- `docs/source/**` and every protected path remain read-only.
- The High-risk slice has standing owner approval and no veto entry.

## TDD Tracer Bullets

1. Add a staff HTTP create/detail test for a same-member adult nominee; capture RED, add the nullable
   protected FK migration and shared validation/serialization, then capture GREEN.
2. Add staff update and invalid-selection HTTP tests one behavior at a time: cross-member, unknown,
   minor, and missing age evidence. Assert no application/audit/workflow mutation on each failure.
3. Add submit-without-selection and select-then-submit HTTP tests; extend the existing submit gate
   and ensure completeness/reference paths cannot bypass it.
4. Add equivalent portal create/update/detail tests through authenticated own-member endpoints,
   including safe metadata and invalid-path side-effect assertions.
5. Add eligibility HTTP regressions proving a legacy null selection remains pending and an explicit
   adult selection is eligible even when reverse-linked nominee rows exist; remove `.first()`
   selection from eligibility.
6. Add frontend service and render tests for real API nominee listing/selection, payload
   `nominee_id`, validation/empty states, and metadata-only staff/portal detail; implement with the
   existing form/select/detail-card patterns only.

Each backend/business behavior follows RED -> minimal GREEN before the next behavior. Logs go to
`evidence/terminal-logs/` under this run.

## Documentation And Evidence

- Add the field and safe summary to `docs/working/API_CONTRACTS.md` and distill any newly used source
  facts into the Epic 005 digest.
- Save staff/portal API examples, frontend visual evidence for selection/validation/detail, and all
  gate outputs inside this run folder.
- Record assumptions only if source documents are silent; never invent nominee business rules.
- Sharpen the next one or two Not Started slices using only source material already opened.

## Verification

- Focused backend tests with `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
- Focused frontend Vitest tests.
- Backend: `manage.py check`, full tests, `makemigrations --check --dry-run`, coverage >= 85%.
- Frontend: lint, typecheck, full tests, build.
- Review the complete worktree diff against the slice and documented standards, then write
  `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`.
- Update state, progress, handoff, and slice status only after every gate passes. Do not commit,
  add, or push; the Ralph orchestrator owns those actions.
