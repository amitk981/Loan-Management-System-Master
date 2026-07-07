# Execution Plan — 003K Prototype Visual Gap Report Update

## Scope
- Slice: `003K-prototype-visual-gap-report-update`
- Risk: Low
- Implementation type: documentation/prototype inventory update only.

## Required Context Read
- `AGENTS.md`
- `docs/working/TOKEN_RULES.md`
- `docs/working/CONTEXT.md`
- `docs/working/AFK_RUNBOOK.md`
- `.ralph/config.yaml`
- `.ralph/permissions.json`
- `.ralph/state.json`
- `docs/working/HANDOFF.md`
- `docs/working/DECISION_POLICY.md`
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/slices/003K-prototype-visual-gap-report-update.md`
- `docs/epics/003-audit-documents-config-foundation.md`
- `docs/working/digests/epic-003-audit-documents-config.md`
- Narrow source excerpts named by the slice: API contracts sections 26, 39, 41, 42, 43; implementation-roadmap sections 20-22 and 30.2; screen/content notification sections S01/S03/S04 and 5.8.

## Permissions Check
Allowed edit targets from `.ralph/permissions.json`:
- `docs/working/**`
- `docs/slices/**`
- `.ralph/runs/**`
- `.ralph/progress.md`
- `.ralph/state.json`

Protected/forbidden targets to avoid:
- `docs/source/**`
- `scripts/**`
- `.ralph/config.yaml`
- `.ralph/permissions.json`
- `AGENTS.md`
- `CLAUDE.md`
- `.git/**`

## Work Steps
1. Update `docs/working/PROTOTYPE_INVENTORY.md` to distinguish API-backed staff screens from remaining prototype/mock shells:
   - Dashboard via `GET /api/v1/dashboard/`.
   - Notifications Center via `GET /api/v1/notifications/` and mark-read.
   - My Profile via `GET /api/v1/auth/me/`.
   - Task Inbox remains prototype/mock.
   - Scheduler added in 003J is internal metadata only.
2. Update `docs/working/PROTOTYPE_GAP_REPORT.md` with the same status and source-backed caveats.
3. Add a short Epic 003 digest note for the source extracts used by 003K.
4. Run standard gates and save terminal logs under `evidence/terminal-logs/`.
5. Save required Ralph artifacts: `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`.
6. Update slice status, handoff, progress, and state after gates pass.
7. Sharpen next 1-2 Not Started slice files using only source/digest context already opened in this run.

## TDD Applicability
This slice has no backend, business logic, or production frontend behavior change. Per the slice test cases, no new unit tests are required if no code is touched. The run will still execute the full backend/frontend quality gates and record that TDD red/green is not applicable for a docs-only inventory update.
