# Failure Summary

- Run: 2026-07-14_043916_normal_run
- Mode: normal_run
- Slice: 007P-sanction-queue-pagination-and-read-boundary-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
e2e-results.md:- FAIL: first trusted slice-specific browser run did not pass.
e2e-results.md:- FAIL: second trusted slice-specific browser run did not pass.
```

## Last 50 lines: e2e-results.md

```
# e2e Results

- PASS: slice-specific trusted browser contract is valid.
- PASS: README E2E command resolves the shared venv through Git's common directory.
- PASS: Playwright pins the dashboard baseline timezone to Asia/Kolkata.
- FAIL: first trusted slice-specific browser run did not pass.
- FAIL: second trusted slice-specific browser run did not pass.
- PASS: every declared browser screenshot exists and is non-empty.

Declared specs:
- e2e/sanction-workbench.e2e.spec.ts
Declared screenshots:
- sanction-paginated-filtered-queue.png
```

## Changed files (git status)

```
.ralph/progress.md
.ralph/state.json
docs/slices/007P-sanction-queue-pagination-and-read-boundary-closure.md
docs/slices/007Q-register-source-fields-and-visual-evidence-closure.md
docs/working/API_CONTRACTS.md
docs/working/CONTEXT.md
docs/working/HANDOFF.md
docs/working/digests/epic-007-sanction-approval-workflow.md
sfpcl-lms/e2e/sanction-workbench.e2e.spec.ts
sfpcl-lms/src/pages/sanction/SanctionWorkbench.test.tsx
sfpcl-lms/src/pages/sanction/SanctionWorkbench.tsx
sfpcl-lms/src/services/approvalRegistersApi.test.ts
sfpcl-lms/src/services/authSession.test.ts
sfpcl-lms/src/services/authSession.ts
sfpcl-lms/src/services/sanctionApi.ts
sfpcl_credit/approvals/modules/approval_case_engine.py
sfpcl_credit/tests/test_approval_case_routing_api.py
.ralph/runs/2026-07-14_043916_normal_run/
```
