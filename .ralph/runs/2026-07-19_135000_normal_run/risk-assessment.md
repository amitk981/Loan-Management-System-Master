# Risk Assessment

Risk level: High

- Selected slice: 009L6-epic-009-owner-selector-equivalence-and-matrix-closure
- Mode: normal_run
- Manual review required: yes; the orchestrator must run the authoritative full backend coverage
  and the declared PostgreSQL acceptance twice.

## Material risks and controls

- **Count/projection divergence:** the Loan Account, SAP send/completion, and pending-CFC database
  selectors now validate the same copied JSON body, canonical JSON text, and SHA-256 digest consumed
  by scalar owners. Synchronized mutation of both JSON copies is rejected when the independent
  canonical manifest remains unchanged. Focused regressions cover Loan, S37, and CFC stale-digest
  cases.
- **Database portability:** JSON key counts, structural equality, JSON scalar extraction, UUID
  normalization, and SHA-256 comparisons have separate SQLite/PostgreSQL SQL generation. The exact
  four-test PostgreSQL label passed locally; 119 impacted SQLite tests passed.
- **Shared PostgreSQL prerequisite:** fresh installation records whether `pgcrypto` predated this
  app. Reverse drops the extension only when that durable marker says this migration created it;
  an older applied migration without the marker reverses conservatively without dropping shared
  infrastructure.
- **Authority expansion:** Senior Finance actors with effective disbursement-initiation authority
  can now use the shared account candidate boundary without the unrelated Loan Account read
  permission or S37 assignment restriction. Exact lifecycle/SAP/readiness evidence remains required,
  and completion-only actors remain assignment-scoped.
- **Audit schema:** legacy audit rows receive blank canonical-manifest fields and are deliberately
  ineligible for these exact selectors until recreated through current owner writers; no historical
  audit body is backfilled or blessed.
- **Regression breadth:** existing 21/101 mixed-account, six-adjacent-drift, page-boundary,
  query-ceiling, authority, action, and 400/403/409 tests remain in the impacted labels. New tests
  add cross-owner body/manifest, related-delivery, task/workflow, and digest-drift coverage.

## Out of scope

- No frontend code or styling changed. Hosted nine-state browser/image-hash acceptance remains with
  CR-012 as declared by the slice.
- No Epic 010 behavior or SAP-posting confirmation authority was added.
