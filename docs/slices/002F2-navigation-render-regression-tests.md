# Slice 002F2: Navigation Render Regression Tests

## Status
Not Started

## Parent Epic
Epic 002: Platform Auth and Role Shell
Epic file: `docs/epics/002-platform-auth-shell.md`

## Goal
Replace the shallow 002F navigation test gap with behavior-level tests that prove the actual staff shell visibility and route guard stay permission-driven.

## User Value
Future frontend slices can add admin and workflow screens without accidentally exposing restricted navigation to zero-permission, tracer-only, or unknown-role users.

## Depends On
- 002F
- 002FL

## Review Finding
Created by architecture review `2026-07-04_085117_architecture_review`.

## Concrete Requirements
1. Add a tested navigation-visibility path that exercises the same code `Sidebar` uses to decide which staff nav items render. Either render `Sidebar` with the existing `RoleContext` using existing dependencies, or extract a small pure helper consumed by `Sidebar` and test that helper directly.
2. For every non-dashboard staff nav item in `allNavItems`, prove a user without that item's `requiredPermission` does not see that item and cannot navigate to that page.
3. Prove a tracer-only backend session sees only Dashboard and Tracer, not Applications, Members, Loan Accounts, Reports, Settings, Audit, or Admin user management.
4. Prove a zero-permission or unknown-role backend session sees only Dashboard and receives the existing access-blocked Dashboard fallback on direct guarded navigation.
5. Keep `tracer.lifecycle.run -> run_tracer` isolated: it must unlock no non-tracer prototype permission.
6. Do not add a new React testing/rendering dependency for this corrective slice unless it is already pinned before the run; prefer extracting a pure visibility helper consumed by `Sidebar` and covered by vitest.
7. When 002G adds the admin user-management route, its nav item and direct route must join the same contract and be covered by these tests behind `manage_users`.
8. Save actual red/green test logs under `.ralph/runs/<run-id>/evidence/terminal-logs/`; the review packet must not reference paths that are absent from the committed run artifacts.

## Source / Digest References
- `docs/working/digests/epic-002-platform-auth.md` entries for 002E2, 002F, and 002G.
- `docs/slices/002F-role-aware-sidebar-header-navigation.md` requirements 1-5.
- `docs/working/FRONTEND_DESIGN_RULES.md` for no visual redesign.

## Test Cases
- Navigation visibility tests fail if `Sidebar` renders a protected item while `can(requiredPermission)` is false.
- Route guard tests fail if direct navigation to a protected page does not return Dashboard with `blockedPage`.
- Existing `authSession.test.ts` tracer-isolation and neutral-role tests still pass.

## Risk Level
Medium

## Acceptance Criteria
- The actual navigation visibility path is covered, not only the exported nav table.
- No production UI styling or labels change.
- All frontend and backend gates remain green.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written first
- [ ] Code implemented, if a helper extraction is needed
- [ ] Tests/typecheck/lint/build/backend gates passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
