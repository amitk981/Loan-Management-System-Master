# Risk Assessment

Risk level: High under the owner's standing approval.

- Selected slice: 008B3-document-renderer-and-output-proof-closure
- Mode: repair
- Demonstrated failure: shaped Unicode PDF content was validated with pypdf's plain extraction;
  Devanagari was split internally, and the selected primary macOS font lacked `₹`.
- Repair: retain HarfBuzz shaping, validate with pypdf layout extraction, and choose the first
  registered host font that covers every character in each retained text token. Missing coverage
  fails before persistence.
- Security/integrity posture: all source/archive/XML/text/placeholder/replacement/output/page
  bounds remain unchanged. Renderer failure remains zero-write; authority, exact replay, checksum,
  cleanup, safe names, metadata-only lists, A-101, and A-102 are unchanged.
- Dependency/data impact: no new dependency, migration, destructive data operation, network
  conversion, external communication, deployment, commit, merge, or push.
- Residual risk: production hosts must provide combined font coverage for retained legal text;
  A-103 records the fail-closed deployment requirement. Independent validation must rerun the full
  gates in the orchestrator environment before commit.
- Evidence: targeted RED/GREEN logs, the complete 736-test coverage log, and strictly reopened
  renderer-capability DOCX/PDF artifacts are under this run's `evidence/` directory.
