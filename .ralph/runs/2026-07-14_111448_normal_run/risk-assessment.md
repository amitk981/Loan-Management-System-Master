# Risk Assessment

Risk level: High (standing owner approval; independent validation required)

- Selected slice: 008B3-document-renderer-and-output-proof-closure
- Mode: normal_run
- Handles retained legal-record content and borrower/sanction merge facts, so malformed output or
  silent placeholder retention would be consequential.
- Adds three pinned in-process dependencies: ReportLab 4.4.4, pypdf 6.1.1, and uharfbuzz 0.51.0.
  They remain behind one legal renderer interface and no network service is permitted.
- Requires a Unicode TrueType font. Missing font/dependency/configuration fails closed before
  storage; no fallback to fake PDF or lossy ASCII is allowed.
- ZIP-bomb/path traversal/oversize risks are bounded before archive extraction. XML/text,
  placeholder/replacement, output-byte, and PDF-page limits are explicit and test-covered.
- Persisted output is created only after DOCX/PDF structural/content validation. Persistence
  failure deletes stored bytes and transaction rollback removes metadata/evidence.
- M05 missing governed terms remain an explicit zero-write blocker; no rate, date, fee, penalty,
  or clause was invented.
- No schema migration, destructive data change, external communication, deployment, network
  conversion, commit, merge, or push was performed.
- Residual risk: PDF dependencies were unavailable in the offline agent venv, so independent
  orchestration must install pins and prove Unicode extraction/multi-page output before commit.
- Diff is within limits: 12 non-run changed files, three dependencies, no migration, and well below
  2,000 changed lines.
