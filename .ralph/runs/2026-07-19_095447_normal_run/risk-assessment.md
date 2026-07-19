# Risk Assessment

Risk level: High

- Selected slice: 009L3-epic-009-authority-evidence-and-pagination-closure
- Mode: normal_run
- Standing approval: confirmed; the owner veto list contains no revoked entry for this slice.

## Material risks and controls

- Financial/data-integrity risk: an unsupported SAP `posted` label could previously masquerade as
  provider success. Migration 0009 now permits only the singular `pending` obligation shape, and
  service coherence plus transfer race assertions enforce the same state.
- Authorisation/nondisclosure risk: workspace projection could be wider than the mutation owner.
  SAP candidate scope now follows the public Credit Manager create domain and CFC admission/actions
  reuse the governed Critical-authority predicate.
- Evidence risk: account reads previously reconstructed weaker SAP truth. They now use the full
  completion/send/Annexure-I decision and serialize only its masked value. The nested integration
  fixture retains its encrypted workbook storage so this is tested without weakening evidence.
- Pagination risk: database role/relationship/state filters run before canonical evidence
  evaluation, and only canonically projected rows contribute to totals/pages. Exact validation
  currently evaluates the database-prefiltered candidate set before slicing; this preserves
  nondisclosure and stable pages but remains the principal portfolio-scale performance risk for
  independent query-ceiling validation.
- UI risk: the approved Tabs component and existing classes restore the S42 shell; all Epic 010
  bodies remain explicitly unavailable and fixture-free in production code.

## Independent acceptance still required

- The exact two-test PostgreSQL class collected locally but skipped on SQLite; Ralph must execute it
  twice on PostgreSQL.
- The exact Playwright spec collected successfully. A local full run could not launch Chromium in
  the coding sandbox (`Target page, context or browser has been closed`); Ralph's two outside-sandbox
  executions decide browser acceptance and produce the declared screenshots.
