# Failure Summary

- Run: 2026-07-16_004952_repair
- Mode: repair
- Slice: 008M-documentation-hub-frontend-wiring
- Failed checks: 2

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
agent-declared-result-check.md:- FAIL: the agent's review-packet.md declares this run failed or unmergeable (Result: Fail — unmergeable due to Ralph diff-limit stop.).
diff-limits-results.md:- FAIL: changed-line count exceeds limits.max_lines_changed.
review-packet.md:Fail — unmergeable due to Ralph diff-limit stop.
```

## Last 50 lines: review-packet.md

```
# Review Packet: 2026-07-16_004952_repair

## Result
Fail — unmergeable due to Ralph diff-limit stop.

## Corrected Review Findings
- One locked/redacted workspace replaces the three-response client composition.
- Latest-current server download actions replace synthesized document-file routes.
- API errors and conflicts remain visible; accepted writes refetch once with no optimistic status.
- All six security workflows, exact approval turn, generation, verification, restricted state, and
  terminal status beside Download have behavioral assertions.
- All four slice-owned documentation files are free of `data/mockData` dependencies.

## Evidence
Focused backend 5/5 and frontend 6/6 tests pass; frontend typecheck passes. RED logs capture the
missing workspace endpoint and old-DTO UI failure. Browser discovery returned no available backend,
so no screenshot was fabricated.

## Blocking Finding
Exact validator arithmetic is 2,084 changed lines outside `.ralph/` against a 2,000-line limit.
The runbook requires stopping on exceeded diff limits. Full gates and success/state/slice transitions
were not performed, and this work must not be committed.

## Recommended Next Action
Re-scope the atomic backend projection into an owner-approved prerequisite/corrective slice or raise
the slice diff budget through the protected owner workflow, then rerun this quarantined repair and
full independent validation.
```

## Changed files (git status)

```
docs/slices/009B-sap-customer-code-confirmation-and-reuse.md
docs/working/API_CONTRACTS.md
docs/working/PROTOTYPE_GAP_REPORT.md
docs/working/PROTOTYPE_INVENTORY.md
docs/working/digests/epic-008-documentation-security-package.md
sfpcl-lms/src/components/loan/AuditTimeline.tsx
sfpcl-lms/src/components/loan/DocumentChecklist.tsx
sfpcl-lms/src/components/loan/DocumentPackModal.tsx
sfpcl-lms/src/pages/documentation/DocumentationHub.tsx
sfpcl_credit/config/urls.py
sfpcl_credit/legal_documents/modules/checklist_actions.py
sfpcl_credit/legal_documents/views.py
sfpcl_credit/tests/test_final_documentation_approval_api.py
.ralph/runs/2026-07-16_000538_normal_run/
.ralph/runs/2026-07-16_004952_repair/
sfpcl-lms/src/pages/documentation/DocumentationHub.test.tsx
sfpcl-lms/src/services/documentationWorkspaceApi.ts
sfpcl_credit/processes/staff_documentation_workspace.py
```
