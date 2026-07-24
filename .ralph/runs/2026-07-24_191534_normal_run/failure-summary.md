# Failure Summary

- Run: 2026-07-24_191534_normal_run
- Mode: normal_run
- Slice: 012F2-performance-readiness-evidence
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
- e2e/performance-readiness.e2e.spec.ts
Declared screenshots:
- performance-readiness-dashboard.png
```

## Changed files (git status)

```
.ralph/runs/2026-07-24_191534_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-24_191534_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-24_191534_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-24_191534_normal_run/changed-files.txt
.ralph/runs/2026-07-24_191534_normal_run/codex-settings.md
.ralph/runs/2026-07-24_191534_normal_run/diff-limits-results.md
.ralph/runs/2026-07-24_191534_normal_run/evidence/bounded-local-environment.json
.ralph/runs/2026-07-24_191534_normal_run/evidence/bounded-local-results.json
.ralph/runs/2026-07-24_191534_normal_run/evidence/controlled-performance-failure.json
.ralph/runs/2026-07-24_191534_normal_run/evidence/exact-commands.md
.ralph/runs/2026-07-24_191534_normal_run/evidence/performance-evidence-hashes.sha256
.ralph/runs/2026-07-24_191534_normal_run/evidence/performance-readiness-summary.json
.ralph/runs/2026-07-24_191534_normal_run/evidence/performance-scenario-matrix.json
.ralph/runs/2026-07-24_191534_normal_run/evidence/terminal-logs/backend-check.log
.ralph/runs/2026-07-24_191534_normal_run/evidence/terminal-logs/backend-migrations.log
.ralph/runs/2026-07-24_191534_normal_run/evidence/terminal-logs/browser-infrastructure-probe.log
.ralph/runs/2026-07-24_191534_normal_run/evidence/terminal-logs/browser-performance-readiness.log
.ralph/runs/2026-07-24_191534_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-24_191534_normal_run/evidence/terminal-logs/focused-backend.log
.ralph/runs/2026-07-24_191534_normal_run/evidence/terminal-logs/frontend-build.log
.ralph/runs/2026-07-24_191534_normal_run/evidence/terminal-logs/frontend-lint.log
.ralph/runs/2026-07-24_191534_normal_run/evidence/terminal-logs/frontend-tests.log
.ralph/runs/2026-07-24_191534_normal_run/evidence/terminal-logs/frontend-typecheck.log
.ralph/runs/2026-07-24_191534_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-24_191534_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-24_191534_normal_run/evidence/terminal-logs/performance-lane.log
.ralph/runs/2026-07-24_191534_normal_run/evidence/terminal-logs/tdd-green-command.log
.ralph/runs/2026-07-24_191534_normal_run/evidence/terminal-logs/tdd-green-local-runner.log
.ralph/runs/2026-07-24_191534_normal_run/evidence/terminal-logs/tdd-green-matrix.log
.ralph/runs/2026-07-24_191534_normal_run/evidence/terminal-logs/tdd-green-summary.log
.ralph/runs/2026-07-24_191534_normal_run/evidence/terminal-logs/tdd-red.log
.ralph/runs/2026-07-24_191534_normal_run/execution-plan.md
.ralph/runs/2026-07-24_191534_normal_run/final-summary.md
.ralph/runs/2026-07-24_191534_normal_run/no-op-check-results.md
.ralph/runs/2026-07-24_191534_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-24_191534_normal_run/preflight-results.md
.ralph/runs/2026-07-24_191534_normal_run/prompt.md
.ralph/runs/2026-07-24_191534_normal_run/protected-paths-check.md
.ralph/runs/2026-07-24_191534_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-24_191534_normal_run/review-packet.md
.ralph/runs/2026-07-24_191534_normal_run/risk-assessment.md
.ralph/runs/2026-07-24_191534_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-24_191534_normal_run/slice-status-transition-check.md
docs/working/PERFORMANCE_READINESS.md
sfpcl-lms/e2e/performance-readiness.e2e.spec.ts
sfpcl_credit/performance_readiness/__init__.py
sfpcl_credit/performance_readiness/local.py
sfpcl_credit/performance_readiness/matrix.py
sfpcl_credit/performance_readiness/probes.py
sfpcl_credit/performance_readiness/runner.py
sfpcl_credit/performance_readiness/timed_runner.py
sfpcl_credit/shared/management/commands/performance_readiness.py
sfpcl_credit/tests/test_performance_readiness.py
```
