# Execution Plan

Selected slice: `011M2-member-portal-kyc-correction-request`

## Decision and boundaries

- Implement the full correction-request path. No owner-approved deferral for 011M2 is recorded in
  `ASSUMPTIONS.md` and `HIGH_RISK_APPROVALS.md`.
- Keep portal access derived exclusively from the authenticated active `PortalAccount`; never accept
  a caller-selected member as authority.
- A submitted request never edits `Member` or `KycProfile`. Staff approval delegates to the existing
  governed member identity-change/reverification path, retaining member history and KYC locking.
- Portal projections expose borrower-facing status, dates, requested changes, evidence metadata, and
  rejection reason only. Staff-only notes and reviewer identity remain internal.
- Use one additive members migration and no new dependency. Reuse existing document, audit, workflow,
  API-envelope, portal layout, form, alert, badge, table, and upload patterns.

## TDD behavior sequence

1. RED/GREEN: an active portal member submits one evidence-backed correction request for their own
   member; the request is pending, creates immutable audit/workflow evidence, and leaves member/KYC
   facts unchanged.
2. RED/GREEN: cross-member claims, evidence not owned by the portal member, missing/unsupported
   fields, and inactive/non-portal callers are rejected with no correction/member/history writes;
   denied cross-scope attempts are audited.
3. RED/GREEN: staff can list/retrieve the governed queue only with member-update authority and
   object scope; a reviewer moves a request to under-review with audit/workflow history.
4. RED/GREEN: approval of a locked identity correction creates and approves the existing governed
   identity-change request, updates masked member history, resets KYC for reverification, links an
   open 011M review when present, and publishes approved status to the borrower.
5. RED/GREEN: rejection requires a borrower-safe reason, publishes rejected status/dates without
   internal notes, and records audit/workflow history.
6. RED/GREEN frontend: MP04 loads correction history, handles loading/empty/error/unauthorized and
   validation states, uploads restricted KYC evidence, submits a correction, and renders detail/status.
7. RED/GREEN browser: add the exact declared Playwright spec and capture
   `portal-kyc-correction-decision.png` from two passing runs at a mobile viewport.

## Planned product changes

- Add the correction request/evidence model and migration under the members owner.
- Add a focused deep service for portal submission/projection and staff review/decision, calling
  existing document ownership, member-governance, audit, workflow, and KYC-review seams.
- Add portal list/create/detail endpoints and staff queue/detail/review/approve/reject endpoints,
  standard envelopes, URL registrations, and working API contract documentation.
- Extend the portal API client and MP04 profile screen using existing visual compositions; update
  prototype inventory/gap records because this closes a documented missing surface.
- Add focused backend API/service/permission/audit tests, frontend component/client tests, and the
  trusted browser acceptance spec.

## Focused validation and evidence

- Save every backend RED and GREEN command output under
  `.ralph/runs/2026-07-23_095043_normal_run/evidence/terminal-logs/` using the mandated venv Python.
- Run focused backend labels only (no complete suite/coverage), Django check, and migration sync.
- Run impacted Vitest files, frontend typecheck, lint, and build.
- Run the declared Playwright spec twice and save the real screenshot if Chromium is available;
  otherwise preserve the launch/runtime output for trusted validation without fabricating evidence.
- Record the permission/locked-field matrix, API examples, risk assessment, self-review, and set the
  review packet Result exactly to `Ready for independent validation`.
