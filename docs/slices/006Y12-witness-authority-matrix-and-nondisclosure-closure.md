# Slice 006Y12: Witness Authority Matrix and Non-Disclosure Closure

## Status
Complete

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

## Goal

Finish 006Y10 with one reusable application-object authority seam, a complete correction matrix, and
resource non-disclosure before witness lookup.

## Depends On
- 006Y10

## Runtime Capabilities
- `localhost-e2e-server`

## Source / Review References
- `docs/source/screen-spec.md` S09
- `docs/source/api-contracts.md` §6-§8 and §44
- `docs/source/auth-permissions.md` §18-§19 and §24
- `docs/source/codebase-design.md` §26.1-§26.3, §36.1-§36.2, and §42.2-§42.3
- `docs/slices/006Y10-witness-correction-matrix-and-module-boundary-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-12_220748_architecture_review`

## Scope

- Remove the copied creator/receiver/Credit Manager object-access algorithm from
  `witness_corrections`. Extract or reuse one lower-level application-owned authority evaluator that
  both generic application access and witness projection/write consume without a runtime import
  cycle. The boundary regression must assert behavioral use of that seam, not a source substring.
- For PATCH, enforce permission and application object non-disclosure before witness lookup. Missing
  and existing witness IDs outside the actor's scope must produce the same standard `403` category
  and reveal no witness/application facts; in-scope missing IDs may remain `404`.
- Execute contact and identity projection/write rows for missing permission, object denial,
  original-verifier maker-checker, stale version, malformed/non-object JSON, unknown/immutable
  fields, and success. Every applicable row asserts exact six-field action, stable reason/category,
  one public PATCH/write, and unchanged witness/history/audit/workflow evidence on failure.
- Complete the mounted `WitnessPanel` matrix for distinct permission, object, maker-checker,
  validation, and version responses for both correction kinds. Assert exact versioned bodies, one
  mutation, no retry/refetch/local merge on failure, and one canonical collection GET on success.
- Retain the three real-session screenshots and exact browser PATCH/GET counts with no interception,
  token injection, local-storage mutation, or styling change.

## Trusted Browser Acceptance

- Spec: `e2e/witness-correction-authority.e2e.spec.ts`
- Screenshot: `witness-contact-correction-reloaded.png`
- Screenshot: `witness-verifier-identity-denied.png`
- Screenshot: `witness-checker-identity-corrected.png`

## Test Cases

- Backend parameter table covers both correction kinds and every named authority/payload/version
  variant with exact response/category and zero loser evidence.
- Out-of-scope PATCH returns indistinguishable `403` envelopes for existing and random witness IDs.
- Mounted failures make one PATCH and zero post-mutation GETs; successes make one PATCH plus one
  canonical GET and render only the returned masked values.

## Evidence Required

Failing-first duplicated-seam/enumeration logs, green backend and mounted matrices, dependency scan,
browser collection, two trusted runs with all screenshots, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- One acyclic evaluator owns application object access for witness projection and write enforcement.
- Every named correction denial is executable, evidence-free, and unable to disclose resource
  existence; frontend behavior remains backend-authored and one-call.
