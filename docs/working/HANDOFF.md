# Ralph Handoff

## Last Run
2026-07-09_233958_repair

## Current Status
Slice `005FB-member-portal-dashboard-profile-and-supply-view` completed successfully in repair mode.

Repair diagnosis:
- The prior validation run used bare `python3`, which loaded an incompatible host
  `cryptography` wheel; this repair used `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for all
  backend commands.
- The leftover `2026-07-09_230232_normal_run` worktree had passing tests but exceeded Ralph diff
  limits with 2187 changed lines. This repair reimplemented the slice smaller in the active
  worktree.

What changed:
- Added member-scoped portal APIs:
  `/api/v1/portal/dashboard/`, `/api/v1/portal/profile/`, and
  `/api/v1/portal/produce-supply/`.
- Portal APIs derive scope only from an active `PortalAccount` linked to the authenticated bearer
  token user. Query `member_id` values are ignored as authority.
- Staff/non-portal tokens receive `403 PERMISSION_DENIED` on portal own-data APIs.
- Dashboard returns own member snapshot, own application counts, open-deficiency pending-action
  count, zero loan placeholders, zero future-action placeholders, and empty notices until those
  modules exist.
- Profile reuses existing member, nominee, shareholding, land/crop, KYC, bank-account, and
  cancelled-cheque serializers. PAN/Aadhaar and bank values stay masked; portal `can_view_full` is
  forced false.
- Produce supply returns an empty source-backed shell because `data-model.md` defines
  `produce_supply_records` but no Django model exists yet. A-043 records this.
- MP03, MP04, and prototype `MP22_ProduceSupply.tsx` now call real portal APIs through
  `sfpcl-lms/src/services/portalApi.ts` and keep existing visual patterns.
- API contracts, prototype inventory/gap report, assumptions, Epic 005 digest, and next slices were
  updated.

Source facts used:
- `screen-spec-member-portal.md` MP03 requires own dashboard summary, pending actions, application
  and loan cards, notices, and quick actions.
- `screen-spec-member-portal.md` MP04 requires own profile tabs for member, contact, nominee,
  shareholding, land/crop, bank, and KYC data.
- `screen-spec-member-portal.md` permissions matrix marks MP03/MP04 as own-only.
- `data-model.md` §11.6 defines `produce_supply_records`.
- `api-contracts.md` §13 and §43 guided profile/dashboard envelope conventions.

## Validation
- TDD red/green saved for backend portal member APIs and frontend portal API/view wiring.
- Focused backend portal tests passed: 2 tests.
- Full backend suite passed: 262 tests.
- Backend coverage passed: 95% total, above 85% floor.
- Backend `manage.py check` and `makemigrations --check --dry-run` passed.
- Frontend tests passed: 88 tests.
- Frontend lint, typecheck, and build passed.
- Playwright screenshot capture failed in this sandbox due macOS Mach port permission denial; the
  error log is saved. Static self-contained visual evidence HTML is saved in the run folder.

Evidence is in `.ralph/runs/2026-07-09_233958_repair/`.

## Next Run
Run `005G-member-portal-application-start-status`.

Key instructions for 005G:
- Reuse the active `PortalAccount.member_id` own-data scope from 005FB; do not accept client
  `member_id` as authority.
- MP03 only exposes summary counts. 005G owns MP05/MP09/MP10 application create/list/status wiring.
- Preserve `incomplete_returned` as borrower rectification work with
  `completeness_status = incomplete` and `current_stage = initial_loan_request`.
- Portal application responses must not expose staff completeness/reference/deficiency-resolution
  actions or sensitive member/bank/document internals.
