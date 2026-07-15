# Stored-byte and migration proof

## Current output

`test_new_outputs_bind_current_provenance_to_reopened_stored_checksum` generates both DOCX and PDF
through the public HTTP boundary. For each output it:

1. reads the retained bytes from the storage adapter path;
2. recomputes SHA-256 from those bytes;
3. proves the value equals both `DocumentFile.checksum_sha256` and the immutable
   `LoanDocument.renderer_validated_checksum_sha256`;
4. proves the frozen provenance document UUID equals the retained `DocumentFile` UUID; and
5. structurally reopens DOCX/PDF and extracts the authoritative borrower and loan amount text.

RED and GREEN output: `terminal-logs/03-current-provenance-red.txt` and
`terminal-logs/04-current-provenance-green.txt`. The final two-format replay/zero-write/selector
matrix is in `terminal-logs/24-docx-pdf-current-replay-selector.txt`.

## Retained legacy output

`test_renderer_provenance_migration_preserves_retained_row_as_legacy` migrates a retained executed,
verified, stamped, and notarised row from `legal_documents.0002` to `0003`. It proves application,
template, generated-file, and lifecycle identities survive byte-for-byte while all three new
provenance columns remain null. `test_legacy_unverified_row_conflicts_on_replay_and_is_labelled_in_list`
then proves such history cannot replay as current or fabricate bytes/audit/workflow evidence.

Focused migration and boundary output: `terminal-logs/11-focused-legal-document-suite.txt`.

## Checklist exclusion

The legacy selector tracer failed before the provenance predicate and passed after it was restricted
to the exact renderer contract/document/checksum binding. See
`terminal-logs/05-checklist-legacy-red.txt` and `terminal-logs/06-checklist-legacy-green.txt`.
