# Risk Assessment

Risk level: Medium

- Selected slice: 011PE-grievance-audit-archive-frontend-wiring
- Mode: normal_run
- Change shape: frontend pages, shared frontend transport/auth mapping, unit/component tests, and
  the inherited Epic 011 browser contract. No backend, schema, dependency, or protected-file
  changes were made.
- Authorization risk: `closure.archive.read` now maps to the existing `view_audit` navigation
  permission so a real Company Secretary or compliance role can reach the read-only archive
  surface. Archive creation remains separately governed by `closure.archive.create` /
  `manage_closure`. Focused auth tests cover the mapping.
- Mutation risk: grievance resolution is available only when the canonical row action allows it,
  requires status and reason, posts to the governed endpoint, and refetches canonical state before
  success. The archive surface exposes no mutation control.
- Audit risk: manifest generation occurs only after the canonical audited archive-detail request
  succeeds; the browser receives a locally generated JSON file from that returned projection.
- Regression risk: the two pages retain the established prototype shells and shared components.
  Mock data and inline business fixtures were removed from all five Epic 011 owners.
- Validation risk: deterministic focused/full frontend gates and cheap backend consistency checks
  pass. System Chrome aborted before page creation in both local browser attempts, so no browser
  assertion or screenshot was fabricated. Trusted validation must run the exact S53-S68 spec twice
  and retain all five named screenshots before final acceptance.
- Diff limits: nine product/test files, 1,788 changed product/test lines including the two new test
  files; within the 30-file / 2,000-line limits.
- Manual review required: yes, specifically trusted browser validation and its screenshot review.
