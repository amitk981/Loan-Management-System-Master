# Ralph Handoff

## Last Run
2026-07-10_190455_architecture_review

## Current Status

Architecture review completed for product slices `006D2C`, `006E2`, `006F`, and `006F2` since
review commit `d29f697`.

- High provenance finding: 006E2 migration 0003 labels legacy rows verified when it finds no later
  audit, but does not require positive pre-appraisal success audits for both prerequisite IDs.
  Corrective 006E3 downgrades unproven rows and retains explicit revalidation.
- High authority finding: review enforces `credit.appraisal.review` and generic object access but
  not the source's actual Credit Manager role rule. A permissioned non-Credit-Manager owner can
  review. 006E3 adds the missing negative authority regression and role gate.
- High history finding: returned `review_comments` are overwritten by the next review, while
  metadata-only audit intentionally excludes them. ADR-0004 and 006E3 add immutable appraisal-owned
  decision history and keep the existing appraisal fields as latest projections.
- High acceptance finding: 006D2C was merged without executing its mandatory PostgreSQL concurrency
  tests; committed evidence contains a missing-driver failure and two SQLite skips. The driver is
  now installed, but this sandbox has no reachable server and cannot initialise one because shared
  memory is denied.
- Architecture finding: rejected review locks appraisal before the rejection-note seam locks the
  application, inverse to draft create/update. Corrective 006F3 normalizes application → appraisal
  → rejection/history lock order and requires real PostgreSQL outcome tests with zero skips.
- No material scope creep was found. Most frozen-snapshot, authority-denial, state, redaction,
  uniqueness, and rollback tests contain substantive assertions. No production code changed.

## Validation

Django check and migration sync passed. The full default backend suite ran 361 tests successfully
with the two explicit PostgreSQL-only skips; coverage is 95% (floor 85%). Frontend lint/typecheck,
107 tests, and build passed. Evidence is in
`.ralph/runs/2026-07-10_190455_architecture_review/`.

## Next Run

Run `006E3-appraisal-history-and-review-authority-hardening`, then
`006F3-appraisal-lock-order-and-postgresql-concurrency-closure`. 006F3 must not complete or merge
without executing both the existing loan-limit and new appraisal concurrency suites on PostgreSQL
with zero skips. After both corrections pass, run sharpened `006G-submit-to-sanction`; it must
consume verified frozen projections and immutable review history and must preserve rejected notes.
