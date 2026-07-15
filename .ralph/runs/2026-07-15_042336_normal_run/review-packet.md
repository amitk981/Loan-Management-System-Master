# Review Packet

## Outcome

Slice 008K2 is complete and ready for independent Ralph validation.

## Standards Review

The first independent pass found ordinary masking decrypting CDSL ciphertext, duplicated evidence
redaction keys, incomplete run artifacts, and regenerated local document files. Remediation added
explicit migrated CDSL last-four projections, removed `FieldEncryption.mask`, centralized recursive
redaction in `shared.masking`, completed the Ralph packet/state, and removed generated files. The
finance policy appears in checklist and coordinator owners because each must preserve the existing
dependency direction; both implement the same fail-closed state rule and are regression-tested.
The final independent Standards re-review passed with no hard blocker after confirming canonical
URL-safe Base64, artifact/state consistency, protected-path cleanliness, and final gate evidence.

## Spec Review

The first independent pass also requested explicit duplicate-hash/plaintext and broader PATCH
proof. The final tests cover stable same-field lookup hashes with random ciphertext, token/database/
evidence plaintext scans, migrated suffix reconciliation, one/several/explicit-null/empty/unknown/
immutable/cross-object/stale/invalid-terminal PATCH shapes, and genuinely partial concurrent
custody candidates. The re-review's remaining evidence requests were closed with all four nested
instrument reads before/after finance state and an existing member/bank owned by another real
application. Its custom-alphabet concern was resolved by canonical URL-safe Base64 and structural
metadata assertions. The final independent Spec re-review passed with no blocker. No UI or later
Epic 009 readiness behavior was added.

## Source / Code / Test Traceability

- Source data-model §§17.4-17.5 and 29-30 require encrypted BO/cheque fields and safe masked
  projection. Code writes opaque `field:v2`, migrates v1 with frozen reconciliation, stores CDSL
  last-four separately, and keeps cheque masking fixed. Tests: `FieldEncryptionTests`, CDSL legacy
  migration/reveal cases, and blank-cheque encrypted create/migration cases.
- Source API §§5.1, 6-8, 28.6 requires partial PATCH with complete-state validation and standard
  errors. Code parses a non-empty mutable subset, merges after `select_for_update`, then calls the
  full request/domain validator. Tests: blank-cheque partial, invalid-shape, stale-terminal, replay,
  and PostgreSQL changed-custody matrices.
- Source auth §§14.1 and 19.2-19.4 requires state-bounded finance readers. Code requires current
  `sanction_approved` for Senior Manager Finance and returns false for CFC until canonical readiness
  exists. Tests: package/nested/checklist before-after, permission-only, and CFC denials.
- Source codebase-design §§9.3-9.4, 28.1, 36.2, 39.1-39.2 requires central sensitive access and
  acyclic owners. Code separates masking/redaction/reveal, issues an unforgeable evidence adapter,
  and preserves top-level coordination. Tests: both-direction AST/fresh-import checks and forged
  package/PoA/SH-4/CDSL/cheque access rejection.

## Validation

- TDD: retained confidentiality, partial PATCH, and finance reader RED/GREEN logs.
- Focused: final expanded security contract suite green (42 tests; four PostgreSQL-only skips).
- PostgreSQL: 12 affected PoA/tri-party/SH-4/CDSL/blank-cheque race tests green twice.
- Backend: Django check and migration sync green; 859 tests green, 39 expected skips; 92% coverage.
- Frontend unchanged: lint, typecheck, 293 tests, and production build green.
- Plaintext scans: production source and generated evidence outputs green; agent transcript excluded
  because it necessarily quotes test fixtures.
- Diff: one migration, no dependency, 28 tracked files and 748 tracked changed lines before final
  artifacts; below configured 30-file/2,000-line limits. No protected/source file changed.

Evidence: `.ralph/runs/2026-07-15_042336_normal_run/evidence/`.
