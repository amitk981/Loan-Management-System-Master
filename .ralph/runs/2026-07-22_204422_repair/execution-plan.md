# Execution Plan — 011G Closure Readiness Repair

## Boundary

Preserve the current 011G candidate and repair only the complete-backend validation domain demonstrated by
`.ralph/runs/2026-07-22_201550_repair/failure-summary.md`: the historical credit model-ownership migration test
cannot resolve `applications.EligibilityAssessment` while creating its pre-move fixture.

## Permission Check

- Product/test edits are limited to `sfpcl_credit/**`, which `.ralph/permissions.json` allows.
- Run evidence is limited to `.ralph/runs/2026-07-22_204422_repair/**`, which is allowed.
- `docs/source/**`, protected workflow/configuration files, orchestrator-owned mechanical facts, and unrelated
  candidate files will not be edited.

## Feedback Loop and Repair Steps

1. Reproduce the exact failing migration test with the mandated Ralph backend interpreter and save the RED output.
2. Inspect only the test's migration-state construction and the migration graph needed to explain the missing
   historical model; rank falsifiable hypotheses before changing the candidate.
3. Use the existing failing test as the regression seam unless diagnosis proves it cannot represent the reported
   failure. Apply the smallest repair that restores the intended historical pre-move state without changing product
   migration history or weakening assertions.
4. Re-run the exact named test until green, then run the focused migration ownership module and any same-domain
   migration consumer tests revealed by that validator.
5. Run Django check and migration consistency, remove temporary instrumentation, and save diagnosis, red/green
   logs, risk assessment, final summary, and a review packet whose Result is exactly
   `Ready for independent validation`.

## Intended Validation

- Exact feedback loop:
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python sfpcl_credit/manage.py test sfpcl_credit.tests.test_credit_model_ownership_migration --verbosity 2`
- Static checks:
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python sfpcl_credit/manage.py check`
  and
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python sfpcl_credit/manage.py makemigrations --check --dry-run`

The orchestrator remains responsible for the authoritative complete-suite coverage rerun required by the repair
prompt; the agent will not duplicate that full lane.
