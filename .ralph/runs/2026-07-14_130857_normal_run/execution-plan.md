# Execution Plan

Selected slice: `008B4-renderer-provenance-and-replay-contract-closure`

## Scope and invariants

- Add one nullable, non-destructive provenance group to retained `LoanDocument` rows: a versioned
  renderer contract plus snapshots of the validated `DocumentFile` identity and SHA-256 checksum.
  New successful generation writes the complete group atomically; pre-008B4 rows remain explicitly
  `legacy_unverified` and no file bytes or historical identity fields are rewritten.
- Define current renderer truth centrally in the legal-documents boundary. A row is current only
  when its contract version is supported and its provenance snapshots match its present stored-file
  identity and checksum. Generation replay conflicts on anything else; collection reads label the
  row `legacy_unverified`; checklist linkage selects current rows only.
- Preserve generation authority and validation ordering, exact replay zero-write behavior for a
  current row, renderer cleanup behavior, nullable-only loan-account integrity, and metadata-only
  responses. Authorized absent applications raise a dedicated not-found outcome mapped to the
  standard `404 NOT_FOUND`; denied/unrelated actors still fail first with 403.
- Keep A-101 explicit: provenance attests only to renderer validation and never to complete governed
  Term Sheet facts, execution, verification, stamping, notarisation, or checklist completion.

## TDD tracer bullets

1. RED -> GREEN: retained legacy DOCX/PDF rows conflict on exact replay, appear only as
   `legacy_unverified` metadata, and are excluded from checklist linkage with zero fabricated
   file/audit/workflow evidence.
2. RED -> GREEN: a newly generated genuine DOCX/PDF stores a complete current provenance binding;
   replay returns the same identity with zero writes, and tests reopen stored bytes and verify the
   checksum plus extracted content.
3. RED -> GREEN: tampered/mismatched provenance cannot satisfy replay or checklist selection, and
   provenance fields cannot be changed after creation while ordinary lifecycle fields remain
   updateable.
4. RED -> GREEN: authorized unknown application ids return 404 for generate/list while unauthorized
   and unrelated actors return nondisclosing 403 before parent existence or payload validation.

## Migration and contract work

- Create at most `legal_documents` migration `0003`, preserving all retained rows as nullable
  legacy data and enforcing all-or-none provenance population plus nullable-only loan-account
  integrity.
- Update the working API contract/digest only where the observable renderer-validation metadata and
  explicit conflict/not-found outcomes need recording; do not edit `docs/source/`.

## Verification and evidence

- Save every failing and passing focused backend command under
  `evidence/terminal-logs/` using `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
- Run focused generation/checklist tests during each vertical cycle, then Django check,
  migration-sync, full backend coverage, frontend build/typecheck/lint/tests, and queue/protected
  checks available through the repository gates.
- Save fresh/retained migration proof, sanitised API examples, stored-byte extraction/checksum proof,
  changed-files, risk assessment, review packet, final summary, and update the selected slice,
  state, progress, handoff, assumptions/digest as applicable.
- Before completion, sharpen the next one or two Not Started slices only from already-opened Epic
  008 sources, without changing their status.
