# Review Packet: 2026-07-10_175450_normal_run

## Result
Success pending required PostgreSQL independent validation

## Slice
006D2C-loan-limit-concurrency-and-boundary-regression

## Outcome

- Added two `TransactionTestCase` regressions using independent Django connections and deterministic
  barriers around `LoanLimitCalculator.calculate_for_application(...)`.
- Valid/valid reruns must serialize, retain one row and UUID, keep each source snapshot internally
  consistent, commit matching audit/workflow evidence, and leave the final audit projection equal
  to the final row.
- Valid/invalid competition must leave the valid snapshot and exactly one success evidence pair;
  the invalid request cannot overwrite state or record success.
- Replaced boundary loopholes with resolved `ast.Import`/`ast.ImportFrom` package/alias inspection,
  concrete assessment/policy/private-helper rejection, positive public-import requirements, and
  required-method subset checks.
- No formula, API, persistence, permission, rerun, audit payload, response, model, or migration
  behavior changed.

## Architecture Map

`applications.views` -> public `LoanLimitCalculator` / `AppraisalWorkflow` -> owning credit modules.
Only `loan_limit_calculator` owns concrete eligibility/loan-limit persistence during calculation;
only `configuration_resolver` owns direct `LoanPolicyConfig` access. Appraisal consumes the public
calculator projection and cannot import concrete assessment models.

## Traceability

- Codebase-design §26.1/§26.3 says financial behavior is tested through its module interface with
  concurrency coverage; the new PostgreSQL transaction tests call the public calculator and assert
  committed outcomes rather than mocked lock calls.
- Data-model §34 says assessment, audit, and workflow rows update atomically; both competition tests
  assert row/evidence cardinality and final projection consistency.
- API §3 and data-model §14.2 require snapshot decisions and the named financial inputs/results;
  the valid/valid test uses two share sources and proves the final snapshot is one complete source
  set, not mixed fields.
- Codebase-design §§12.2-12.3 require calculator/appraisal seams; static fixtures reject bypasses
  and positively require those imports without freezing unrelated class shape.

## TDD Evidence

- `evidence/terminal-logs/boundary-red.log`
- `evidence/terminal-logs/boundary-package-red.log`
- `evidence/terminal-logs/boundary-fixtures-red.log`
- `evidence/terminal-logs/boundary-positive-red.log`
- Matching `*-green.log` files and `boundary-suite-green.log`
- `evidence/terminal-logs/concurrency-postgres-red.log` proves the initial missing configuration.
- `evidence/terminal-logs/concurrency-driver-missing.log` proves the completed settings reach the
  expected offline-only missing pinned-driver boundary.
- `evidence/terminal-logs/concurrency-sqlite-explicit-nonproof.log` records the backend and explicit
  non-proof skips.

## Validation

- Backend check: pass.
- Migration sync: pass; no changes detected.
- Focused characterization: 90 pass, 2 PostgreSQL-only skips under SQLite.
- Full backend coverage gate: 347 pass, 2 PostgreSQL-only skips, 94% >= 85%.
- Frontend lint/typecheck: pass.
- Frontend tests: 107 pass across 16 files.
- Frontend build: pass; existing non-blocking bundle-size warning only.
- `git diff --check`: pass.

## Mandatory Independent PostgreSQL Gate

After installing `sfpcl_credit/requirements.txt` and provisioning PostgreSQL with the environment
variables supported by `sfpcl_credit.config.postgres_test_settings`, run:

```bash
/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py test sfpcl_credit.tests.test_credit_modules.LoanLimitConcurrencyTests --settings=sfpcl_credit.config.postgres_test_settings -v 2
```

Required result: both tests pass and print `database_backend=postgresql` with the serialized order.
A SQLite skip is not acceptance evidence. Do not commit/merge this slice if this command fails.

## Recommended Next Action
Install the pinned dependency, run the mandatory PostgreSQL gate, then let the orchestrator validate
and commit. After that, run 006E2 and then 006F.
