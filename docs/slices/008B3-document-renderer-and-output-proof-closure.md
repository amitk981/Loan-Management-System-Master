# Slice 008B3: Document Renderer and Output Proof Closure

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Depends On
- 008B2

## Runtime Capabilities

none

## Goal

Replace the metadata-only rendering claim with a bounded legal-document renderer seam and prove
that genuine approved Word templates produce readable, structurally valid Word and PDF outputs.

## Source / Review References

- `docs/source/codebase-design.md` §§14.1, 18, 27.1, 36.1, 42.2, and 44.1
- `docs/source/functional-spec.md` §15.1 and M06-FR-013/M06-FR-015
- `docs/source/implementation-roadmap.md` §13.3 and the PDF-generation dependency/risk entries
- `docs/source/api-contracts.md` §26.4-26.5
- `docs/working/digests/epic-008-documentation-security-package.md` §008B
- `docs/slices/008B-document-generation-shell.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-14_093142_architecture_review`

## Concrete Requirements

1. Put rendering behind a legal-documents-owned interface independent of storage. Choose and record
   one boring supported DOCX/PDF strategy for this repository; callers supply retained template
   bytes plus validated merge values and receive validated output bytes/content metadata.
2. Accept a genuine DOCX package rather than a UTF-8 text file merely named `.docx`. Preserve its
   package structure and non-placeholder content for Word output. Support declared placeholders
   across ordinary Word runs or fail at template approval/generation with a precise validation
   error; never silently emit an unmerged placeholder.
3. PDF output must be structurally parseable, contain the merged authoritative text, handle Indian
   currency and Unicode borrower/legal text, and use bounded line/page behavior suitable for a
   retained legal record. A PDF header/file name alone is not acceptance.
4. Bound archive entry count, expanded bytes, XML/text size, placeholder count, replacement size,
   and output size so a compressed or pathological template fails before persistent output. Use
   replacement functions that cannot interpret borrower text as regex backreferences or markup.
5. Tests must use a genuine retained DOCX fixture with formatting/non-placeholder content and
   extract/assert both generated DOCX and PDF content. Keep checksum/size verification, output
   cleanup on failure, safe names, exact replay, and metadata-only list behavior.
6. Do not fabricate the currently absent governed numeric rate, repayment-date, penal-rate, or
   dispute-clause source. Prove that a real M05 decision with missing required terms returns the
   explicit zero-write configuration/field blocker; separately test the renderer with an exact
   frozen sanctioned fixture. A future source-governance owner, not this renderer, closes the full
   13-field production Term Sheet.

## Dependency / Adapter Impact

Any renderer dependency must be pinned, within the Ralph dependency limit, and isolated behind the
renderer interface. No external/network conversion service is permitted.

## Test Cases

- Genuine multi-run DOCX placeholders, formatting, tables/header/footer content where supported,
  Unicode/₹/ampersand/backslash values, and missing/duplicate/undeclared placeholders.
- Extractable PDF and DOCX outputs contain exact frozen facts and retained template text; malformed
  or empty output is rejected before storage metadata/evidence.
- Zip-bomb/oversized-entry/pathological placeholder inputs fail bounded and zero-write.
- Real M05-generated nullable terms block a full Term Sheet honestly; direct fixture population may
  test renderer capability but cannot be labelled an end-to-end M05/M06 tracer.
- Existing permission/object/replay/PostgreSQL behavior remains green after the adapter change.

## Evidence Required

Backend RED/GREEN output, genuine input/output artifact samples inside the run evidence folder,
content-extraction assertions, bounded-input matrix, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Stored Word/PDF outputs are genuine, readable products of the retained approved template.
- Malformed/pathological templates cannot create output or evidence.
- Tests no longer claim metadata-only PDF creation proves rendered legal content.
- All configured gates pass.

