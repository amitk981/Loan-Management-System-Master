# Failure Summary

- Run: 2026-07-24_103525_normal_run
- Mode: normal_run
- Slice: 012E-operational-dashboard-hardening
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
e2e-results.md:- FAIL: first trusted slice-specific browser run did not pass.
e2e-results.md:- FAIL: first run screenshot evidence or manifest is incomplete.
e2e-results.md:- FAIL: second run screenshot evidence or manifest is incomplete.
```

## Last 50 lines: e2e-results.md

```
# e2e Results

- PASS: slice-specific trusted browser contract is valid.
- PASS: README E2E command resolves the shared venv through Git's common directory.
- PASS: Playwright pins the dashboard baseline timezone to Asia/Kolkata.
- FAIL: first trusted slice-specific browser run did not pass.
- SKIP: second trusted slice-specific browser run deferred because the first run failed.
- FAIL: first run screenshot evidence or manifest is incomplete.
- FAIL: second run screenshot evidence or manifest is incomplete.

Declared specs:
- e2e/operational-dashboard.e2e.spec.ts
Declared screenshots:
- operational-dashboard-populated.png
- operational-dashboard-empty.png
- operational-dashboard-error.png
- operational-dashboard-forbidden.png
```

## Changed files (git status)

```
.ralph/runs/2026-07-24_103525_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-24_103525_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-24_103525_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-24_103525_normal_run/changed-files.txt
.ralph/runs/2026-07-24_103525_normal_run/codex-settings.md
.ralph/runs/2026-07-24_103525_normal_run/diff-limits-results.md
.ralph/runs/2026-07-24_103525_normal_run/evidence/dashboard-performance.md
.ralph/runs/2026-07-24_103525_normal_run/evidence/role-card-reconciliation.md
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/backend-check-final.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/backend-check.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/backend-focused-dashboard.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/backend-focused-final.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/backend-green-canonical-scope-budget.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/backend-green-dedicated-route.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/backend-green-pending-completeness.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/backend-green-query-budget.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/backend-migrations-check.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/backend-migrations-final.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/backend-red-canonical-scope-budget.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/backend-red-dedicated-route.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/backend-red-pending-completeness.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/backend-red-query-budget.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/browser-infrastructure-probe.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/browser-operational-dashboard.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/frontend-build-final.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/frontend-build.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/frontend-focused-dashboard.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/frontend-focused-final.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/frontend-green-dashboard-refresh-navigation.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/frontend-lint-final.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/frontend-lint.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/frontend-red-dashboard-refresh-navigation.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/frontend-red-invalid-count.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/frontend-typecheck-final.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/frontend-typecheck.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-24_103525_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-24_103525_normal_run/execution-plan.md
.ralph/runs/2026-07-24_103525_normal_run/final-summary.md
.ralph/runs/2026-07-24_103525_normal_run/no-op-check-results.md
.ralph/runs/2026-07-24_103525_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-24_103525_normal_run/preflight-results.md
.ralph/runs/2026-07-24_103525_normal_run/prompt.md
.ralph/runs/2026-07-24_103525_normal_run/protected-paths-check.md
.ralph/runs/2026-07-24_103525_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-24_103525_normal_run/review-packet.md
.ralph/runs/2026-07-24_103525_normal_run/risk-assessment.md
.ralph/runs/2026-07-24_103525_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-24_103525_normal_run/slice-status-transition-check.md
docs/working/API_CONTRACTS.md
sfpcl-lms/e2e/operational-dashboard.e2e.spec.ts
sfpcl-lms/src/pages/Dashboard.test.tsx
sfpcl-lms/src/pages/Dashboard.tsx
sfpcl-lms/src/pages/applications/ApplicationList.test.tsx
sfpcl-lms/src/pages/applications/ApplicationList.tsx
sfpcl-lms/src/services/applicationIntakeApi.ts
sfpcl-lms/src/services/dashboardApi.ts
sfpcl_credit/closure/modules/loan_closure.py
sfpcl_credit/config/urls.py
sfpcl_credit/dashboard/services.py
sfpcl_credit/dashboard/views.py
sfpcl_credit/tests/test_dashboard_api.py
```
