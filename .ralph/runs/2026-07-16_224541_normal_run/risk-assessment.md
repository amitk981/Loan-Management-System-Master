# Risk Assessment

Risk level: High

- Selected slice: `009B3C-sap-current-evidence-and-adapter-contract-closure`
- Mode: `normal_run`
- Financial/workflow impact: downstream loan and disbursement readiness consume this SAP decision.
  A false positive could release a code whose delivery or confirmation evidence was changed; this
  implementation therefore fails closed.
- Security/privacy impact: the affected routes can expose a masked customer code, a one-use
  capability, or a restricted workbook. All three now consume the same exact owner evidence and
  invalid evidence exposes none of them.
- Audit impact: send and completion audits now retain their actual old request status plus a sealed
  complete safe-body manifest. The manifest contains no customer code, Aadhaar, PAN, address, bank
  plaintext, workbook bytes, capability, or signed URL.
- Compatibility: schema, tables, migrations, routes, response shapes, error codes, encryption
  context, model aliases, and one-use capability semantics are unchanged. Existing pre-closure SAP
  rows without the complete sealed tuple become honestly non-current; no history is deleted or
  rewritten.
- Performance: current-decision reads now verify the restricted XLSX through its storage adapter and
  query singular ledgers. This adds bounded I/O in exchange for preventing label/checksum-only
  authorisation; 009D3 retains responsibility for its end-to-end query bound.
- Adapter risk: local instance replay state prevents a Future transport from being invoked twice in
  one adapter lifecycle, while the persisted request transaction remains the HTTP-level replay
  owner. No real SAP/email transport was introduced.
- Blast radius: four production/test Python files plus Ralph/docs bookkeeping; no frontend source,
  dependency, configuration, source document, or protected file changed.
- Validation: staged failing-first logs, 89 focused SAP tests green (three declared PostgreSQL-only
  races skipped under runtime capability `none`), Django check, migration sync, frontend lint,
  typecheck, 327 tests, and build are green.
- Residual gate: the orchestrator still owns authoritative complete backend coverage and commit.
