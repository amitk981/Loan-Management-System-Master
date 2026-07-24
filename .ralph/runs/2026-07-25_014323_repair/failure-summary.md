# Failure Summary

- Run: 2026-07-25_014323_repair
- Mode: repair
- Slice: 011PC-closure-frontend-wiring
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
- e2e/default-closure-compliance-staff.e2e.spec.ts
Declared screenshots:
- closure-readiness-blockers.png
```

## Changed files (git status)

```
.ralph/runs/2026-07-25_003342_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-25_003342_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-25_003342_normal_run/backend-check-results.md
.ralph/runs/2026-07-25_003342_normal_run/backend-coverage-results.md
.ralph/runs/2026-07-25_003342_normal_run/backend-impacted-results.md
.ralph/runs/2026-07-25_003342_normal_run/backend-migrations-results.md
.ralph/runs/2026-07-25_003342_normal_run/backend-test-results.md
.ralph/runs/2026-07-25_003342_normal_run/backend-validation-lane-results.md
.ralph/runs/2026-07-25_003342_normal_run/build-results.md
.ralph/runs/2026-07-25_003342_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-25_003342_normal_run/candidate-hash-results.md
.ralph/runs/2026-07-25_003342_normal_run/changed-files.txt
.ralph/runs/2026-07-25_003342_normal_run/codex-settings.md
.ralph/runs/2026-07-25_003342_normal_run/diff-limits-results.md
.ralph/runs/2026-07-25_003342_normal_run/e2e-results.md
.ralph/runs/2026-07-25_003342_normal_run/evidence/browser-acceptance.md
.ralph/runs/2026-07-25_003342_normal_run/evidence/closure-contract-matrix.md
.ralph/runs/2026-07-25_003342_normal_run/evidence/screenshots/run-1/recovery-approval-decision.png
.ralph/runs/2026-07-25_003342_normal_run/evidence/terminal-logs/browser-infrastructure-probe.log
.ralph/runs/2026-07-25_003342_normal_run/evidence/terminal-logs/closure-browser-run-1-retry.log
.ralph/runs/2026-07-25_003342_normal_run/evidence/terminal-logs/closure-browser-run-1.log
.ralph/runs/2026-07-25_003342_normal_run/evidence/terminal-logs/closure-frontend-green-attempt-1.log
.ralph/runs/2026-07-25_003342_normal_run/evidence/terminal-logs/closure-frontend-green.log
.ralph/runs/2026-07-25_003342_normal_run/evidence/terminal-logs/closure-frontend-red.log
.ralph/runs/2026-07-25_003342_normal_run/evidence/terminal-logs/closure-frontend-review-green-final.log
.ralph/runs/2026-07-25_003342_normal_run/evidence/terminal-logs/closure-frontend-review-green.log
.ralph/runs/2026-07-25_003342_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-25_003342_normal_run/evidence/terminal-logs/epic-011-reverse-consumers-final.log
.ralph/runs/2026-07-25_003342_normal_run/evidence/terminal-logs/epic-011-reverse-consumers.log
.ralph/runs/2026-07-25_003342_normal_run/evidence/terminal-logs/final-candidate-checks.log
.ralph/runs/2026-07-25_003342_normal_run/evidence/terminal-logs/frontend-build-final.log
.ralph/runs/2026-07-25_003342_normal_run/evidence/terminal-logs/frontend-build.log
.ralph/runs/2026-07-25_003342_normal_run/evidence/terminal-logs/frontend-lint-final.log
.ralph/runs/2026-07-25_003342_normal_run/evidence/terminal-logs/frontend-lint.log
.ralph/runs/2026-07-25_003342_normal_run/evidence/terminal-logs/frontend-test-full-final.log
.ralph/runs/2026-07-25_003342_normal_run/evidence/terminal-logs/frontend-test-full.log
.ralph/runs/2026-07-25_003342_normal_run/evidence/terminal-logs/frontend-typecheck-final.log
.ralph/runs/2026-07-25_003342_normal_run/evidence/terminal-logs/frontend-typecheck.log
.ralph/runs/2026-07-25_003342_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-25_003342_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-25_003342_normal_run/evidence/terminal-logs/trusted-browser-acceptance-1.log
.ralph/runs/2026-07-25_003342_normal_run/execution-plan.md
.ralph/runs/2026-07-25_003342_normal_run/failure-summary.md
.ralph/runs/2026-07-25_003342_normal_run/final-summary.md
.ralph/runs/2026-07-25_003342_normal_run/install-results.md
.ralph/runs/2026-07-25_003342_normal_run/lint-results.md
.ralph/runs/2026-07-25_003342_normal_run/no-op-check-results.md
.ralph/runs/2026-07-25_003342_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-25_003342_normal_run/preflight-results.md
.ralph/runs/2026-07-25_003342_normal_run/prompt.md
.ralph/runs/2026-07-25_003342_normal_run/protected-paths-check.md
.ralph/runs/2026-07-25_003342_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-25_003342_normal_run/review-packet.md
.ralph/runs/2026-07-25_003342_normal_run/risk-assessment.md
.ralph/runs/2026-07-25_003342_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-25_003342_normal_run/slice-status-transition-check.md
.ralph/runs/2026-07-25_003342_normal_run/test-results.md
.ralph/runs/2026-07-25_003342_normal_run/typecheck-results.md
.ralph/runs/2026-07-25_003342_normal_run/validated-commit-candidate.sha256
.ralph/runs/2026-07-25_010637_repair/agent-declared-result-check.md
.ralph/runs/2026-07-25_010637_repair/artifact-quality-check.md
.ralph/runs/2026-07-25_010637_repair/backend-check-results.md
.ralph/runs/2026-07-25_010637_repair/backend-coverage-results.md
.ralph/runs/2026-07-25_010637_repair/backend-impacted-results.md
.ralph/runs/2026-07-25_010637_repair/backend-migrations-results.md
.ralph/runs/2026-07-25_010637_repair/backend-test-results.md
.ralph/runs/2026-07-25_010637_repair/backend-validation-lane-results.md
.ralph/runs/2026-07-25_010637_repair/build-results.md
.ralph/runs/2026-07-25_010637_repair/candidate-fast-check-results.md
.ralph/runs/2026-07-25_010637_repair/candidate-hash-results.md
.ralph/runs/2026-07-25_010637_repair/changed-files.txt
.ralph/runs/2026-07-25_010637_repair/codex-settings.md
.ralph/runs/2026-07-25_010637_repair/diff-limits-results.md
.ralph/runs/2026-07-25_010637_repair/e2e-results.md
.ralph/runs/2026-07-25_010637_repair/evidence/browser-repair-diagnosis.md
.ralph/runs/2026-07-25_010637_repair/evidence/screenshots/run-1/recovery-approval-decision.png
.ralph/runs/2026-07-25_010637_repair/evidence/terminal-logs/agent-browser-diagnosis.log
.ralph/runs/2026-07-25_010637_repair/evidence/terminal-logs/browser-infrastructure-probe.log
.ralph/runs/2026-07-25_010637_repair/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-25_010637_repair/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-25_010637_repair/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-25_010637_repair/evidence/terminal-logs/trusted-browser-acceptance-1.log
.ralph/runs/2026-07-25_010637_repair/execution-plan.md
.ralph/runs/2026-07-25_010637_repair/failure-summary.md
.ralph/runs/2026-07-25_010637_repair/final-summary.md
.ralph/runs/2026-07-25_010637_repair/install-results.md
.ralph/runs/2026-07-25_010637_repair/lint-results.md
.ralph/runs/2026-07-25_010637_repair/orchestrator-ownership-check.md
.ralph/runs/2026-07-25_010637_repair/preflight-results.md
.ralph/runs/2026-07-25_010637_repair/prompt.md
.ralph/runs/2026-07-25_010637_repair/protected-paths-check.md
.ralph/runs/2026-07-25_010637_repair/ralph-artifact-validation.md
.ralph/runs/2026-07-25_010637_repair/review-packet.md
.ralph/runs/2026-07-25_010637_repair/risk-assessment.md
.ralph/runs/2026-07-25_010637_repair/slice-queue-lint.md
.ralph/runs/2026-07-25_010637_repair/slice-status-transition-check.md
.ralph/runs/2026-07-25_010637_repair/test-results.md
.ralph/runs/2026-07-25_010637_repair/typecheck-results.md
.ralph/runs/2026-07-25_010637_repair/validated-commit-candidate.sha256
.ralph/runs/2026-07-25_014243_repair/agent-declared-result-check.md
.ralph/runs/2026-07-25_014243_repair/artifact-quality-check.md
.ralph/runs/2026-07-25_014243_repair/candidate-fast-check-results.md
.ralph/runs/2026-07-25_014243_repair/changed-files.txt
.ralph/runs/2026-07-25_014243_repair/claude-settings.md
.ralph/runs/2026-07-25_014243_repair/diff-limits-results.md
.ralph/runs/2026-07-25_014243_repair/evidence/terminal-logs/browser-infrastructure-probe.log
.ralph/runs/2026-07-25_014243_repair/evidence/terminal-logs/claude-summary.md
.ralph/runs/2026-07-25_014243_repair/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-25_014243_repair/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-25_014243_repair/execution-plan.md
.ralph/runs/2026-07-25_014243_repair/failure-summary.md
.ralph/runs/2026-07-25_014243_repair/final-summary.md
.ralph/runs/2026-07-25_014243_repair/orchestrator-ownership-check.md
.ralph/runs/2026-07-25_014243_repair/preflight-results.md
.ralph/runs/2026-07-25_014243_repair/prompt.md
.ralph/runs/2026-07-25_014243_repair/protected-paths-check.md
.ralph/runs/2026-07-25_014243_repair/ralph-artifact-validation.md
.ralph/runs/2026-07-25_014243_repair/review-packet.md
.ralph/runs/2026-07-25_014243_repair/risk-assessment.md
.ralph/runs/2026-07-25_014243_repair/slice-queue-lint.md
.ralph/runs/2026-07-25_014243_repair/slice-status-transition-check.md
.ralph/runs/2026-07-25_014323_repair/agent-declared-result-check.md
.ralph/runs/2026-07-25_014323_repair/artifact-quality-check.md
.ralph/runs/2026-07-25_014323_repair/candidate-fast-check-results.md
.ralph/runs/2026-07-25_014323_repair/changed-files.txt
.ralph/runs/2026-07-25_014323_repair/codex-settings.md
.ralph/runs/2026-07-25_014323_repair/diff-limits-results.md
.ralph/runs/2026-07-25_014323_repair/evidence/terminal-logs/artifact-quality-green.log
.ralph/runs/2026-07-25_014323_repair/evidence/terminal-logs/browser-infrastructure-probe.log
.ralph/runs/2026-07-25_014323_repair/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-25_014323_repair/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-25_014323_repair/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-25_014323_repair/execution-plan.md
.ralph/runs/2026-07-25_014323_repair/final-summary.md
.ralph/runs/2026-07-25_014323_repair/orchestrator-ownership-check.md
.ralph/runs/2026-07-25_014323_repair/preflight-results.md
.ralph/runs/2026-07-25_014323_repair/prompt.md
.ralph/runs/2026-07-25_014323_repair/protected-paths-check.md
.ralph/runs/2026-07-25_014323_repair/ralph-artifact-validation.md
.ralph/runs/2026-07-25_014323_repair/review-packet.md
.ralph/runs/2026-07-25_014323_repair/risk-assessment.md
.ralph/runs/2026-07-25_014323_repair/slice-queue-lint.md
.ralph/runs/2026-07-25_014323_repair/slice-status-transition-check.md
docs/working/ASSUMPTIONS.md
sfpcl-lms/e2e/default-closure-compliance-staff.e2e.spec.ts
sfpcl-lms/src/pages/closure/LoanClosureHub.test.tsx
sfpcl-lms/src/pages/closure/LoanClosureHub.tsx
sfpcl-lms/src/services/authSession.ts
sfpcl-lms/src/services/recoveryApi.test.ts
sfpcl-lms/src/services/recoveryApi.ts
```
