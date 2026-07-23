# Failure Summary

- Run: 2026-07-23_104026_repair
- Mode: repair
- Slice: 011M2-member-portal-kyc-correction-request
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAILED (errors=1, skipped=91)
```

## Last 50 lines: backend-coverage-results.md

```
    ^^^^^^^^^^^^^^^^^
KeyError: 'eligibilityassessment'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 57, in testPartExecutor
    yield
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 619, in run
    self._callSetUp()
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 576, in _callSetUp
    self.setUp()
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_095043_normal_run/sfpcl_credit/tests/test_credit_model_ownership_migration.py", line 46, in setUp
    self.identifiers = self._create_pre_move_rows(old_apps)
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_095043_normal_run/sfpcl_credit/tests/test_credit_model_ownership_migration.py", line 150, in _create_pre_move_rows
    EligibilityAssessment = old_apps.get_model("applications", "EligibilityAssessment")
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/apps/registry.py", line 213, in get_model
    return app_config.get_model(model_name, require_ready=require_ready)
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/apps/config.py", line 237, in get_model
    raise LookupError(
    ^^^^^^^^^^^^^^^^^
LookupError: App 'applications' doesn't have a 'EligibilityAssessment' model.

----------------------------------------------------------------------
Ran 1561 tests in 1294.795s

FAILED (errors=1, skipped=91)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 81.163s
  Creating 'default' took 81.074s
  Cloning 'default' took 0.020s
  Cloning 'default' took 0.016s
  Cloning 'default' took 0.013s
  Cloning 'default' took 0.014s
  Cloning 'default' took 0.014s
  Cloning 'default' took 0.013s
Total database teardown took 0.033s
Total run took 1376.964s

Duration milliseconds: 1378079
Exit code: 1
```

## Changed files (git status)

```
.ralph/runs/2026-07-23_095043_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-23_095043_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-23_095043_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-23_095043_normal_run/changed-files.txt
.ralph/runs/2026-07-23_095043_normal_run/codex-settings.md
.ralph/runs/2026-07-23_095043_normal_run/diff-limits-results.md
.ralph/runs/2026-07-23_095043_normal_run/evidence/api-examples.md
.ralph/runs/2026-07-23_095043_normal_run/evidence/browser-acceptance.md
.ralph/runs/2026-07-23_095043_normal_run/evidence/permission-matrix.md
.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/backend-final-focused.log
.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/backend-final-integration.log
.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/backend-focused-integration.log
.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/backend-green-01-submission.log
.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/backend-green-02-own-scope.log
.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/backend-green-03-approve.log
.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/backend-green-04-reject.log
.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/backend-green-05-staff-queue.log
.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/backend-red-01-submission.log
.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/backend-red-02-own-scope.log
.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/backend-red-03-approve.log
.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/backend-red-04-reject.log
.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/backend-red-05-staff-queue.log
.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/browser-infrastructure-probe.log
.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/browser-portal-kyc-run-1.log
.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/browser-portal-kyc-run-2.log
.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/frontend-final-gates.log
.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/frontend-focused-tests.log
.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/frontend-green-01-kyc-correction-panel.log
.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/frontend-red-01-kyc-correction-panel.log
.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/frontend-typecheck-lint-build.log
.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-23_095043_normal_run/execution-plan.md
.ralph/runs/2026-07-23_095043_normal_run/failure-summary.md
.ralph/runs/2026-07-23_095043_normal_run/final-summary.md
.ralph/runs/2026-07-23_095043_normal_run/no-op-check-results.md
.ralph/runs/2026-07-23_095043_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-23_095043_normal_run/preflight-results.md
.ralph/runs/2026-07-23_095043_normal_run/prompt.md
.ralph/runs/2026-07-23_095043_normal_run/protected-paths-check.md
.ralph/runs/2026-07-23_095043_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-23_095043_normal_run/review-packet.md
.ralph/runs/2026-07-23_095043_normal_run/risk-assessment.md
.ralph/runs/2026-07-23_095043_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-23_095043_normal_run/slice-status-transition-check.md
.ralph/runs/2026-07-23_103351_repair/agent-declared-result-check.md
.ralph/runs/2026-07-23_103351_repair/artifact-quality-check.md
.ralph/runs/2026-07-23_103351_repair/backend-check-results.md
.ralph/runs/2026-07-23_103351_repair/backend-coverage-results.md
.ralph/runs/2026-07-23_103351_repair/backend-impacted-results.md
.ralph/runs/2026-07-23_103351_repair/backend-migrations-results.md
.ralph/runs/2026-07-23_103351_repair/backend-test-results.md
.ralph/runs/2026-07-23_103351_repair/backend-validation-lane-results.md
.ralph/runs/2026-07-23_103351_repair/build-results.md
.ralph/runs/2026-07-23_103351_repair/candidate-fast-check-results.md
.ralph/runs/2026-07-23_103351_repair/candidate-hash-results.md
.ralph/runs/2026-07-23_103351_repair/changed-files.txt
.ralph/runs/2026-07-23_103351_repair/codex-settings.md
.ralph/runs/2026-07-23_103351_repair/diff-limits-results.md
.ralph/runs/2026-07-23_103351_repair/e2e-results.md
.ralph/runs/2026-07-23_103351_repair/evidence/terminal-logs/agent-result-final.log
.ralph/runs/2026-07-23_103351_repair/evidence/terminal-logs/agent-result-green.log
.ralph/runs/2026-07-23_103351_repair/evidence/terminal-logs/agent-result-red.log
.ralph/runs/2026-07-23_103351_repair/evidence/terminal-logs/browser-infrastructure-probe.log
.ralph/runs/2026-07-23_103351_repair/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-23_103351_repair/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-23_103351_repair/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-23_103351_repair/evidence/terminal-logs/trusted-browser-acceptance-1.log
.ralph/runs/2026-07-23_103351_repair/execution-plan.md
.ralph/runs/2026-07-23_103351_repair/failure-summary.md
.ralph/runs/2026-07-23_103351_repair/final-summary.md
.ralph/runs/2026-07-23_103351_repair/install-results.md
.ralph/runs/2026-07-23_103351_repair/lint-results.md
.ralph/runs/2026-07-23_103351_repair/orchestrator-ownership-check.md
.ralph/runs/2026-07-23_103351_repair/preflight-results.md
.ralph/runs/2026-07-23_103351_repair/prompt.md
.ralph/runs/2026-07-23_103351_repair/protected-paths-check.md
.ralph/runs/2026-07-23_103351_repair/ralph-artifact-validation.md
.ralph/runs/2026-07-23_103351_repair/review-packet.md
.ralph/runs/2026-07-23_103351_repair/risk-assessment.md
.ralph/runs/2026-07-23_103351_repair/slice-queue-lint.md
.ralph/runs/2026-07-23_103351_repair/slice-status-transition-check.md
.ralph/runs/2026-07-23_103351_repair/test-results.md
.ralph/runs/2026-07-23_103351_repair/typecheck-results.md
.ralph/runs/2026-07-23_103351_repair/validated-commit-candidate.sha256
.ralph/runs/2026-07-23_104026_repair/agent-declared-result-check.md
.ralph/runs/2026-07-23_104026_repair/artifact-quality-check.md
.ralph/runs/2026-07-23_104026_repair/candidate-fast-check-results.md
.ralph/runs/2026-07-23_104026_repair/changed-files.txt
.ralph/runs/2026-07-23_104026_repair/codex-settings.md
.ralph/runs/2026-07-23_104026_repair/diff-limits-results.md
.ralph/runs/2026-07-23_104026_repair/evidence/browser-acceptance.md
.ralph/runs/2026-07-23_104026_repair/evidence/terminal-logs/browser-infrastructure-probe.log
.ralph/runs/2026-07-23_104026_repair/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-23_104026_repair/evidence/terminal-logs/frontend-final-gates.log
.ralph/runs/2026-07-23_104026_repair/evidence/terminal-logs/frontend-green-pan-label.log
.ralph/runs/2026-07-23_104026_repair/evidence/terminal-logs/frontend-impacted-tests.log
.ralph/runs/2026-07-23_104026_repair/evidence/terminal-logs/frontend-red-pan-label.log
.ralph/runs/2026-07-23_104026_repair/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-23_104026_repair/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-23_104026_repair/evidence/terminal-logs/trusted-browser-after-fix-1.log
.ralph/runs/2026-07-23_104026_repair/evidence/terminal-logs/trusted-browser-after-fix-2.log
.ralph/runs/2026-07-23_104026_repair/evidence/terminal-logs/trusted-browser-red.log
.ralph/runs/2026-07-23_104026_repair/execution-plan.md
.ralph/runs/2026-07-23_104026_repair/final-summary.md
.ralph/runs/2026-07-23_104026_repair/orchestrator-ownership-check.md
.ralph/runs/2026-07-23_104026_repair/preflight-results.md
.ralph/runs/2026-07-23_104026_repair/prompt.md
.ralph/runs/2026-07-23_104026_repair/protected-paths-check.md
.ralph/runs/2026-07-23_104026_repair/ralph-artifact-validation.md
.ralph/runs/2026-07-23_104026_repair/review-packet.md
.ralph/runs/2026-07-23_104026_repair/risk-assessment.md
.ralph/runs/2026-07-23_104026_repair/slice-queue-lint.md
.ralph/runs/2026-07-23_104026_repair/slice-status-transition-check.md
docs/working/API_CONTRACTS.md
docs/working/ASSUMPTIONS.md
docs/working/PROTOTYPE_GAP_REPORT.md
docs/working/PROTOTYPE_INVENTORY.md
sfpcl-lms/e2e/portal-kyc-correction.e2e.spec.ts
sfpcl-lms/src/pages/borrower/portal/MP04_MyProfile.tsx
sfpcl-lms/src/pages/borrower/portal/PortalMemberViews.test.tsx
sfpcl-lms/src/services/portalApi.test.ts
sfpcl-lms/src/services/portalApi.ts
sfpcl_credit/config/urls.py
sfpcl_credit/members/migrations/0016_kyc_correction_request.py
sfpcl_credit/members/models.py
sfpcl_credit/members/modules/kyc_correction_requests.py
sfpcl_credit/members/portal_views.py
sfpcl_credit/tests/test_portal_kyc_correction_api.py
```
