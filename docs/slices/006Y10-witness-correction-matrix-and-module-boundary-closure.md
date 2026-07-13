# Slice 006Y10: Witness Correction Matrix and Module Boundary Closure

## Status
Complete

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

## Goal

Execute the witness denial/error matrix omitted by 006Y8 and leave one acyclic owner for correction
authority, projection, and write enforcement.

## Depends On
- 006Y8

## Runtime Capabilities
- `localhost-e2e-server`

## Source / Review References
- `docs/source/screen-spec.md` S09
- `docs/source/api-contracts.md` §6-§8 and §44
- `docs/source/auth-permissions.md` §18-§19 and §24
- `docs/source/codebase-design.md` §23.3-§23.6, §26.3, §36.1-§36.2, and §42.2-§42.3
- `docs/slices/006Y8-witness-maker-checker-and-browser-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-12_203645_architecture_review`

## Scope

- Make the application-owned witness-correction module the single owner of exact permission,
  application-object scope, correction-kind maker-checker, and version evaluation. Remove the
  `applications.services -> witness_corrections -> applications.services` runtime import cycle and
  the duplicate/discarded object-access calculation; serializers only translate returned actions.
- Execute projection/write parity for contact and identity corrections under missing permission,
  object denial, original-verifier maker-checker denial, stale version, malformed/non-object JSON,
  unknown/immutable fields, and success. Assert exact reason/category and zero loser evidence.
  Both correction actions require `members.witness.update`; object denial returns
  `OBJECT_ACCESS_DENIED`, permission/maker-checker denial returns `FORBIDDEN`, payload failures return
  `VALIDATION_ERROR`, and stale `version` returns `VERSION_CONFLICT`.
- Extend the mounted `WitnessPanel` suite to drive API-wrapper `400`, `403`, and `409` failures for
  both correction kinds. Each submit makes exactly one PATCH, no retry/refetch/local merge on error,
  retains server field/reason facts, and refetches the canonical collection exactly once on success.
- Instrument the real browser scenario's request stream: verifier denial must record zero witness
  PATCH requests, while contact/checker successes each record one exact versioned body and one
  canonical GET. Keep all three existing screenshot states and approved visual composition.

## Trusted Browser Acceptance

- Spec: `e2e/witness-correction-authority.e2e.spec.ts`
- Screenshot: `witness-contact-correction-reloaded.png`
- Screenshot: `witness-verifier-identity-denied.png`
- Screenshot: `witness-checker-identity-corrected.png`

## Trusted Browser Scenario

- Use the real staff login, routed Application Detail, and backend responses without interception,
  token injection, or local-storage mutation.
- Assert exact PATCH/GET counts and bodies around contact success, verifier denial, checker identity
  success, reload, and the three declared screenshots.

## Test Cases

- Backend table covers every named authority/payload/version case for contact and identity writes.
- Mounted table covers `400 VALIDATION_ERROR`, `403` authority/object/maker-checker, and
  `409 VERSION_CONFLICT` with one-call/no-refetch behavior.
- Static dependency regression rejects imports from `applications.modules.witness_corrections` back
  into `applications.services` and requires serializer callers to consume the public projection.

## Evidence Required

Failing-first dependency/backend/frontend logs, green parity/error tables, exact request-count output,
browser collection, two trusted runs with all screenshots, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- One acyclic public seam owns witness correction authority and both projection/write callers agree.
- Every required negative HTTP/UI path is executable, one-call, canonical, and evidence-free.
