# Slice 004E2: Witness Evidence Snapshot and Input Hardening

## Status
Not Started

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

## Goal

Make witness verification durable and envelope-safe by snapshotting the exact qualifying
shareholding/folio and rejecting malformed bodies without server errors.

## Depends On
- 002J2

## Source / Review References
- `docs/source/data-model.md` §10.5, §29, and §30
- `docs/source/api-contracts.md` §6-§8
- `docs/source/codebase-design.md` §6.3, §7.2, and §25
- `docs/slices/004E-witness-shareholder-validation.md`
- `docs/working/REVIEW_FINDINGS.md` entry for this review

## Scope

- Persist the exact active positive `Shareholding` used at verification and an immutable folio
  snapshot on `Witness`; use protected FKs and one additive migration. Backfill existing rows only
  when the audit/member/shareholding facts identify one unambiguous qualifying row; otherwise keep
  explicit nullable legacy provenance rather than guessing.
- Serialize the stored verification-time shareholding/folio. A later shareholding status, folio,
  count, or newly created holding must not rewrite an existing witness response or audit evidence.
- Catch malformed JSON, arrays/non-object JSON, missing fields, and unknown fields at the nested
  witness adapter and return the standard `400 VALIDATION_ERROR` envelope with no witness/audit/
  workflow write.
- Remove redundant indexes caused by combining Django FK/`db_index=True` indexes with duplicate
  explicit `Meta.indexes`; retain exactly the application and identity-hash indexes required by
  the source model.
- Move list/query/serialization composition behind the application-owned witness service/module
  seam so the HTTP view remains authenticate/parse/call/translate only.

## Test Cases

- Failing-first malformed/non-object JSON regressions assert a standard 400 and zero writes.
- Create a witness, then mutate/deactivate/add shareholdings and change folio values; GET must retain
  the original shareholding UUID and folio snapshot.
- Migration tests cover unambiguous backfill, ambiguous/no-match quarantine, reverse safety, and
  migration idempotency; schema inspection asserts no duplicate application/hash indexes.
- Preserve permission/object-access, masking, KYC/name/shareholder, forged-metadata, and metadata-
  only audit tests from 004E.

## Evidence Required

Red/green API and migration output, stable before/after response examples, index inspection, and all
configured gates.

## Risk Level
Medium

## Acceptance Criteria

- Witness reads expose immutable verification-time shareholding evidence.
- Every malformed body is enveloped, and the witness schema contains no redundant indexes.

## Sharpened Implementation Anchors (2026-07-11)

- Extend `applications.models.Witness` with a protected nullable verification-time shareholding FK
  and immutable folio snapshot; the single migration owns both schema and conservative backfill.
- Drive red/green coverage through `loan_application_witnesses`, `create_witness`, and
  `serialize_witness`; list composition must leave the view and remain in `applications.services`.
- The migration/schema regression must name the retained application and identity-hash indexes so
  duplicate implicit FK/explicit indexes cannot silently return.
