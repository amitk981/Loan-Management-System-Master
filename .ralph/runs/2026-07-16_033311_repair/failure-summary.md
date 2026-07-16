# Failure Summary

- Run: 2026-07-16_033311_repair
- Mode: repair
- Slice: 008M2-documentation-workspace-contract-and-visual-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
e2e-results.md:- FAIL: slice-specific trusted browser contract is missing or invalid.
e2e-results.md:- FAIL: first trusted slice-specific browser run did not pass.
e2e-results.md:- FAIL: second trusted slice-specific browser run did not pass.
e2e-results.md:- FAIL: one or more declared browser screenshots are missing or empty.
```

## Last 50 lines: e2e-results.md

```
# e2e Results

- FAIL: slice-specific trusted browser contract is missing or invalid.
- PASS: README E2E command resolves the shared venv through Git's common directory.
- PASS: Playwright pins the dashboard baseline timezone to Asia/Kolkata.
- FAIL: first trusted slice-specific browser run did not pass.
- FAIL: second trusted slice-specific browser run did not pass.
- FAIL: one or more declared browser screenshots are missing or empty.

Declared specs:
- e2e/staff-documentation-workspace.e2e.spec.ts
Declared screenshots:
- documentation-checklist-blockers.png
- documentation-security-workflow.png
- documentation-restricted-state.png
- documentation-final-approval.png
```

## Changed files (git status)

```
.ralph/progress.md
.ralph/state.json
docs/slices/008M2-documentation-workspace-contract-and-visual-closure.md
docs/working/API_CONTRACTS.md
docs/working/HANDOFF.md
docs/working/PROTOTYPE_INVENTORY.md
sfpcl-lms/src/components/loan/DocumentChecklist.tsx
sfpcl-lms/src/components/loan/DocumentPackModal.tsx
sfpcl-lms/src/pages/documentation/DocumentationHub.test.tsx
sfpcl-lms/src/pages/documentation/DocumentationHub.tsx
sfpcl-lms/src/services/documentationWorkspaceApi.ts
sfpcl_credit/config/urls.py
sfpcl_credit/legal_documents/modules/document_generation.py
sfpcl_credit/legal_documents/views.py
sfpcl_credit/processes/staff_documentation_workspace.py
sfpcl_credit/tests/test_final_documentation_approval_api.py
.ralph/runs/2026-07-16_033311_repair/
sfpcl-lms/e2e/staff-documentation-workspace.e2e.spec.ts
```
