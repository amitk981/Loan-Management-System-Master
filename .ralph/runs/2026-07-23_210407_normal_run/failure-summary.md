# Failure Summary

- Run: 2026-07-23_210407_normal_run
- Mode: normal_run
- Slice: 011O-auditor-read-only-views
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
- e2e/auditor-read-only-epic-011.e2e.spec.ts
Declared screenshots:
- auditor-epic-011-populated.png
- auditor-epic-011-empty.png
- auditor-epic-011-unauthorised.png
```

## Changed files (git status)

```
.ralph/runs/2026-07-23_210407_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-23_210407_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-23_210407_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-23_210407_normal_run/changed-files.txt
.ralph/runs/2026-07-23_210407_normal_run/codex-settings.md
.ralph/runs/2026-07-23_210407_normal_run/diff-limits-results.md
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-backend-focused.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-empty-green.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-empty-red.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-frontend-green.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-frontend-red.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-mutation-green.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-mutation-red.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-mutation-side-effects-green.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-mutation-side-effects.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-playwright.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-populated-green.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-populated-red.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-scope-green.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/auditor-epic-011-scope-red.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/backend-check.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/backend-impacted-regressions-green.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/backend-impacted-regressions.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/backend-migrations-check.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/browser-infrastructure-probe.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/frontend-build.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/frontend-full-tests.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/frontend-lint.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/frontend-typecheck.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-23_210407_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-23_210407_normal_run/execution-plan.md
.ralph/runs/2026-07-23_210407_normal_run/final-summary.md
.ralph/runs/2026-07-23_210407_normal_run/no-op-check-results.md
.ralph/runs/2026-07-23_210407_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-23_210407_normal_run/preflight-results.md
.ralph/runs/2026-07-23_210407_normal_run/prompt.md
.ralph/runs/2026-07-23_210407_normal_run/protected-paths-check.md
.ralph/runs/2026-07-23_210407_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-23_210407_normal_run/review-packet.md
.ralph/runs/2026-07-23_210407_normal_run/risk-assessment.md
.ralph/runs/2026-07-23_210407_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-23_210407_normal_run/slice-status-transition-check.md
docs/working/API_CONTRACTS.md
docs/working/PROTOTYPE_GAP_REPORT.md
docs/working/PROTOTYPE_INVENTORY.md
sfpcl-lms/e2e/auditor-read-only-epic-011.e2e.spec.ts
sfpcl-lms/src/App.tsx
sfpcl-lms/src/pages/compliance/AuditorEpic011View.test.tsx
sfpcl-lms/src/pages/compliance/AuditorEpic011View.tsx
sfpcl-lms/src/services/auditorApi.ts
sfpcl_credit/approvals/modules/read_scope.py
sfpcl_credit/closure/modules/loan_closure.py
sfpcl_credit/compliance/modules/auditor_epic_011.py
sfpcl_credit/compliance/modules/compliance_control_tracker.py
sfpcl_credit/compliance/modules/grievance_workflow.py
sfpcl_credit/compliance/modules/kyc_review_tracker.py
sfpcl_credit/compliance/modules/nbfc_principal_business_test.py
sfpcl_credit/compliance/modules/section186_tracker.py
sfpcl_credit/compliance/views.py
sfpcl_credit/config/urls.py
sfpcl_credit/defaults/modules/default_workflow.py
sfpcl_credit/identity/catalogue.py
sfpcl_credit/tests/test_auditor_epic_011_api.py
sfpcl_credit/tests/test_default_case_opening_api.py
sfpcl_credit/tests/test_kyc_review_api.py
sfpcl_credit/tests/test_statutory_trackers.py
```
