# Slice 006Y14: Witness Parent Non-Disclosure and Matrix Closure

## Status
Complete

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

## Goal

Close 006Y12's remaining parent-application enumeration path and replace example-based witness
correction coverage with the promised executable contact/identity authority matrix.

## Depends On
- 006Y12

## Runtime Capabilities
- `localhost-e2e-server`

## Source / Review References
- `docs/source/screen-spec.md` S09
- `docs/source/api-contracts.md` §6-§8 and §44
- `docs/source/auth-permissions.md` §3-§3.1, §18-§19, and §24
- `docs/source/codebase-design.md` §26.1-§26.3, §27.1, and §42.2-§42.3
- `docs/slices/006Y12-witness-authority-matrix-and-nondisclosure-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-12_234227_architecture_review`

## Scope

- Enforce permission and application-object non-disclosure before returning any parent application
  or witness lookup fact. Existing out-of-scope and random application IDs must yield the same
  standard `403 OBJECT_ACCESS_DENIED` envelope; in-scope missing parents may remain `404`.
- Execute contact and identity projection/write rows for missing permission, parent object denial,
  witness object non-disclosure, original-verifier maker-checker, stale version, malformed/non-object
  JSON, unknown/immutable fields, and success. Each applicable row asserts the exact six-field action,
  one public PATCH, stable reason/category, and unchanged witness/history/audit/workflow evidence on
  failure.
- Keep application authority behind one public seam. Remove or deepen the zero-leverage compatibility
  wrapper, and test behavioral parity rather than internal mock call counts.
- Retain the mounted one-call behavior and the three trusted real-session screenshots without UI or
  styling changes.

## Trusted Browser Acceptance

- Spec: `e2e/witness-correction-authority.e2e.spec.ts`
- Screenshot: `witness-contact-correction-reloaded.png`
- Screenshot: `witness-verifier-identity-denied.png`
- Screenshot: `witness-checker-identity-corrected.png`

## Test Cases

- Missing and existing out-of-scope application IDs are indistinguishable before witness lookup and
  produce zero evidence; an in-scope missing application remains a normal `404`.
- Parameterized contact/identity rows cover every named authority, payload, version, and success
  variant with exact action/write parity and zero loser evidence.
- Mounted failures perform one PATCH and no post-mutation GET; successes perform one PATCH and one
  canonical collection GET. Trusted runs preserve the existing exact request counts/screenshots.

## Evidence Required

Failing parent-enumeration and incomplete-matrix logs, green backend/mounted matrices, dependency
scan, browser collection, two trusted runs with screenshots, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Witness PATCH cannot disclose either parent application or child witness existence outside scope.
- Both correction kinds have independently executable projection/write/evidence parity for every
  required denial and success class through the public authority seam.
