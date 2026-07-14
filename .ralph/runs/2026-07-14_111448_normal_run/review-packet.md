# Review Packet: 2026-07-14_111448_normal_run

## Result

Implementation complete; authoritative dependency-prepared validation pending

## Slice

008B3-document-renderer-and-output-proof-closure

## What Changed

- Added `legal_documents.modules.document_renderer`, a deep storage-independent interface for
  bounded genuine DOCX merging and validated local PDF construction.
- Removed the plain-text `.docx` fallback and hand-written PDF header/object implementation.
- Added three pinned rendering/parser/text-shaping dependencies and A-103's explicit limits/font
  configuration.
- Replaced fake fixtures with genuine formatted OPC packages containing tables, headers, footers,
  retained text, and placeholders split across Word runs.
- Added extracted-content, Unicode/₹/ampersand/backslash, multi-page, placeholder contract,
  bounded-input, API zero-write, and honest M05 blocker tests.
- Sharpened 008C/008D so later owners consume metadata without treating rendering as execution,
  stamp, notary, checklist, or approval evidence.

## Traceability

- The source says approved borrower-variant templates must generate readable Word/PDF legal
  records with authoritative facts (`functional-spec.md` §15.1, M06-FR-013/M06-FR-015;
  `api-contracts.md` §26.4-26.5). The code merges genuine retained Word packages and reopens every
  PDF before storage. Verified by
  `test_term_sheet_word_output_contains_all_thirteen_authoritative_facts`,
  `test_sanctioned_application_generates_retained_pdf_from_exact_template`, and
  `test_pdf_wraps_long_legal_text_across_bounded_pages`.
- The slice requires bounded pathological-input failure and no silent placeholder. The renderer
  enforces archive/XML/text/placeholder/replacement/output/page limits plus safe paths and exact
  placeholder cardinality. Verified by `test_renderer_rejects_every_bounded_input_class` and
  `test_word_placeholder_contract_rejects_duplicate_undeclared_and_missing_fields`, including
  API-level zero persistent output/evidence.
- A-101 says missing governed M05 terms must not be invented. The projection now treats an empty
  charges object as missing, and
  `test_m05_writer_nullable_terms_block_full_term_sheet_with_zero_writes` proves the five absent
  term classes block without loan-document/audit/workflow writes. Existing M05 test
  `test_final_joint_approval_creates_source_shaped_sanction_and_completion_evidence` proves the
  terminal writer produces that nullable shape.
- The architecture source places legal rendering behind the legal-documents owner. The foundation
  `documents` app has no renderer import; generation calls the renderer only after authority,
  template, application, sanction, replay, and source-byte validation.

## Evidence

- RED/GREEN and gate logs:
  `.ralph/runs/2026-07-14_111448_normal_run/evidence/terminal-logs/`
- Genuine input/rendered DOCX packages and extracted-content proof:
  `.ralph/runs/2026-07-14_111448_normal_run/evidence/artifacts/`
- Local gates: frontend build/typecheck/lint/293 tests green; Django check/migration sync green;
  dependency-free renderer tests green; backend coverage 92%.
- Honest local limitation: seven PDF-path tests could not run because newly pinned packages are
  absent from the offline venv. The orchestrator must install them and create final PDF proof.

## Recommended Next Action

Install the pinned backend requirements, run the focused legal-document tests and full backend
coverage gate, retain a parsed PDF artifact containing exact Unicode/₹ frozen text, render every
page to PNG with Poppler, and inspect margins/wrapping/header/footer/glyph legibility. Commit and
advance to sharpened 008C only if those independent gates pass; otherwise enter repair.
