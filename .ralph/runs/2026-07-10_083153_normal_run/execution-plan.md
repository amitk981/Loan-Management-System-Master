# Execution Plan

Selected slice: `006D-loan-limit-snapshot-storage`

## Scope

Add a read-only stored loan-limit assessment endpoint and persist only the minimum policy-source
snapshot needed to serialize an assessment without consulting mutable configuration. Preserve the
existing 006C calculator and one-to-one assessment identity. No frontend, override, appraisal, or
new formula work is included.

## TDD sequence

1. Add one API test proving `GET /api/v1/loan-applications/{id}/loan-limit-assessment/` returns the
   original stored numeric, identifier, warning, rule-version, and policy-source values after the
   underlying application/shareholding/land/crop/policy records are mutated. Run it first and save
   the expected red failure.
2. Add the minimum model fields and migration for immutable policy config UUID, policy name, and
   Board approval reference; populate them only after a successful calculation. Add the GET route,
   read permission/object-access checks, stored-assessment lookup, and serializer that reads only
   assessment fields. Run the tracer test and save green evidence.
3. Add incremental API tests for missing-assessment 404, read permission/object-scope denial, no
   read audit/workflow writes, successful rerun snapshot replacement with old/new audit values,
   and failed rerun preservation. Implement only what each failing behavior requires.
4. Update the working API contract and Epic 006 digest to distinguish immutable stored snapshot
   output from mutable source records.

## Files expected to change

- `sfpcl_credit/applications/models.py`
- `sfpcl_credit/applications/migrations/0009_*.py`
- `sfpcl_credit/applications/services.py`
- `sfpcl_credit/applications/views.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/tests/test_loan_applications_api.py`
- `docs/working/API_CONTRACTS.md`
- `docs/working/digests/epic-006-eligibility-loan-limit-appraisal.md`
- Ralph state/progress/handoff, selected/next slice files, and this run's evidence/review artifacts

## Verification

- Focused red/green loan-application API tests using
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python` with terminal output saved under
  `evidence/terminal-logs/`.
- Backend check, full test suite, migration drift check, and coverage at or above 85%.
- Frontend lint, typecheck, tests, and build because they are mandatory repository gates even though
  this slice has no frontend changes.
- `git diff --check`, protected-path review, changed-file/diff-limit review, and API response example.
