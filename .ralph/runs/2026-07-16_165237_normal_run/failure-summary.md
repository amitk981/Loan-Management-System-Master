# Failure Summary

- Run: 2026-07-16_165237_normal_run
- Mode: normal_run
- Slice: 008M5-documentation-durable-actions-and-blocker-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
e2e-results.md:- FAIL: first trusted slice-specific browser run did not pass.
e2e-results.md:- FAIL: one or more declared browser screenshots are missing or empty.
```

## Last 50 lines: e2e-results.md

```
# e2e Results

- PASS: slice-specific trusted browser contract is valid.
- PASS: README E2E command resolves the shared venv through Git's common directory.
- PASS: Playwright pins the dashboard baseline timezone to Asia/Kolkata.
- FAIL: first trusted slice-specific browser run did not pass.
- SKIP: second trusted slice-specific browser run deferred because the first run failed.
- FAIL: one or more declared browser screenshots are missing or empty.

Declared specs:
- e2e/staff-documentation-workspace.e2e.spec.ts
Declared screenshots:
- documentation-checklist-blockers.png
- documentation-security-workflow.png
- documentation-restricted-state.png
- documentation-final-approval.png
- documentation-checklist-narrow.png
```

## Changed files (git status)

```
.ralph/progress.md
.ralph/state.json
docs/slices/008M5-documentation-durable-actions-and-blocker-closure.md
docs/working/API_CONTRACTS.md
docs/working/HANDOFF.md
docs/working/digests/epic-008-documentation-security-package.md
sfpcl-lms/e2e/staff-documentation-workspace.e2e.spec.ts
sfpcl-lms/package-lock.json
sfpcl-lms/src/pages/documentation/DocumentationHub.test.tsx
sfpcl-lms/src/pages/documentation/DocumentationHub.tsx
sfpcl-lms/src/services/documentationWorkspaceApi.ts
sfpcl_credit/legal_documents/models.py
sfpcl_credit/legal_documents/modules/checklist_actions.py
sfpcl_credit/legal_documents/modules/staff_workspace_actions.py
sfpcl_credit/processes/staff_documentation_workspace.py
sfpcl_credit/security_instruments/modules/staff_workspace_actions.py
sfpcl_credit/tests/test_final_documentation_approval_api.py
.ralph/runs/2026-07-16_165237_normal_run/
sfpcl_credit/legal_documents/migrations/0014_staff_documentation_durable_actions.py
sfpcl_credit/legal_documents/modules/documentation_actions.py
```
