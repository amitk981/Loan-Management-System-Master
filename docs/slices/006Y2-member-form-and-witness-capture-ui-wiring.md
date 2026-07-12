# Slice 006Y2: Member Form and Witness Capture UI Wiring

## Status
Complete

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

## Goal
Give the 006Y member create/update contract and the 004E witness backend a reachable staff UI: member registration/edit forms (individual and FPC) and a witness capture/read/edit surface. Application Detail currently shows "No API-backed witness details" even though 004E delivered the APIs (PRODUCTION_COMPLETION_BLUEPRINT.md §6.3).

## User Value
Staff register members and capture witness/shareholder details in the product instead of via seed data or offline records.

## Depends On
- 006Y

## Runtime Capabilities
- `localhost-e2e-server`

## Trusted Browser Acceptance
- Spec: `e2e/member-governance-closure.e2e.spec.ts`
- Screenshot: `member-create.png`
- Screenshot: `member-identity-locked.png`
- Screenshot: `member-reverification.png`
- Screenshot: `witness-capture.png`
- Screenshot: `member-governance-unauthorized.png`

## Source References
- docs/source/screen-spec.md member registration/profile screens and witness sections
- docs/source/api-contracts.md section 13 (member create/update), section covering witness endpoints delivered by 004E
- docs/source/auth-permissions.md member/witness permission codes
- docs/slices/004E-witness-shareholder-validation.md (delivered backend contract)
- docs/slices/004E2-witness-evidence-snapshot-and-input-hardening.md

## Prototype Reference
- sfpcl-lms/src/pages/members/MemberDirectory.tsx and MemberProfile.tsx (form patterns)
- sfpcl-lms/src/pages/applications/ApplicationDetail.tsx (witness panel)

## Concrete Requirements
1. Member create form and profile edit form wired to `POST/PATCH /api/v1/members/` with individual/FPC variants, backend field errors surfaced inline, and KYC-locked fields rendered read-only with the lock reason from the contract.
2. Witness panel in Application Detail (and the member profile where the spec places it) wired to the 004E witness APIs for capture, read, and edit, including the 004E2 evidence snapshot behaviour.
3. Role-gated visibility: create/edit controls appear only for roles holding the mutation permissions; others get read-only or unauthorized states. Assert 403 on direct API calls.
4. Loading, empty, error, unauthorized, validation, and stale states; reuse existing form/panel patterns, no new visual design.
5. Record any contract mismatch discovered while wiring in API_CONTRACTS.md rather than papering over it client-side.

## Test Cases
- Form submission asserts exact URL/body; backend validation errors render at the field level.
- Locked identity fields are read-only after verification and the reverification path is reachable per 006Y contract.
- Witness capture/edit round-trips through the 004E APIs; snapshot behaviour preserved.
- Non-permitted roles see no mutation controls; direct calls 403.

## Out of Scope
Backend contract changes (006Y), sensitive reveal UI (004K owns), portal profile/KYC correction (011M2).

## Risk Level
Medium

## Acceptance Criteria
- A member can be created and corrected, and witnesses captured, end to end through the UI with audit trails.
- All gates pass; screenshots of forms, locked-field state, witness panel, and unauthorized state saved.

## Run-Ahead Sharpening Review (006X, 2026-07-11)

- Mount the real directory/profile/application-detail containers in interaction tests: assert
  exact member POST/PATCH and witness create/update bodies, then refresh from their canonical GET
  endpoints rather than merging response facts into local state.
- Treat backend identity-lock and stale-write errors as authoritative field/state facts. A global
  permission from `/auth/me` must not expose mutation controls when the selected member or witness
  resource disables the action; retain the existing directory/profile/witness panel composition.

## Run-Ahead Sharpening Review (architecture review 2026-07-11_230238)

- Use a mounted default-container Testing Library matrix from the first failing test; static child
  markup, source-string assertions, and route-only Playwright fixtures do not prove member/witness
  HTTP wiring. Assert exact mutation plus canonical GET refresh counts and one-call 400/403/409.
- Declare a `localhost-e2e-server` runtime and exact `Trusted Browser Acceptance` spec/screenshots
  before implementation. The contract must collect non-zero tests and exercise real authenticated
  backend sessions for create, locked-field/reverification, witness capture, and unauthorized state.

## Run-Ahead Sharpening Review (006X3, 2026-07-12)

- Keep one collectable declared spec and committed one-line encoded Chromium baselines so binary
  artifacts cannot exhaust Ralph's changed-line budget. Trusted run 1 creates only absent
  baselines; trusted run 2 must compare all five without refresh.
- Reopen the routed screen after every browser reload; assert resource actions before mutation and
  canonical GET refreshes after success, with no client merge/retry on 400/403/409.

## Run-Ahead Sharpening Review (006Y, 2026-07-12)

- Member mutations must send the detail response's current `version`. Render
  `VERIFIED_IDENTITY_LOCKED` as the existing locked-field state and call the dedicated
  `/reverification/` action only with a non-empty reason; after success refetch canonical detail.
- Consume only the six-field `members.member.update` and `members.member.reverify_identity`
  resource actions. Preserve the backend's 400/403/409 response without client retries or local
  state merging, and never place plaintext identity values in browser fixtures or screenshots.

## Done Checklist
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] Permissions tested
- [x] Audit events tested
- [x] Visual evidence delegated to trusted browser acceptance (local Chromium denied macOS services)
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [ ] Commit created only after passing gates
