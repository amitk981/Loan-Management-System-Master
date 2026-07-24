# Execution Plan

Selected slice: 012B-register-exports
Mode: same-worktree repair

## Demonstrated Failure

The independent `backend-coverage` lane failed only
`ApiContractHarnessUnitTests.test_production_code_does_not_use_legacy_permission_denied_literal`.
Its AST scan identified `reports/modules/report_export.py` because that candidate file contains two
production string constants with the retired `PERMISSION_DENIED` value.

## Permission Check

- `.ralph/permissions.json` permits edits under `sfpcl_credit/**` and `.ralph/runs/**`.
- This repair will not touch protected files, `docs/source/**`, queue/state/progress bookkeeping, or
  any unrelated candidate path.
- The current slice candidate is preserved in place.

## Repair Steps

1. Run the exact failing contract-harness test with the mandated Ralph Python interpreter and retain
   its red output.
2. Replace only the two retired permission-code literals in the report export module with the shared
   canonical `FORBIDDEN` constant.
3. Re-run the exact contract-harness test until green, then run the focused report-export tests to
   prove request denial, audit sanitisation, and failure handling remain intact.
4. Run Django system check and migration-sync check; do not run the complete backend suite or full
   coverage because independent validation owns that authoritative lane.
5. Save repair evidence, risk assessment, review packet, and final summary. Leave the review result
   exactly `Ready for independent validation`.

## Feedback Loop

Command:

`/Users/amitkallapa/LMS/.ralph/venv/bin/python sfpcl_credit/manage.py test sfpcl_credit.tests.test_api_contract_harness.ApiContractHarnessUnitTests.test_production_code_does_not_use_legacy_permission_denied_literal --verbosity 2`

Expected red signal: offender list contains `reports/modules/report_export.py`.
Expected green signal: one test passes with exit code 0.
