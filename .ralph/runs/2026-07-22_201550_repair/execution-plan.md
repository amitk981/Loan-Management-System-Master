# Execution Plan — 011G Closure Readiness Repair

## Boundary

Preserve the current 011G candidate and repair only the backend coverage validation domain demonstrated by
`.ralph/runs/2026-07-22_200332_repair/failure-summary.md`: the bounded DPD monitoring portfolio response
executes 23 queries while its established regression contract permits at most 20.

## Permission Check

- Product edits are limited to `sfpcl_credit/**`, which `.ralph/permissions.json` allows.
- Run evidence is limited to `.ralph/runs/2026-07-22_201550_repair/**`, which is allowed.
- `docs/source/**`, protected workflow/configuration files, orchestrator-owned mechanical facts, and unrelated
  candidate files will not be edited.

## Feedback Loop and Repair Steps

1. Reproduce the exact failing test with the mandated Ralph backend interpreter and save the RED output.
2. Inspect only the DPD monitoring API query path and its test fixture/query capture to rank and test bounded
   query-count hypotheses.
3. Add or refine the smallest regression assertion only if the existing failing test is not already a correct
   seam; make the minimal production/test-fixture repair that restores the established `<= 20` contract.
4. Re-run the exact named test until green, then run the focused DPD monitoring test module to catch errors
   subsequently revealed in the same validator domain.
5. Save diagnosis, terminal evidence, risk assessment, and a self-contained review packet whose Result is
   exactly `Ready for independent validation`.

## Intended Validation

- Exact feedback loop:
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python sfpcl_credit/manage.py test sfpcl_credit.tests.test_dpd_monitoring_api.DpdMonitoringApiTests.test_bounded_active_portfolio_reports_each_outcome --verbosity 2`
- Focused same-domain suite:
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python sfpcl_credit/manage.py test sfpcl_credit.tests.test_dpd_monitoring_api --verbosity 2`
- Cheap backend static checks if the repair changes production code:
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python sfpcl_credit/manage.py check`
  and
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python sfpcl_credit/manage.py makemigrations --check --dry-run`

The orchestrator remains responsible for the authoritative complete-suite coverage rerun.

## Completion

- Exact RED reproduced and saved.
- Root cause isolated to the redundant generic update guard on the already-locked DPD pointer path.
- Minimal closed-conditional pointer update implemented; temporary instrumentation removed.
- Exact GREEN, focused DPD, closure/repayment reverse consumers, static checks, and artifact checks passed.
- Candidate is ready for Ralph's independent complete coverage and PostgreSQL acceptance validation.
