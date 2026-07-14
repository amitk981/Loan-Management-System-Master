# Slice 008A2: Template Effective Integrity and File Reference Boundary

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Depends On
- 008A

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal

Make the 008A template catalogue's approved effective-range invariant race-safe and route template
file references through one documents-owned provenance/permission decision before 008B consumes
them for generation.

## Source / Review References

- `docs/source/api-contracts.md` §§3, 6-8, 26.1-26.4
- `docs/source/data-model.md` §§16.1-16.3, 30, and 34
- `docs/source/codebase-design.md` §§7.2, 26.1-27.1, and 36.1
- `docs/working/digests/epic-008-documentation-security-package.md` §008A-008B
- `docs/slices/008A-document-template-model-and-versioning.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-14_064206_architecture_review`

## Concrete Requirements

1. Serialize every create/successor for the same `document_type` plus nullable borrower variant
   through a database-backed identity lock (or an equally strong portable constraint). Locking only
   rows that already exist is insufficient. Two concurrent first approved versions with different
   codes/versions but overlapping effective dates must persist exactly one winner.
2. Keep exact successor replay zero-write and retain the predecessor. Concurrent non-overlapping
   versions may both succeed only when their effective ranges and lineage rules are valid; losing
   overlap/duplicate attempts write no template, audit, or version-history evidence.
3. Add one public documents-owned template-file reference decision. It must verify existence,
   immutable upload metadata consistency, global/template-source provenance, sensitivity validity,
   and the exact actor permission needed to reference the file. A direct `DocumentFile` query or
   `documents.file.download` permission alone is not reference authority; template read/manage
   still grants no download action or storage descriptor.
4. Fail closed for a missing upload ledger, application/loan-owned file, mismatched audit metadata,
   unsupported sensitivity, or unrelated actor. Do not invent an Annexure-letter, category-to-
   template, file-format, or borrower-variant business mapping absent from source.
5. Move template list/filter/query shaping to a documents selector and pass transport-neutral
   request metadata into the write module. Preserve the exact §26.3 routes/envelopes, strict filters,
   bounded pagination, immutable successor/evidence contract, and metadata-only response.
6. Reconcile the source `Individual/FPO` template vocabulary with the repository's
   `individual_farmer`/`fpc`/`producer_institution` member vocabulary behind one explicit resolver.
   Until governance confirms a mapping, unresolved variants fail with a configuration-required
   validation result; 008B must not guess or select across variants.

## Database / Migration Impact

At most one non-destructive migration for the template-identity lock/constraint. Do not rewrite
retained template versions, file ids, or disputed Annexure metadata.

## Test Cases

- Five PostgreSQL requests create different-code/different-version overlapping first approved
  rows for one identity: one succeeds and one approved interval/evidence set remains.
- Concurrent exact successor replay returns one linked successor; non-overlapping identities and
  borrower variants remain independent.
- A real globally attributable template upload is referenceable; a direct file row, missing or
  corrupt upload audit, application-owned file, inaccessible file, and permission-only file all
  fail with indistinguishable zero-write validation.
- Reader/manager/download/reference matrices prove metadata, mutation, reference, and download
  authority remain separate.
- List/filter/page behavior remains standard-envelope and selector-owned; no generation endpoint or
  rendered borrower document is added.

## Evidence Required

Backend RED/GREEN output, two PostgreSQL race passes, file-reference boundary matrices, migration
sync, sanitised API examples, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Approved effective ranges cannot overlap under first-row or successor races.
- Template files cross one provenance-aware documents boundary and confer no download authority.
- Borrower variant ambiguity fails closed before generation.
- All configured gates pass.

