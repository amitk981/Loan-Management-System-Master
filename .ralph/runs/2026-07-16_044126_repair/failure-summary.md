# Failure Summary

- Run: 2026-07-16_044126_repair
- Mode: repair
- Slice: 008M2-documentation-workspace-contract-and-visual-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
diff-limits-results.md:- FAIL: changed-line count exceeds limits.max_lines_changed.
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
.ralph/runs/2026-07-16_042513_repair/
.ralph/runs/2026-07-16_044126_repair/
sfpcl-lms/e2e/staff-documentation-workspace.e2e.spec.ts
sfpcl_credit/e2e-document-storage/
```
