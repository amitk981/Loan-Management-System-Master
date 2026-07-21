# Failure Summary

- Run: 2026-07-21_150232_repair
- Mode: repair
- Slice: CR-015-epic-010-terminal-servicing-owner-finalizer
- Failed checks: 2

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAIL: test_sap_posting_requires_permission_reference_and_records_safe_audit_truth (sfpcl_credit.tests.test_direct_repayment_posting_api.DirectRepaymentPostingApiTests.test_sap_posting_requires_permission_reference_and_records_safe_audit_truth)
backend-coverage-results.md:FAILED (failures=1)
postgresql-acceptance-results.md:- FAIL: first independent run did not satisfy the slice contract and exact count.
postgresql-acceptance-results.md:- FAIL: second independent run did not satisfy the slice contract and exact count.
postgresql-acceptance-results.md:- FAIL: PostgreSQL environment evidence is missing.
```

## Last 50 lines: postgresql-acceptance-results.md

```
# PostgreSQL Acceptance Results

- Contract expected tests: 5
- Contract labels:
  - sfpcl_credit.tests.test_epic010_terminal_owner_finalizer.Epic010TerminalOwnerFinalizerPostgreSQLAcceptanceTests
- FAIL: first independent run did not satisfy the slice contract and exact count.
- FAIL: second independent run did not satisfy the slice contract and exact count.
- FAIL: PostgreSQL environment evidence is missing.
```

## Last 50 lines: backend-coverage-results.md

```
.......................................................................................................................Catalogue seeded: 189 permissions, 20 roles, 8 teams, 225 role-permission links.
Catalogue seeded: 189 permissions, 20 roles, 8 teams, 225 role-permission links.
.................................................................................................................................................................................................................................................................................................................................................F
======================================================================
FAIL: test_sap_posting_requires_permission_reference_and_records_safe_audit_truth (sfpcl_credit.tests.test_direct_repayment_posting_api.DirectRepaymentPostingApiTests.test_sap_posting_requires_permission_reference_and_records_safe_audit_truth)
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
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_141242_normal_run/sfpcl_credit/tests/test_direct_repayment_posting_api.py", line 167, in test_sap_posting_requires_permission_reference_and_records_safe_audit_truth
    self.assertEqual(repeated.status_code, 409, repeated.content)
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 873, in assertEqual
    assertion_func(first, second, msg=msg)
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 866, in _baseAssertEqual
    raise self.failureException(msg)
    ^^^^^^^^^^^^^^^^^
AssertionError: 200 != 409 : b'{"success": true, "data": {"repayment_id": "83adecaa-776b-4019-afed-e24f5d92d877", "loan_account_id": "c1f220c0-11bb-4846-8b56-35c37ceaeda7", "repayment_source": "direct_farmer", "amount_received": "100000.00", "received_date": "2026-12-04", "payment_method": "rtgs", "bank_reference_number": "UTR-DIRECT-VALIDATION-001", "bank_statement_line_id": null, "statement_match_status": "not_linked", "allocation_status": "pending", "sap_posting": {"status": "posted", "due_date": "2026-12-07", "sap_entry_reference": "SAP-RCPT-123", "posted_at": "2026-12-02T10:00:00Z"}}, "meta": {"request_id": "req-repayment-posting-001", "timestamp": "2026-07-21T09:46:41.460003Z", "api_version": "v1"}}'

----------------------------------------------------------------------
Ran 457 tests in 18.912s

FAILED (failures=1)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 58.760s
  Creating 'default' took 58.695s
  Cloning 'default' took 0.009s
  Cloning 'default' took 0.010s
  Cloning 'default' took 0.011s
  Cloning 'default' took 0.013s
  Cloning 'default' took 0.011s
  Cloning 'default' took 0.010s
Total database teardown took 0.002s
Total run took 78.190s

Duration milliseconds: 78832
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
.ralph/runs/2026-07-21_150232_repair/candidate-fast-check-results.md
.ralph/runs/2026-07-21_150232_repair/changed-files.txt
.ralph/runs/2026-07-21_150232_repair/codex-settings.md
.ralph/runs/2026-07-21_150232_repair/diff-limits-results.md
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
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/reminder-owner-green.log
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/reminder-owner-red.log
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/review-closure-validator.log
.ralph/runs/2026-07-21_150232_repair/evidence/terminal-logs/statement-owner-green.log
.ralph/runs/2026-07-21_150232_repair/execution-plan.md
.ralph/runs/2026-07-21_150232_repair/final-summary.md
.ralph/runs/2026-07-21_150232_repair/impact-analysis.md
.ralph/runs/2026-07-21_150232_repair/orchestrator-ownership-check.md
.ralph/runs/2026-07-21_150232_repair/preflight-results.md
.ralph/runs/2026-07-21_150232_repair/prompt.md
.ralph/runs/2026-07-21_150232_repair/protected-paths-check.md
.ralph/runs/2026-07-21_150232_repair/ralph-artifact-validation.md
.ralph/runs/2026-07-21_150232_repair/review-closure-evidence.md
.ralph/runs/2026-07-21_150232_repair/review-packet.md
.ralph/runs/2026-07-21_150232_repair/risk-assessment.md
.ralph/runs/2026-07-21_150232_repair/slice-queue-lint.md
.ralph/runs/2026-07-21_150232_repair/slice-status-transition-check.md
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
