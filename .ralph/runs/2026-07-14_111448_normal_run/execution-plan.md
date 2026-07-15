# Execution Plan

Selected slice: 008B3-document-renderer-and-output-proof-closure

## Scope and interface

- Keep `legal_documents.modules.document_generation.generate` as the single authority and
  persistence interface used by direct and HTTP callers.
- Add a legal-documents-owned deep renderer module whose small interface accepts retained DOCX
  bytes, declared authoritative merge values, and an output format, then returns validated output
  bytes plus content metadata. Storage remains outside this renderer seam.
- Preserve `legal_documents.LoanDocument`, exact replay identity, metadata-only list responses,
  cleanup on persistence failure, safe names, and A-102's nullable-only loan-account constraint.

## Test-first tracer bullets

1. Replace the fake `.docx` fixture with a genuine OPC/DOCX package containing formatted retained
   text, a table, header/footer, and a placeholder split across runs. Add public generation tests
   that reopen output DOCX and extract exact retained and merged Unicode/currency/legal content.
2. Add public PDF generation proof that parses the stored PDF and extracts the same exact content;
   implement bounded pagination and a Unicode-capable embedded-font PDF adapter.
3. Add malformed/pathological input cases for archive entries, expanded bytes, XML/text,
   placeholders, replacement values, and output size. Assert precise validation and zero output,
   metadata, audit, or workflow writes.
4. Add undeclared/duplicate/unresolved placeholder cases and replacement characters that would be
   unsafe as regex backreferences or XML. Ensure no placeholder is silently retained.
5. Exercise the real M05 terminal writer with its honestly nullable governed terms and prove a
   full Term Sheet is configuration-blocked with zero writes; label the populated sanction row as
   renderer-capability-only evidence.

## Verification and closure

- Save every focused RED/GREEN command under
  `.ralph/runs/2026-07-14_111448_normal_run/evidence/terminal-logs/` and copy genuine input/output
  artifact samples plus extraction evidence into the run evidence folder.
- Run focused backend tests after each tracer, then Django check, migration sync, full backend
  coverage, and all configured frontend build/typecheck/lint/test gates with the mandated Python
  interpreter.
- Review dependency direction and changed-file/diff limits; update assumptions/digest only where
  this slice resolves or clarifies them.
- Sharpen the next one or two Not Started slices from already-open Epic 008 material, then write
  changed-files, risk assessment, review packet, final summary, state, progress, handoff, and mark
  only 008B3 Complete.
