# Execution Plan

Selected slice: 010O-header-notification-summary-wiring

## Permission check

- Product targets `sfpcl-lms/src/**` and `sfpcl-lms/e2e/**`, plus this run's
  `.ralph/runs/2026-07-22_084434_normal_run/**` evidence, are allowed by
  `.ralph/permissions.json` and writable in the active worktree.
- `docs/source/**` is forbidden by policy even though the worktree filesystem may report it as
  writable; it will remain untouched. No protected, approval-required, state, progress, slice
  status, or mechanical handoff path is an implementation target.

## Slice boundary

Wire only the existing header notification dropdown to the existing notification list and
versioned mark-read contracts. Reuse the current header and Notifications Center patterns, remove
the final `Header.tsx` mock surface, and add the exact trusted-browser spec/screenshots declared by
the slice. No endpoint, permission, notification-generation, global-search, portal, or visual-system
change is planned.

## Behavior-first sequence

1. Inspect the current header, notification service/center, auth/error helpers, test setup, routing,
   and representative Playwright contract specs to identify the existing public seams and styles.
2. RED then GREEN: add a focused header behavior test for a populated bounded unread summary and
   real badge, then minimally connect the dropdown to the existing list service.
3. RED then GREEN one behavior at a time for loading, empty, error, unauthorized, successful
   versioned mark-read, and `409 STALE_WRITE` refresh. Save each focused red/green output under
   `evidence/terminal-logs/`.
4. Add the final mock-removal regression asserting `Header.tsx` has no `mockData` import or inline
   notification fixture, and keep View all routing to the existing Notifications Center.
5. Implement `e2e/header-notifications.e2e.spec.ts` with deterministic API interception for
   populated, empty, and error dropdown states; run the contract twice and save the three exact
   screenshots in this run's evidence folder.
6. Run focused notification/header regressions, then frontend tests, typecheck, lint, and build.
   Run the cheap backend `manage.py check` and migration-sync checks only, using the mandated Ralph
   Python interpreter; the orchestrator owns the authoritative backend lane.
7. Save mock-removal/request-contract proof, test and browser evidence, risk assessment, review
   packet, and final summary. Set the review result exactly to `Ready for independent validation`
   only after all focused work is green.

## Expected files

- `sfpcl-lms/src/components/layout/Header.tsx`
- Focused header/service tests under `sfpcl-lms/src/`
- `sfpcl-lms/e2e/header-notifications.e2e.spec.ts`
- `.ralph/runs/2026-07-22_084434_normal_run/**` evidence only
