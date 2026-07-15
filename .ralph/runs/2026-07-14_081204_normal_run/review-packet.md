# Review Packet: 2026-07-14_081204_normal_run

## Result
Success

## Slice
008A2-template-effective-integrity-and-file-reference-boundary

## Outcome

Template catalogue writes now serialize through a persistent identity even before the first row,
template files cross one provenance/permission boundary, and borrower-template ambiguity fails
closed. Catalogue reads are selector-owned and write modules no longer receive raw HTTP requests.
No generation endpoint, rendered document, or frontend behavior was added.

## Traceability

- Source data-model §16.2/§34 and slice requirement 1 say approved effective ranges must remain
  coherent under concurrent first versions. `DocumentTemplateIdentity` plus
  `_lock_identity` serializes the identity; PostgreSQL test
  `test_five_overlapping_first_versions_persist_one_winner_and_evidence_set` proves one of five
  overlapping requests persists one template/identity/audit/version-history set.
- Slice requirements 2/5 preserve immutable replay and exact §26.3 transport. Existing successor
  replay remains zero-write and the two-race suite passes twice; API/filter/pagination tests prove
  unchanged standard envelopes and bounded strict filters after extraction to `documents/selectors.py`.
- API §26.1-26.4, data-model §16.1, and requirements 3/4 require attributable safe file references.
  `documents.services.resolve_template_source_reference` validates the singular upload ledger,
  immutable metadata, global/template-source provenance, sensitivity, and exact permission.
  Public API tests cover valid reference plus missing/bare/corrupt/duplicate/application-owned/
  invalid-sensitivity/manage/download/reference-only failures with indistinguishable zero writes.
- Data-model §16.2 and digest V10 p.29 say Individual/FPO while the repository uses different member
  labels. `resolve_borrower_template_variant` maps only the unambiguous individual case and tests
  configuration-required failures for `fpc`, `producer_institution`, and unknown values.
- Codebase-design §§7.2/36.1 assign reads to selectors and forbid transport leakage into modules.
  The view now calls the selector and constructs immutable `RequestMetadata`; the write module has
  no request-helper import.

## Validation

- Backend: 710 tests pass with 21 expected skips; 93% coverage (85% required).
- Focused: 39 documents/catalogue tests pass; both PostgreSQL races pass twice.
- Django: system check and migration-drift check pass.
- Frontend: all 287 tests, typecheck, ESLint, and production build pass.
- Evidence: `.ralph/runs/2026-07-14_081204_normal_run/evidence/` including RED/GREEN logs,
  provenance matrix, PostgreSQL passes, coverage, and sanitized API examples.
- Scope: one additive migration, no dependency/frontend/protected/source change, within configured
  file/line limits.

## Recommended Next Action
Independent orchestrator validation/commit/merge/push, then run sharpened 008B.
