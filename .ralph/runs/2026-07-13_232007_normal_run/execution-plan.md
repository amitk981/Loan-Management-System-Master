# Execution Plan

Selected slice: `007I-sanction-workbench-ui`

## Public seam and constraints

- Keep the existing Sanction Workbench and Approval Panel composition and styling. Replace only
  labels/data/action authority required by the API-backed workflow.
- Add one frontend approval-case service seam over the authenticated HTTP boundary. The real
  workbench container and its interaction tests will use that same interface.
- Treat each selected case projection as self-contained server truth. Never derive authority,
  checklist facts, amounts, conflict, meeting status, or historical-cycle validity from live
  appraisal/register data.
- Intersect enabled resource `available_actions` with `/auth/me` canonical permissions for
  usability. Never union global actions into resource authority.

## TDD sequence

1. Replace the obsolete not-connected test with one failing container tracer: load the assigned
   queue/detail, render the ten frozen review checks and authority, then approve with the exact
   case URL/body and canonical refresh.
2. Implement the typed approval-case service and minimum workbench/ApprovalPanel wiring to make
   that tracer green; remove both owned mock/client-authority paths.
3. Add one failing interaction at a time for reject/return mandatory reasons and field errors,
   partial/final joint decisions, stale refresh, conflict denial/abstention visibility, denied and
   nondisclosing states, GM gate errors, frozen old/new cycle isolation, and terminal sanction
   decision reads. Make each green before proceeding.
4. Add special-case evidence recording only when the case action plus `/auth/me` permissions make
   it usable, submitting the exact bounded §25.11 payload and three distinct document ids. Keep
   document metadata non-authoritative and do not add register/live-appraisal reads.
5. Update the App shell route to use the real container, add mock-removal regressions, and update
   the prototype inventory/gap ledger.

## Verification and evidence

- Save RED and GREEN focused Vitest output under
  `.ralph/runs/2026-07-13_232007_normal_run/evidence/terminal-logs/`.
- Run focused sanction tests regularly, then frontend typecheck, lint, test, and build.
- Run backend Django check, migration sync, and the full coverage gate with the mandated Ralph
  virtualenv interpreter even though production backend code is unchanged.
- Attempt the existing deterministic Playwright/browser evidence path; retain genuine screenshots
  if Chromium launches, otherwise record the sandbox limitation without fabricating evidence.
- Run the required final review, then write changed-files, risk, review packet, final summary,
  progress/handoff/state, and complete only the selected slice. Sharpen the next one or two
  Not Started slices using already-opened Epic 007 material.
