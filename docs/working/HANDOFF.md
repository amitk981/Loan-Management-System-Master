# Ralph Handoff

## Last Run

2026-07-14_041501_normal_run

## Current Status

Slice 007O is complete. The routed credit review package now freezes member/application identity
and reviewed sanction terms. Final approval revalidates the locked canonical package and creates
the sanction decision and immutable Credit Sanction Register only from frozen facts. The register
retains the exact review package, so later application/member/appraisal/risk changes cannot alter
approved or rejected formal evidence. Malformed terminal truth is exact zero-write.

General Meeting availability and mutation now use the same public `approval_case_is_readable`
decision as detail/actions/registers while retaining legal-audience and document authority.
Migration 0018 adds the immutable register's `source_review_facts_json` field. No frontend behavior
changed. 007P and 007Q were sharpened with the newly explicit boundary/source ownership.

## Validation

Run evidence is in `.ralph/runs/2026-07-14_041501_normal_run/evidence/`. Backend RED/GREEN proves
approved/rejected between-routing mutation, malformed-package zero-write, and shared General
Meeting readability. Django check/migration sync and all 691 backend tests pass with 19 expected
PostgreSQL-only skips at 93% coverage. Frontend build/typecheck/lint and all 257 tests pass.

## Next Run

Run `007P-sanction-queue-pagination-and-read-boundary-closure`, then
`007Q-register-source-fields-and-visual-evidence-closure`. Only after those correctives, start
sharpened 008A/008B. Their concurrency requirements declare the required PostgreSQL five-race
capability; A-095 still owns the unresolved S72 active-versus-approved question.
