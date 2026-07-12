# Slice 006Y8: Witness Maker-Checker and Browser Closure

## Status
Not Started

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

## Goal

Make witness update actions faithfully project identity maker-checker authority and deliver the real
routed correction proof required but not executed by 006Y6.

## Depends On
- 006Y6

## Runtime Capabilities
- `localhost-e2e-server`

## Source / Review References
- `docs/source/screen-spec.md` S09
- `docs/source/data-model.md` §10.5 and §29-§30
- `docs/source/api-contracts.md` §6-§8 and §44
- `docs/source/codebase-design.md` §23.3-§23.6, §26.3, and §42.2-§42.3
- `docs/slices/006Y6-witness-contact-and-action-parity-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-12_141135_architecture_review`

## Scope

- Split or parameterise witness correction actions only as needed so contact-only and protected-
  identity updates express the exact authority they govern; React must never infer which fields a
  verifier may change.
- Projection and write must share exact permission, application-object, maker-checker, version, and
  immutable-evidence evaluations. The original verifier cannot see an enabled identity-correction
  action that its write rejects. Each projected action must contain exactly §44's six fields and
  preserve the backend denial reason verbatim in the routed control.
- Extend the backend matrix across verifier identity correction, allowed contact-only correction,
  missing permission, object denial, stale version, malformed/unknown payloads, and immutable
  verification evidence, with exact reasons/categories and zero evidence on denial.
- Mount the routed Application Detail container for exact correction bodies, one canonical
  collection refetch, `400`/`403`/`409` one-call behavior, disabled reasons, and absence of forbidden
  mutation calls.

## Trusted Browser Acceptance

- Spec: `sfpcl-lms/e2e/witness-correction-authority.e2e.spec.ts`
- Start from the real staff login boundary and routed Application Detail; no API route interception,
  direct local-storage token injection, or mocked witness response is allowed.
- Correct address/mobile as an authorised actor, reload, and prove canonical persisted values.
- As the original verifier, show the backend-projected identity-correction denial and prove no PATCH;
  then use a separate authorised checker to correct masked identity and reload it.
- Required screenshots:
  - `evidence/screenshots/witness-contact-correction-reloaded.png`
  - `evidence/screenshots/witness-verifier-identity-denied.png`
  - `evidence/screenshots/witness-checker-identity-corrected.png`

## Test Cases

- Backend projection/write parity covers verifier versus checker separately for contact and identity
  fields; no generic enabled update action may over-promise authority.
- Mounted tests assert exact request counts/bodies, canonical refetch, server field errors, and no
  mutation from disabled controls.
- Trusted browser collection discovers the named tests and the orchestrator produces all three
  screenshots in two independent runs.

## Evidence Required

Failing-first backend/frontend logs, green parity matrix, exact HTTP/history examples, browser
collection, trusted screenshot outputs, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Witness action facts and writes agree for permission, object scope, maker-checker, and stale state.
- Address/mobile and protected identity correction are proven through the real routed/authenticated UI.
