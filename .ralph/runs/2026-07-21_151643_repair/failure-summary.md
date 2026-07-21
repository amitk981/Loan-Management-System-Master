# Failure Summary

- Run: 2026-07-21_151643_repair
- Mode: repair
- Slice: CR-015-epic-010-terminal-servicing-owner-finalizer
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAIL: test_bounded_active_portfolio_reports_each_outcome (sfpcl_credit.tests.test_dpd_monitoring_api.DpdMonitoringApiTests.test_bounded_active_portfolio_reports_each_outcome)
backend-coverage-results.md:FAILED (failures=1)
```

## Last 50 lines: backend-coverage-results.md

```
Catalogue seeded: 189 permissions, 20 roles, 8 teams, 225 role-permission links.
..............................................................................................................................................................................................................................................................................................................................................................................................................................Catalogue seeded: 189 permissions, 20 roles, 8 teams, 225 role-permission links.
..............F
======================================================================
FAIL: test_bounded_active_portfolio_reports_each_outcome (sfpcl_credit.tests.test_dpd_monitoring_api.DpdMonitoringApiTests.test_bounded_active_portfolio_reports_each_outcome)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 57, in testPartExecutor
    yield
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 623, in run
    self._callTestMethod(testMethod)
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 579, in _callTestMethod
    if method() is not None:
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_141242_normal_run/sfpcl_credit/tests/test_dpd_monitoring_api.py", line 179, in test_bounded_active_portfolio_reports_each_outcome
    self.assertLessEqual(len(queries), 20)
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 1265, in assertLessEqual
    self.fail(self._formatMessage(msg, standardMsg))
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 703, in fail
    raise self.failureException(msg)
    ^^^^^^^^^^^^^^^^^
AssertionError: 21 not less than or equal to 20

----------------------------------------------------------------------
Ran 548 tests in 38.056s

FAILED (failures=1)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 60.509s
  Creating 'default' took 60.428s
  Cloning 'default' took 0.011s
  Cloning 'default' took 0.011s
  Cloning 'default' took 0.012s
  Cloning 'default' took 0.014s
  Cloning 'default' took 0.014s
  Cloning 'default' took 0.017s
Total database teardown took 0.010s
Total run took 100.124s

Duration milliseconds: 100795
Exit code: 1
```

## Changed files (git status)

```
.ralph/runs/2026-07-21_141242_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-21_141242_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-21_141242_normal_run/backend-check-results.md
.ralph/runs/2026-07-21_141242_normal_run/backend-coverage-results.md
.ralph/runs/2026-07-21_141242_normal_run/backend-impacted-results.md
.ralph/runs/2026-07-21_141242_normal_run/backend-migrations-results.md
.ralph/runs/2026-07-21_141242_normal_run/backend-test-results.md
.ralph/runs/2026-07-21_141242_normal_run/backend-validation-lane-results.md
.ralph/runs/2026-07-21_141242_normal_run/build-results.md
.ralph/runs/2026-07-21_141242_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-21_141242_normal_run/candidate-hash-results.md
.ralph/runs/2026-07-21_141242_normal_run/changed-files.txt
.ralph/runs/2026-07-21_141242_normal_run/codex-settings.md
.ralph/runs/2026-07-21_141242_normal_run/diff-limits-results.md
.ralph/runs/2026-07-21_141242_normal_run/e2e-results.md
.ralph/runs/2026-07-21_141242_normal_run/evidence/postgresql-environment-validation.md
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/backend-check.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/backend-focused-final.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/backend-focused-regressions-final.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/backend-focused-regressions.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/direct-repayment-backend-green.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/direct-repayment-backend-red.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/direct-repayment-frontend-green.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/direct-repayment-frontend-red.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/django-check-final.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/frontend-build-final.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/frontend-build.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/frontend-focused-final.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/frontend-focused-tests.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/frontend-lint-final.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/frontend-lint.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/frontend-typecheck-final.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/frontend-typecheck.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/instruction-projection-green.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/instruction-projection-red.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/migration-check-final.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/migration-sync.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/mis-owner-green.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/mis-owner-red.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/portal-pagination-green.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/portal-pagination-red.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/postgresql-acceptance-authoritative-pass-1.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/postgresql-acceptance-authoritative-pass-2.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/postgresql-acceptance-final-pass-1.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/postgresql-acceptance-final-pass-2.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/postgresql-acceptance-green-pass-1.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/postgresql-acceptance-green-pass-2.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/postgresql-acceptance-local.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/postgresql-acceptance-validation-1.txt
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/postgresql-acceptance-validation-2.txt
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/reminder-owner-green.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/reminder-owner-red.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/statement-owner-green.log
.ralph/runs/2026-07-21_141242_normal_run/evidence/terminal-logs/statement-owner-red.log
.ralph/runs/2026-07-21_141242_normal_run/execution-plan.md
.ralph/runs/2026-07-21_141242_normal_run/failure-summary.md
.ralph/runs/2026-07-21_141242_normal_run/final-summary.md
.ralph/runs/2026-07-21_141242_normal_run/impact-analysis-check-results.md
.ralph/runs/2026-07-21_141242_normal_run/impact-analysis.md
.ralph/runs/2026-07-21_141242_normal_run/install-results.md
.ralph/runs/2026-07-21_141242_normal_run/lint-results.md
.ralph/runs/2026-07-21_141242_normal_run/no-op-check-results.md
.ralph/runs/2026-07-21_141242_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-21_141242_normal_run/postgresql-acceptance-results.md
.ralph/runs/2026-07-21_141242_normal_run/preflight-results.md
.ralph/runs/2026-07-21_141242_normal_run/prompt.md
.ralph/runs/2026-07-21_141242_normal_run/protected-paths-check.md
.ralph/runs/2026-07-21_141242_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-21_141242_normal_run/review-closure-contract-results.md
.ralph/runs/2026-07-21_141242_normal_run/review-closure-evidence.md
.ralph/runs/2026-07-21_141242_normal_run/review-packet.md
.ralph/runs/2026-07-21_141242_normal_run/risk-assessment.md
.ralph/runs/2026-07-21_141242_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-21_141242_normal_run/slice-status-transition-check.md
.ralph/runs/2026-07-21_141242_normal_run/test-results.md
.ralph/runs/2026-07-21_141242_normal_run/typecheck-results.md
.ralph/runs/2026-07-21_141242_normal_run/validated-commit-candidate.sha256
.ralph/runs/2026-07-21_150232_repair/agent-declared-result-check.md
.ralph/runs/2026-07-21_150232_repair/artifact-quality-check.md
.ralph/runs/2026-07-21_150232_repair/backend-check-results.md
.ralph/runs/2026-07-21_150232_repair/backend-coverage-results.md
.ralph/runs/2026-07-21_150232_repair/backend-impacted-results.md
.ralph/runs/2026-07-21_150232_repair/backend-migrations-results.md
.ralph/runs/2026-07-21_150232_repair/backend-test-results.md
.ralph/runs/2026-07-21_150232_repair/backend-validation-lane-results.md
.ralph/runs/2026-07-21_150232_repair/build-results.md
.ralph/runs/2026-07-21_150232_repair/candidate-fast-check-results.md
.ralph/runs/2026-07-21_150232_repair/candidate-hash-results.md
.ralph/runs/2026-07-21_150232_repair/changed-files.txt
.ralph/runs/2026-07-21_150232_repair/codex-settings.md
.ralph/runs/2026-07-21_150232_repair/diff-limits-results.md
.ralph/runs/2026-07-21_150232_repair/e2e-results.md
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/communication-final-accepted-green.log
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/communication-final-accepted-red.log
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/communication-nonfinal-accepted-green.log
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/communication-nonfinal-accepted-probe.log
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/communication-worker-runtime-green.log
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/direct-repayment-backend-green.log
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/direct-repayment-backend-red.log
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/django-check.log
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/migration-check.log
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/mis-owner-green.log
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/mis-owner-red.log
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/postgresql-acceptance-authoritative-pass-2.log
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/postgresql-acceptance-validation-1.txt
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/postgresql-acceptance-validation-2.txt
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/reminder-owner-green.log
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/reminder-owner-red.log
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/review-closure-validator.log
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/statement-owner-green.log
.ralph/runs/2026-07-21_150232_repair/execution-plan.md
.ralph/runs/2026-07-21_150232_repair/failure-summary.md
.ralph/runs/2026-07-21_150232_repair/final-summary.md
.ralph/runs/2026-07-21_150232_repair/impact-analysis.md
.ralph/runs/2026-07-21_150232_repair/install-results.md
.ralph/runs/2026-07-21_150232_repair/lint-results.md
.ralph/runs/2026-07-21_150232_repair/orchestrator-ownership-check.md
.ralph/runs/2026-07-21_150232_repair/postgresql-acceptance-results.md
.ralph/runs/2026-07-21_150232_repair/preflight-results.md
.ralph/runs/2026-07-21_150232_repair/prompt.md
.ralph/runs/2026-07-21_150232_repair/protected-paths-check.md
.ralph/runs/2026-07-21_150232_repair/ralph-artifact-validation.md
.ralph/runs/2026-07-21_150232_repair/review-closure-contract-results.md
.ralph/runs/2026-07-21_150232_repair/review-closure-evidence.md
.ralph/runs/2026-07-21_150232_repair/review-packet.md
.ralph/runs/2026-07-21_150232_repair/risk-assessment.md
.ralph/runs/2026-07-21_150232_repair/slice-queue-lint.md
.ralph/runs/2026-07-21_150232_repair/slice-status-transition-check.md
.ralph/runs/2026-07-21_150232_repair/test-results.md
.ralph/runs/2026-07-21_150232_repair/typecheck-results.md
.ralph/runs/2026-07-21_150232_repair/validated-commit-candidate.sha256
.ralph/runs/2026-07-21_151643_repair/agent-declared-result-check.md
.ralph/runs/2026-07-21_151643_repair/artifact-quality-check.md
.ralph/runs/2026-07-21_151643_repair/candidate-fast-check-results.md
.ralph/runs/2026-07-21_151643_repair/changed-files.txt
.ralph/runs/2026-07-21_151643_repair/codex-settings.md
.ralph/runs/2026-07-21_151643_repair/diff-limits-results.md
.ralph/runs/2026-07-21_151643_repair/evidence/postgresql-environment-validation.md
.ralph/runs/2026-07-21_151643_repair/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-21_151643_repair/evidence/terminal-logs/communication-owner-boundary-green.log
.ralph/runs/2026-07-21_151643_repair/evidence/terminal-logs/communication-regressions-green.log
.ralph/runs/2026-07-21_151643_repair/evidence/terminal-logs/direct-repayment-backend-green.log
.ralph/runs/2026-07-21_151643_repair/evidence/terminal-logs/direct-repayment-backend-red.log
.ralph/runs/2026-07-21_151643_repair/evidence/terminal-logs/direct-repayment-idempotency-green.log
.ralph/runs/2026-07-21_151643_repair/evidence/terminal-logs/direct-repayment-idempotency-red.log
.ralph/runs/2026-07-21_151643_repair/evidence/terminal-logs/direct-repayment-regressions-green.log
.ralph/runs/2026-07-21_151643_repair/evidence/terminal-logs/django-check.log
.ralph/runs/2026-07-21_151643_repair/evidence/terminal-logs/migration-check.log
.ralph/runs/2026-07-21_151643_repair/evidence/terminal-logs/mis-owner-green.log
.ralph/runs/2026-07-21_151643_repair/evidence/terminal-logs/mis-owner-red.log
.ralph/runs/2026-07-21_151643_repair/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-21_151643_repair/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-21_151643_repair/evidence/terminal-logs/postgresql-acceptance-pass-1.log
.ralph/runs/2026-07-21_151643_repair/evidence/terminal-logs/postgresql-acceptance-pass-2.log
.ralph/runs/2026-07-21_151643_repair/evidence/terminal-logs/postgresql-probe-cleanup.log
.ralph/runs/2026-07-21_151643_repair/evidence/terminal-logs/reminder-competing-workers-green.log
.ralph/runs/2026-07-21_151643_repair/evidence/terminal-logs/reminder-owner-green.log
.ralph/runs/2026-07-21_151643_repair/evidence/terminal-logs/reminder-owner-red.log
.ralph/runs/2026-07-21_151643_repair/evidence/terminal-logs/review-closure-validator.log
.ralph/runs/2026-07-21_151643_repair/evidence/terminal-logs/statement-owner-green.log
.ralph/runs/2026-07-21_151643_repair/execution-plan.md
.ralph/runs/2026-07-21_151643_repair/final-summary.md
.ralph/runs/2026-07-21_151643_repair/impact-analysis.md
.ralph/runs/2026-07-21_151643_repair/orchestrator-ownership-check.md
.ralph/runs/2026-07-21_151643_repair/preflight-results.md
.ralph/runs/2026-07-21_151643_repair/prompt.md
.ralph/runs/2026-07-21_151643_repair/protected-paths-check.md
.ralph/runs/2026-07-21_151643_repair/ralph-artifact-validation.md
.ralph/runs/2026-07-21_151643_repair/review-closure-evidence.md
.ralph/runs/2026-07-21_151643_repair/review-packet.md
.ralph/runs/2026-07-21_151643_repair/risk-assessment.md
.ralph/runs/2026-07-21_151643_repair/slice-queue-lint.md
.ralph/runs/2026-07-21_151643_repair/slice-status-transition-check.md
docs/working/API_CONTRACTS.md
sfpcl-lms/src/pages/borrower/portal/loans/PortalLoanViews.test.tsx
sfpcl-lms/src/services/portalApi.test.ts
sfpcl-lms/src/services/portalApi.ts
sfpcl-lms/src/services/servicingApi.test.ts
sfpcl-lms/src/services/servicingApi.ts
sfpcl_credit/communications/modules/communication_dispatcher.py
sfpcl_credit/config/urls.py
sfpcl_credit/configurations/migrations/0009_repaymentinstructionversion_and_more.py
sfpcl_credit/configurations/models.py
sfpcl_credit/loans/modules/direct_repayment_posting.py
sfpcl_credit/loans/modules/dpd_source_decision.py
sfpcl_credit/loans/views.py
sfpcl_credit/monitoring/modules/quarterly_mis.py
sfpcl_credit/monitoring/modules/reminder_engine.py
sfpcl_credit/processes/communication_delivery.py
sfpcl_credit/processes/direct_repayment_command.py
sfpcl_credit/processes/loan_ledger_statements.py
sfpcl_credit/processes/portal_loan_servicing.py
sfpcl_credit/tests/servicing_builders.py
sfpcl_credit/tests/test_epic010_terminal_owner_finalizer.py
sfpcl_credit/tests/test_portal_loan_accounts_api.py
```
