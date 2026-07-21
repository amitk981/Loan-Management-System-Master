# Failure Summary

- Run: 2026-07-21_162231_normal_run
- Mode: normal_run
- Slice: 010MB-interest-and-monitoring-frontend-wiring
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
- e2e/servicing-monitoring-workflows.e2e.spec.ts
Declared screenshots:
- interest-management.png
- monitoring-dashboard.png
```

## Changed files (git status)

```
.ralph/runs/2026-07-21_162231_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-21_162231_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-21_162231_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-21_162231_normal_run/changed-files.txt
.ralph/runs/2026-07-21_162231_normal_run/codex-settings.md
.ralph/runs/2026-07-21_162231_normal_run/diff-limits-results.md
.ralph/runs/2026-07-21_162231_normal_run/evidence/terminal-logs/backend-check.log
.ralph/runs/2026-07-21_162231_normal_run/evidence/terminal-logs/backend-final-checks.log
.ralph/runs/2026-07-21_162231_normal_run/evidence/terminal-logs/backend-focused-final.log
.ralph/runs/2026-07-21_162231_normal_run/evidence/terminal-logs/backend-migrations-check.log
.ralph/runs/2026-07-21_162231_normal_run/evidence/terminal-logs/backend-read-projections-green.log
.ralph/runs/2026-07-21_162231_normal_run/evidence/terminal-logs/backend-read-projections-red.log
.ralph/runs/2026-07-21_162231_normal_run/evidence/terminal-logs/browser-infrastructure-probe.log
.ralph/runs/2026-07-21_162231_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-21_162231_normal_run/evidence/terminal-logs/e2e-seed-permissions-red.log
.ralph/runs/2026-07-21_162231_normal_run/evidence/terminal-logs/final-candidate-audit.log
.ralph/runs/2026-07-21_162231_normal_run/evidence/terminal-logs/frontend-build.log
.ralph/runs/2026-07-21_162231_normal_run/evidence/terminal-logs/frontend-final-gates.log
.ralph/runs/2026-07-21_162231_normal_run/evidence/terminal-logs/frontend-focused-final.log
.ralph/runs/2026-07-21_162231_normal_run/evidence/terminal-logs/frontend-lint.log
.ralph/runs/2026-07-21_162231_normal_run/evidence/terminal-logs/frontend-typecheck.log
.ralph/runs/2026-07-21_162231_normal_run/evidence/terminal-logs/mock-policy-auth-audit.log
.ralph/runs/2026-07-21_162231_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-21_162231_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-21_162231_normal_run/evidence/terminal-logs/playwright-collection.log
.ralph/runs/2026-07-21_162231_normal_run/evidence/terminal-logs/servicing-api-green.log
.ralph/runs/2026-07-21_162231_normal_run/evidence/terminal-logs/servicing-api-red.log
.ralph/runs/2026-07-21_162231_normal_run/evidence/terminal-logs/servicing-workspaces-green.log
.ralph/runs/2026-07-21_162231_normal_run/evidence/terminal-logs/servicing-workspaces-red.log
.ralph/runs/2026-07-21_162231_normal_run/execution-plan.md
.ralph/runs/2026-07-21_162231_normal_run/final-summary.md
.ralph/runs/2026-07-21_162231_normal_run/no-op-check-results.md
.ralph/runs/2026-07-21_162231_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-21_162231_normal_run/preflight-results.md
.ralph/runs/2026-07-21_162231_normal_run/prompt.md
.ralph/runs/2026-07-21_162231_normal_run/protected-paths-check.md
.ralph/runs/2026-07-21_162231_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-21_162231_normal_run/review-packet.md
.ralph/runs/2026-07-21_162231_normal_run/risk-assessment.md
.ralph/runs/2026-07-21_162231_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-21_162231_normal_run/slice-status-transition-check.md
docs/working/API_CONTRACTS.md
sfpcl-lms/e2e/servicing-monitoring-workflows.e2e.spec.ts
sfpcl-lms/src/pages/interest/InterestManagement.tsx
sfpcl-lms/src/pages/monitoring/MonitoringDashboard.tsx
sfpcl-lms/src/pages/servicing/InterestMonitoringWorkspaces.test.tsx
sfpcl-lms/src/services/servicingApi.test.ts
sfpcl-lms/src/services/servicingApi.ts
sfpcl_credit/config/urls.py
sfpcl_credit/identity/management/commands/seed_e2e_users.py
sfpcl_credit/monitoring/modules/dpd_monitoring.py
sfpcl_credit/monitoring/modules/reminder_engine.py
sfpcl_credit/monitoring/views.py
sfpcl_credit/tests/test_dpd_monitoring_api.py
sfpcl_credit/tests/test_reminder_queue_api.py
sfpcl_credit/tests/test_seed_e2e_users.py
```
