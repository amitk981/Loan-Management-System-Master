# Failure Summary

- Run: 2026-07-22_173435_normal_run
- Mode: normal_run
- Slice: 011F-recovery-action-execution-shell
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
- e2e/recovery-action-execution.e2e.spec.ts
Declared screenshots:
- recovery-action-blocked.png
- recovery-action-approved.png
```

## Changed files (git status)

```
.ralph/runs/2026-07-22_173435_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-22_173435_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-22_173435_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-22_173435_normal_run/changed-files.txt
.ralph/runs/2026-07-22_173435_normal_run/codex-settings.md
.ralph/runs/2026-07-22_173435_normal_run/diff-limits-results.md
.ralph/runs/2026-07-22_173435_normal_run/evidence/terminal-logs/backend-check.log
.ralph/runs/2026-07-22_173435_normal_run/evidence/terminal-logs/backend-decision-pg-focused.log
.ralph/runs/2026-07-22_173435_normal_run/evidence/terminal-logs/backend-focused-recovery-action.log
.ralph/runs/2026-07-22_173435_normal_run/evidence/terminal-logs/backend-focused-recovery.log
.ralph/runs/2026-07-22_173435_normal_run/evidence/terminal-logs/backend-green-complete-ledger.log
.ralph/runs/2026-07-22_173435_normal_run/evidence/terminal-logs/backend-green-initiate-sh4.log
.ralph/runs/2026-07-22_173435_normal_run/evidence/terminal-logs/backend-migrations-check.log
.ralph/runs/2026-07-22_173435_normal_run/evidence/terminal-logs/backend-red-complete-ledger.log
.ralph/runs/2026-07-22_173435_normal_run/evidence/terminal-logs/backend-red-initiate-sh4.log
.ralph/runs/2026-07-22_173435_normal_run/evidence/terminal-logs/backend-reverse-security-owners.log
.ralph/runs/2026-07-22_173435_normal_run/evidence/terminal-logs/browser-infrastructure-probe.log
.ralph/runs/2026-07-22_173435_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-22_173435_normal_run/evidence/terminal-logs/frontend-build.log
.ralph/runs/2026-07-22_173435_normal_run/evidence/terminal-logs/frontend-final-focused.log
.ralph/runs/2026-07-22_173435_normal_run/evidence/terminal-logs/frontend-final-typecheck.log
.ralph/runs/2026-07-22_173435_normal_run/evidence/terminal-logs/frontend-green-recovery-s57.log
.ralph/runs/2026-07-22_173435_normal_run/evidence/terminal-logs/frontend-lint.log
.ralph/runs/2026-07-22_173435_normal_run/evidence/terminal-logs/frontend-red-recovery-s57.log
.ralph/runs/2026-07-22_173435_normal_run/evidence/terminal-logs/frontend-typecheck.log
.ralph/runs/2026-07-22_173435_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-22_173435_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-22_173435_normal_run/evidence/terminal-logs/trusted-browser-recovery.log
.ralph/runs/2026-07-22_173435_normal_run/execution-plan.md
.ralph/runs/2026-07-22_173435_normal_run/final-summary.md
.ralph/runs/2026-07-22_173435_normal_run/no-op-check-results.md
.ralph/runs/2026-07-22_173435_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-22_173435_normal_run/preflight-results.md
.ralph/runs/2026-07-22_173435_normal_run/prompt.md
.ralph/runs/2026-07-22_173435_normal_run/protected-paths-check.md
.ralph/runs/2026-07-22_173435_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-22_173435_normal_run/review-packet.md
.ralph/runs/2026-07-22_173435_normal_run/risk-assessment.md
.ralph/runs/2026-07-22_173435_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-22_173435_normal_run/slice-status-transition-check.md
docs/working/API_CONTRACTS.md
docs/working/ASSUMPTIONS.md
sfpcl-lms/e2e/recovery-action-execution.e2e.spec.ts
sfpcl-lms/src/pages/defaults/DefaultRecoveryHub.test.tsx
sfpcl-lms/src/pages/defaults/DefaultRecoveryHub.tsx
sfpcl-lms/src/services/recoveryApi.ts
sfpcl_credit/config/urls.py
sfpcl_credit/defaults/modules/default_workflow.py
sfpcl_credit/identity/catalogue.py
sfpcl_credit/legal_documents/modules/recovery_evidence.py
sfpcl_credit/loans/modules/recovery_proceeds.py
sfpcl_credit/recovery/migrations/0002_recovery_action_execution.py
sfpcl_credit/recovery/models.py
sfpcl_credit/recovery/modules/recovery_decision.py
sfpcl_credit/recovery/modules/recovery_workflow.py
sfpcl_credit/recovery/views.py
sfpcl_credit/security_instruments/modules/recovery_invocation.py
sfpcl_credit/tests/test_default_recovery_postgresql_acceptance.py
sfpcl_credit/tests/test_recovery_action_api.py
sfpcl_credit/tests/test_recovery_decision_api.py
```
