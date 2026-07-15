# Slice 008B4: Renderer Provenance and Replay Contract Closure

## Status
Complete

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Depends On
- 008B3

## Runtime Capabilities

none

## Goal

Make genuine renderer validation an immutable property of every replayable/listable generated legal
document, so rows created before 008B3 cannot masquerade as validated DOCX/PDF output.

## Source / Review References

- `docs/source/codebase-design.md` §§14.1, 26.1-26.3, 27.1, 36.1-36.2, and 42.2
- `docs/source/api-contracts.md` §§6-8 and 26.4-26.5
- `docs/source/data-model.md` §§16.1-16.3 and 34
- `docs/source/functional-spec.md` §15.1 and M06-FR-013/M06-FR-015
- `docs/slices/008B3-document-renderer-and-output-proof-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-14_124337_architecture_review`

## Concrete Requirements

1. Persist immutable renderer-contract provenance for each newly successful `LoanDocument`, tied to
   the exact validated output file/checksum and a versioned legal renderer contract. Add at most one
   non-destructive migration and do not rewrite application/template/output identity or file bytes.
2. Treat retained rows without current renderer provenance as `legacy_unverified`. Exact replay must
   never return such a row as current validated success, and loan-document lists/checklist selectors
   must not describe it as renderer-validated. Return an explicit remediation conflict or create a
   governed successor through one documented path; never silently overwrite an executed, verified,
   signed, stamped, notarised, or checklist-linked record.
3. Prove current-provenance rows by the same stored-file identity/checksum written after 008B3
   structural and extracted-content validation. Metadata flags, extension, MIME type, `%PDF` prefix,
   or `generation_status=generated` alone are insufficient.
4. Preserve exact replay zero-write behavior for genuine current rows, output cleanup on every
   failure, A-102 nullable-only loan-account integrity, metadata-only list responses, and all direct/
   HTTP permission and application-scope decisions.
5. Align authorized unknown-application generation and list reads with the standard `404 NOT_FOUND`
   contract. Keep denied actors nondisclosing and prove validation/authority ordering without turning
   an absent parent into `400 VALIDATION_ERROR`.
6. Keep A-101 honest: provenance proves renderer output only and does not make the incomplete real
   M05 Term Sheet path source-complete.

## Test Cases

- A retained pre-provenance DOCX text blob and minimal legacy PDF cannot satisfy replay, list current-
  validation, or checklist-link selection; no new file/audit/workflow evidence is fabricated.
- A genuine current DOCX and PDF retain exact replay identity and are reopened through structural/
  extracted-content assertions tied to their stored checksum.
- Remediation rejects any legacy row with downstream execution/verification/stamp/notary/checklist
  evidence rather than overwriting it; safe remediation, if implemented, is attributable and atomic.
- Authorized unknown application ids return standard 404 for generate/list; unauthorized and
  unrelated actors remain 403 without an existence oracle.
- Existing renderer bounds, Unicode content, direct authority, fresh migration, and exact replay
  suites remain green.

## Evidence Required

Backend RED/GREEN logs, fresh/retained-row migration evidence, sanitised legacy/current API examples,
stored-byte extraction proof, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Only immutably provenance-bound genuine renderer output is accepted as current generated truth.
- Legacy rows fail or remediate explicitly without rewriting legal history.
- Unknown-parent errors and authority ordering follow the standard API contract.
- All configured gates pass.
