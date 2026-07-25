# Failure Summary

- Run: 2026-07-25_065407_normal_run
- Mode: normal_run
- Slice: 012DAC-audit-explorer-and-observation-frontend-wiring
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
- e2e/reports-exports-audit-explorer.e2e.spec.ts
Declared screenshots:
- audit-explorer.png
- audit-observation-recorded.png
```

## Authoritative validator diagnostics

These bounded excerpts come from orchestrator-owned trusted validation logs.
They take precedence over agent-authored review packets or evidence narratives.

```
Authoritative source: evidence/terminal-logs/trusted-browser-acceptance-1.log
  1) [chromium] › reports-exports-audit-explorer.e2e.spec.ts:179:5 › S74 audit explorer preserves backend scope, filters, pagination, and restricted-field protection 

    Error: locator.fill: Error: strict mode violation: getByLabel('Action') resolved to 2 elements:
        1) <input value="" aria-label="Action" class="field-input text-sm"/> aka getByLabel('Action', { exact: true })
        2) <input checked id="_r_1_" type="checkbox" class="styles-module__checkboxInput___ECzzO"/> aka getByLabel('Block page interactions')

    Call log:
      - waiting for getByLabel('Action')


      224 |
      225 |   await page.getByLabel('Entity type').fill('compliance_evidence');

Duration milliseconds: 73211
Exit code: 1
Screenshot evidence exit code: 1
Screenshot manifest: /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-25_065407_normal_run/.ralph/runs/2026-07-25_065407_normal_run/evidence/trusted-browser-screenshots-1.sha256
```

## Changed files (git status)

```
.ralph/runs/2026-07-25_065407_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-25_065407_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-25_065407_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-25_065407_normal_run/changed-files.txt
.ralph/runs/2026-07-25_065407_normal_run/codex-settings.md
.ralph/runs/2026-07-25_065407_normal_run/diff-limits-results.md
.ralph/runs/2026-07-25_065407_normal_run/evidence/browser-acceptance.md
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/audit-api-green.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/audit-api-red.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/audit-explorer-page-green.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/audit-explorer-page-red.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/audit-focused-green.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/audit-page-intermediate.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/audit-readonly-green.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/audit-readonly-red-behavior.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/audit-readonly-red.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/audit-state-permission-green.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/backend-audit-regressions.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/backend-check.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/backend-migrations.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/browser-contract-list.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/browser-infrastructure-probe.log
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/browser-run-1.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/build.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/frontend-tests.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/lint.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/observation-api-green.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/observation-api-red.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/observation-page-green.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/observation-page-red.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/post-review-focused-tests.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/typecheck-intermediate.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/typecheck.txt
.ralph/runs/2026-07-25_065407_normal_run/evidence/test-summary.md
.ralph/runs/2026-07-25_065407_normal_run/execution-plan.md
.ralph/runs/2026-07-25_065407_normal_run/final-summary.md
.ralph/runs/2026-07-25_065407_normal_run/no-op-check-results.md
.ralph/runs/2026-07-25_065407_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-25_065407_normal_run/preflight-results.md
.ralph/runs/2026-07-25_065407_normal_run/prompt.md
.ralph/runs/2026-07-25_065407_normal_run/protected-paths-check.md
.ralph/runs/2026-07-25_065407_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-25_065407_normal_run/review-packet.md
.ralph/runs/2026-07-25_065407_normal_run/risk-assessment.md
.ralph/runs/2026-07-25_065407_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-25_065407_normal_run/slice-status-transition-check.md
docs/working/PROTOTYPE_GAP_REPORT.md
docs/working/PROTOTYPE_INVENTORY.md
sfpcl-lms/e2e/reports-exports-audit-explorer.e2e.spec.ts
sfpcl-lms/src/App.tsx
sfpcl-lms/src/pages/compliance/AuditArchiveHub.test.tsx
sfpcl-lms/src/pages/compliance/AuditArchiveHub.tsx
sfpcl-lms/src/services/auditExplorerApi.test.ts
sfpcl-lms/src/services/auditExplorerApi.ts
```
