# Slice 006Y4: Witness Correction and Resource Action Closure

## Status
Complete

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

## Goal

Deliver the witness edit path that 006Y2 declared but deferred: a versioned, audited backend
correction contract, resource-owned actions, and mounted/real-browser proof through Application
Detail without changing immutable shareholder-verification evidence.

## Depends On
- 006Y3

## Runtime Capabilities
- `localhost-e2e-server`

## Trusted Browser Acceptance
- Spec: `e2e/member-governance-closure.e2e.spec.ts`
- Screenshot: `witness-capture-refetched.png`
- Screenshot: `witness-correction-refetched.png`
- Screenshot: `witness-correction-stale.png`
- Screenshot: `witness-resource-denied.png`

## Source / Review References
- `docs/source/data-model.md` §10.5 and §29-§30
- `docs/source/screen-spec.md` S09
- `docs/source/auth-permissions.md` §12.2, §15.4, §26.4, and §34
- `docs/source/api-contracts.md` §6-§8 and §44
- `docs/source/codebase-design.md` §23.3-§23.6, §26.3, and §42.2-§42.3
- `docs/slices/004E-witness-shareholder-validation.md`
- `docs/slices/004E2-witness-evidence-snapshot-and-input-hardening.md`
- `docs/slices/006Y2-member-form-and-witness-capture-ui-wiring.md`
- `docs/working/ASSUMPTIONS.md` A-062, A-063, and A-066
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-12_092009_architecture_review`

## Scope

- Define versioned witness correction through a narrow application-owned public module seam. Add
  the exact update permission/action following the existing witness namespace; do not borrow a
  nominee/member permission or hard-code a role. Record the source permission gap in assumptions.
- Permit correction only for source-backed mutable contact/identity/display fields confirmed by
  S09. The verification-time member, shareholding UUID, folio snapshot, shareholder-qualified fact,
  verification actor/time, and evidence provenance are immutable; a proposed member/folio change
  must use a new capture or explicitly re-run governed shareholder/KYC verification rather than
  rewriting evidence.
- Require current version, exact application object access, protected identity storage, masked
  responses/history/audit, standard field errors, maker-checker where verification changes, and
  one-call stale/conflict behavior. Project six-field read/create/update actions from the same
  evaluations consumed by writes.
- Return witness list/detail as a resource envelope carrying actions; remove App's `/auth/me`
  permission-derived witness controls. Application Detail must consume only resource actions,
  surface loading/empty/error/unauthorized/validation/stale states, and refetch the canonical list
  after successful capture/correction without local synthesis.
- Reuse the existing Witness tab, form, alert, card, and modal patterns. Do not add a new layout,
  colour, badge, table, or typography system.

## Test Cases

- Backend tests cover capture/read/update, exact mutable allowlist, immutable evidence rejection,
  protected identity, version conflicts, object access, permission, maker-checker, and metadata-only
  audit/history with zero writes on `400`/`403`/`409`.
- Mounted Application Detail tests click capture and correction through mocked authenticated HTTP,
  assert exact bodies/counts and canonical refetch, and prove absent/disabled actions cannot invoke.
- The declared real-session browser contract performs capture and correction, proves stale and
  denied states, and emits all four screenshots twice.

## Evidence Required

Failing-first backend/frontend logs, exact HTTP and masked audit examples, immutable-evidence proof,
two trusted-browser runs with four screenshots, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Witness capture, read, and correction round-trip through governed APIs and the routed UI while
  verification-time shareholder evidence remains immutable.
- No witness mutation control derives authority from `/auth/me`, and every success/error path is
  proven through the mounted container and real browser.
