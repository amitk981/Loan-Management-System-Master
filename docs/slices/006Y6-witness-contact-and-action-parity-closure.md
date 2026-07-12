# Slice 006Y6: Witness Contact and Action Parity Closure

## Status
Not Started

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

## Goal

Complete 006Y4's S09 witness correction surface and make disabled resource actions faithfully
project the same permission/object/maker-checker denials as their writes.

## Depends On
- 006Y4

## Source / Review References
- `docs/source/screen-spec.md` S09
- `docs/source/data-model.md` §10.5 and §29-§30
- `docs/source/api-contracts.md` §6-§8 and §44
- `docs/source/codebase-design.md` §23.3-§23.6, §26.3, and §42.2-§42.3
- `docs/slices/006Y4-witness-correction-and-resource-action-closure.md`
- `docs/working/ASSUMPTIONS.md` A-069
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-12_125256_architecture_review`

## Scope

- Add S09 address and mobile to the versioned witness record, protected correction history, API
  projection, form, and non-destructive migration. Preserve immutable member/shareholding/folio/
  verification provenance.
- Return read/create/update actions as six-field projections even when disabled. Use the same
  permission, application-object, and maker-checker evaluations consumed by capture/correction;
  do not omit denied actions or infer authority in React.
- Validate exact writable/immutable fields, mobile/address shapes, version, protected identities,
  and malformed/unknown payloads before persistence. Preserve one-call standard errors and zero
  evidence on denial.
- Canonically refetch the witness collection after contact or identity correction using the
  existing Application Detail surface.

## Test Cases

- Backend projection/write matrix covers missing read/create/update permission, object denial,
  verifier identity correction, contact-only correction, stale version, and immutable evidence.
- Mounted tests click contact and identity updates, assert exact bodies/refetch counts, and prove a
  disabled/absent authority cannot invoke a mutation.
- Real-browser flow corrects address/mobile, proves denied action reason, and reloads canonical data.

## Evidence Required

Failing-first backend/frontend logs, green parity matrix, masked history/audit examples, exact HTTP
examples, routed browser screenshots, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- All S09 mutable witness fields round-trip through governed correction without rewriting
  verification evidence.
- Disabled resource actions expose stable reasons and cannot diverge from public writes.

