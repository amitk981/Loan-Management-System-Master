# Functional and Test-Quality Review

## Substantive implementation evidence

- 008B4 tests genuine DOCX/PDF outputs, stored checksums, current replay, legacy rows, selectors,
  ORM immutability paths, and unknown-parent authority ordering. The implementation binds new output
  to renderer contract + file UUID + checksum and excludes legacy rows honestly.
- 008C2 tests direct terminal bypass, canonical frozen facts, preservation/conflict matrices,
  verified cheque/subsidiary facts, read authority, separate applicability/linkage evidence, and a
  genuine five-worker final-sanction race run twice on PostgreSQL.
- 008D tests current-row replay/change/history, validation/evidence/role matrices, checklist
  preservation, and a genuine five-worker changed-submission race.
- 008E tests capture/replay, both mismatch evidence types, application-scoped current provenance,
  resolved-history immutability, checklist projection/rollback, and action-specific basic roles.

## Missing or misleading edges

- 008E protects an unresolved mismatch only from a different signer's normal signature. It never
  changes the same signer from mismatch to signed, which is the actual bypass.
- 008D tests Compliance denial for positive CS outcomes but never `insufficient`/`rejected`,
  preparer downgrade, multi-role same-user maker/checker, or verifier replacement.
- 008E declares concurrency but has no race test at all.
- 008D/008E fixtures manually assign renderer provenance to bare file rows. This isolates their
  rules but does not provide a public generation-to-verification tracer. 008F/008G now require one.
- Signature tests accept arbitrary nominee UUID/name pairs, so they do not prove that later PoA/
  tri-party consumers receive canonical application parties. 008E2 owns that fact interface.

## Functional requirement status

- M06-FR-001: substantive through 008C2 automatic terminal checklist creation.
- M06-FR-013: renderer/provenance mechanism substantive; real 13-term M05 path remains A-101 blocked.
- M06-FR-008/M06-FR-015: stamp/notary tracking exists, but authority correction and later PoA/Loan
  Agreement execution remain; not complete.
- M06-FR-016/M06-FR-017: mechanism exists, but mismatch authority/identity/nondisclosure/race gaps
  keep them partial until 008E2. A-107 remains an honest signed-copy evidence limitation.
- M06-FR-012/M06-FR-014: remain with later CDSL/final-approval slices; no false completion claim.

No epic completed in the review window. No ADR is required because existing source documents already
fix the disputed ownership, serializer, action-envelope, maker-checker, and nondisclosure decisions.
