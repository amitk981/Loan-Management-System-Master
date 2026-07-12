# Slice 006Y3: Member Registry and Identity Change Approval Closure

## Status
Not Started

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

## Goal

Move governed member writes behind the documented Member Registry seam, reject duplicate identity,
record complete masked field history, and replace reason-only reverification with the approved
change-request workflow required by M02-FR-012, reachable through the existing staff UI.

## Depends On
- 006X4

## Runtime Capabilities
- `localhost-e2e-server`

## Trusted Browser Acceptance
- Spec: `e2e/member-governance-closure.e2e.spec.ts`
- Screenshot: `member-create-submitted.png`
- Screenshot: `member-update-refetched.png`
- Screenshot: `member-identity-change-requested.png`
- Screenshot: `member-identity-change-approved.png`
- Screenshot: `member-governance-denied.png`

## Source / Review References
- `docs/source/codebase-design.md` §6.3-§6.4, §10.1, §26.3, and §42.2-§42.3
- `docs/source/api-contracts.md` §6-§8, §13, and §44
- `docs/source/auth-permissions.md` §12.2, §17-§18, §25.1, and §34.2
- `docs/source/data-model.md` §10.1-§10.3, §29-§30, and §34
- `docs/source/functional-spec.md` M02-FR-001 and M02-FR-012 plus M02 acceptance criteria
- `docs/slices/006Y-member-create-update-and-identity-governance.md`
- `docs/slices/006Y2-member-form-and-witness-capture-ui-wiring.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-12_092009_architecture_review`

## Scope

- Introduce `members.modules.member_registry.MemberRegistry` as the public create/update/read and
  identity-change seam. It must enforce exact permissions and existing object scope internally;
  views remain adapters and no non-HTTP caller can bypass governance.
- Reject duplicate member PAN/Aadhaar before creation and at the database concurrency boundary,
  returning standard field errors with zero member/profile/history/audit writes. Validate unknown,
  malformed, missing, wrong-variant, date, email, nested-profile, folio, and identity inputs before
  model persistence; database integrity errors must not escape as `500` responses.
- Store complete field-level masked create/update history. Nested individual/institution profile
  facts must be represented without plaintext identity; address updates must contain real old/new
  address objects rather than `null` placeholders.
- Replace direct reason-only reverification with a persisted optimistic identity change request.
  Request creation stores protected proposed values, reason, requester, member version, and pending
  status. A different actor holding a dedicated approval permission may approve once; approval
  atomically applies the protected identity, resets KYC to pending, clears re-KYC due date, writes
  masked history/audit, and increments the member version. No hard-coded approver role or automatic
  approval is allowed; record the new permission/assignment default in `ASSUMPTIONS.md`.
- Project request/update/approval actions from the same evaluations consumed by writes. Direct
  identity PATCH and the legacy reason-only endpoint must fail closed or become a compatibility
  adapter that requires an approved request; pending-KYC and stale requests cannot be applied.
- Complete the source §13.2 individual and institution registration fields in the existing form.
  Use an existing modal/action pattern instead of permanently prepending a form card to Directory
  or Profile. Successful create/update/request/approval must refetch canonical resources.

## Test Cases

- Red/green Member Registry tests cover both member variants, duplicate PAN/Aadhaar races, malformed
  nested payloads, complete masked history, standard errors, and zero-write denials.
- A request/approve matrix covers requester-checker separation, exact permission, object scope,
  locked/pending KYC, current/stale versions, repeat approval, and action/write parity.
- Mounted routed-container tests assert exact member POST/PATCH/request/approve bodies, canonical
  GET counts, field errors, and one-call `400`/`403`/`409` without client retry or local merge.
- The declared real-session browser contract submits member creation and update, completes the
  two-actor identity-change path, proves denial, and emits all five screenshots twice.

## Evidence Required

Failing-first backend/frontend logs, duplicate-race evidence, exact HTTP examples, masked history
examples, action/write matrix, two trusted-browser runs with five screenshots, and all gates.

## Risk Level
High

## Acceptance Criteria

- M02-FR-012 is satisfied by a real approved change request, not a free-text reason acting as
  approval, and every mutation is safe through the public Member Registry interface.
- Full source payload variants, duplicate rejection, masked field history, and routed staff flows
  are proven end to end without changing the approved visual system.

