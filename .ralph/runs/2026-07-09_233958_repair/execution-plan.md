# Execution Plan

Selected slice: 005FB-member-portal-dashboard-profile-and-supply-view

Mode: repair

## Repair Diagnosis
- Most recent failed validation evidence:
  - `.ralph/runs/2026-07-09_225628_validate/ralph-artifact-validation.md` failed because
    validation artifacts were missing in that validation folder.
  - `.ralph/runs/2026-07-09_225628_validate/backend-check-results.md` and
    `backend-test-results.md` failed because the command used bare `python3`, which loaded an
    incompatible host `cryptography` wheel.
- Leftover failed worktree inspected read-only:
  `/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-09_230232_normal_run`.
  Its implementation passed tests but failed Ralph diff limits:
  `2187` changed lines against the `2000` limit.
- Repair strategy: reimplement the selected slice in the active worktree only, use the required
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for backend commands, and keep code/docs changes
  smaller than the diff limit.

## Source Facts
- `screen-spec-member-portal.md` MP03 requires own-only dashboard cards for profile, pending
  actions, application/loan summary, repayment summary, notices, and quick actions.
- `screen-spec-member-portal.md` MP04 requires own-only profile tabs for member, contact, nominee,
  shareholding, land/crop, bank, and KYC status.
- `screen-spec-member-portal.md` permissions matrix marks MP03/MP04 as own-only and blocks other
  member access.
- `data-model.md` documents `produce_supply_records`, but no backend model exists in this
  codebase yet; the slice requires a documented empty shell rather than invented data.
- `api-contracts.md` dashboard examples use standard success envelopes with cards/tasks, and
  member/profile responses must preserve masked sensitive fields.

## Implementation Plan
1. Backend TDD red loop:
   - Add focused tests for portal dashboard/profile/supply endpoints.
   - Cover borrower own scope, staff-token denial, open-deficiency count, masked profile data, and
     empty produce-supply shell.
   - Save failing output to `evidence/terminal-logs/backend-portal-member-red.log`.
2. Backend implementation:
   - Add a thin `members.portal_services` module that derives the member from the active
     `PortalAccount` linked to the authenticated portal user.
   - Reuse existing member serializers for profile, nominees, shareholdings, land/crop, KYC, bank
     accounts, and cancelled cheques.
   - Count current own loan applications and open deficiencies from implemented application
     tables. Return zero placeholders for future loan/signature/repayment/KYC/closure actions.
   - Add `GET /api/v1/portal/dashboard/`, `/api/v1/portal/profile/`, and
     `/api/v1/portal/produce-supply/`.
3. Frontend TDD red/green:
   - Add a compact portal API client test for bearer-auth calls.
   - Add screen tests proving MP03/MP04/MP22 render backend data, masked values, and empty states.
   - Save red/green logs under `evidence/terminal-logs/`.
4. Frontend implementation:
   - Wire existing MP03, MP04, and MP22 screens to real portal APIs using existing layout, cards,
     badges, tables, alerts, colors, spacing, and typography.
   - Keep loading/error/empty states in existing portal patterns.
5. Documentation/artifacts:
   - Update API contracts, assumptions, digest, prototype inventory/gap report only with concise
     005FB facts.
   - Update slice status, Ralph progress/state/handoff, changed files, risk assessment, review
     packet, final summary, and evidence.
6. Gates:
   - Focused backend tests, full backend tests, backend check, migrations check, coverage.
   - Frontend lint, typecheck, tests, and build.
   - `git diff --check` and diff-limit awareness before finalizing.
