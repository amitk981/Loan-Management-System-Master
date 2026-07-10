# Ralph Handoff

## Last Run
2026-07-10_083153_normal_run

## Current Status
Completed `006D-loan-limit-snapshot-storage`.

What changed:
- Added `GET /api/v1/loan-applications/{loan_application_id}/loan-limit-assessment/` with
  `applications.loan_application.read` and existing application object access. Missing snapshots
  return `404`; reads calculate nothing and write no audit/workflow evidence.
- Added immutable policy config UUID, policy name, and Board approval reference snapshot columns.
  Calculate/GET responses and audit old/new values now serialize policy source only from the
  assessment row, never the mutable policy row.
- Proved application amount, shareholding, land/crop, and policy mutations cannot alter stored GET
  output until a successful rerun atomically replaces the snapshot while preserving its UUID.
- Proved invalid-state, missing-source, permission, and object-scope rerun failures preserve the
  prior snapshot and success-evidence counts.
- Updated the working API contract, Epic 006 digest, and A-048 legacy-row migration behavior.
  Revalidated already-concrete 006E and sharpened 006F Credit Manager review requirements from
  source §24.4, data model §14.4, auth permissions, and appraisal test-plan cases.

## Validation
- Backend TDD stored-GET tracer: red `404`, then green immutable snapshot read.
- Focused loan-application API suite passed: 39 tests.
- Backend `manage.py check` passed.
- Backend full suite passed: 290 tests.
- Backend `makemigrations --check --dry-run` passed.
- Backend coverage passed: 95%, above the 85% floor.
- Frontend lint and typecheck passed.
- Frontend tests passed: 98 tests.
- Frontend build passed.
- `git diff --check` passed; no protected files changed; diff limits remain within configured caps.

Evidence is in `.ralph/runs/2026-07-10_083153_normal_run/`.

## Next Run
Run the architecture review now due after four completed slices, then run
`006E-appraisal-note-create-edit-submit`.

Key instructions for 006E:
- Require stored eligible 006B and stored 006D loan-limit snapshots before appraisal creation;
  consume them without recalculation.
- Implement one appraisal/risk assessment per application with draft-only update,
  source §24.1 fields, two-day immutable TAT due facts, and submit-for-review.
- Enforce create/update/submit-review/risk permissions separately with existing application object
  access, metadata-only evidence, and no free-text summaries in audit JSON.
