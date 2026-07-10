# Review Packet: 2026-07-10_190455_architecture_review

## Result
Success — corrective slices required before sanction submission

## Fixed Point And Reviewed Set

- Fixed point: `d29f697a7da8e6d0425f35a5525ac1426fef54f5`
- Diff: `git diff d29f697...HEAD`
- Commits: `9dd5386` 006D2C, `d5753d1` 006E2, `2684996` 006F, `3f7f386` 006F2
- Spec sources: the four slice files, Epic 006/digest, functional §9.8/M04-FR-008-011,
  API §3/§21.3/§24, data-model §14/§34, auth §19.2/§25.3/§34.4, and appraisal tests.
- Standards sources: AGENTS/Decision Policy plus codebase-design §12/§22/§26, API §3, and
  data-model §34.

## Standards

1. **Hard — unsafe legacy snapshot verification.** 006E2 permits a legacy copy only when audit
   chronology proves it, but migration 0003 merely checks that no later audit exists before marking
   `verified` (`credit/migrations/0003_appraisal_prerequisite_snapshots.py:101-125`). Its positive
   fixture contains no prerequisite success audit (`tests/test_appraisal_api.py:1724-1752,
   1850-1857`). Absence of audit is not historical proof.
2. **Hard — required concurrency proof never passed.** Financial modules require concurrency tests;
   006D2C explicitly requires PostgreSQL and rejects SQLite skips. Saved PostgreSQL evidence stops
   at missing `psycopg`, SQLite skips both cases, and the packet says not to merge without a pass,
   but the slice is Complete and merged.
3. **Judgment — inverse lock order.** Draft mutation locks application then appraisal
   (`appraisal_workflow.py:80-95`); rejected review locks appraisal then the rejection-note module
   locks application (`appraisal_workflow.py:556-612`; `applications/services.py:976-984`). A
   concurrent stale PATCH/reject can deadlock.
4. **Judgment — transport-shaped interface growth.** `AppraisalWorkflow.review` accepts extracted
   values plus raw `payload_fields`, and the view passes the same HTTP body twice. A typed domain
   review input would keep conditional rejection fields and unknown-field validation local without
   making request mechanics part of the module interface. This is watched within 006E3 rather than
   forcing a separate refactor.

## Spec

1. **High — missing PostgreSQL acceptance proof.** The authoritative 006D2C test class is skipped
   off PostgreSQL (`tests/test_credit_modules.py:887-901`); committed evidence contains two skips and
   no executed PostgreSQL case despite the slice's no-merge condition.
2. **High — Credit Manager role is not enforced.** Source auth §25.3 says the user must be Credit
   Manager. Review checks the permission plus generic application access
   (`appraisal_workflow.py:530-575`); generic access permits a non-Credit-Manager owner with that
   permission (`identity/modules/object_permissions.py:39-54`). The test matrix omits this actor.
3. **High — returned-review history is overwritten.** 006F requires retention of the return reason.
   The model has only latest comments/decision, each later review overwrites them
   (`appraisal_workflow.py:622-633`), and metadata-only audit omits the text. The resubmit/re-review
   test never verifies the original reason survives.
4. **Medium — legacy verification lacks positive chronology.** Migration 0003 treats no later audit
   as proof even when there is no prerequisite audit at all, contrary to 006E2's conservative
   legacy rule.

No material scope creep was found.

Summary: Standards found 2 hard violations and 2 judgment calls; worst is unproven legacy decision
provenance. Spec found 4 gaps; worst issues are missing Credit-Manager-only authority and lost review
history (alongside the unexecuted mandatory PostgreSQL acceptance condition).

## Corrective Architecture

- Accepted `ADR-0004-append-only-appraisal-review-decisions`: immutable decision records retain
  review reasons; appraisal fields remain only the latest projection; audit references IDs without
  free-text leakage.
- Created High-risk `006E3-appraisal-history-and-review-authority-hardening`: positive prerequisite
  audit proof, conservative data repair, actual Credit Manager authority, append-only review history,
  and stale contract-summary reconciliation.
- Created High-risk `006F3-appraisal-lock-order-and-postgresql-concurrency-closure`: one application
  → appraisal → rejection/history lock order plus zero-skip PostgreSQL execution of existing loan-
  limit and new appraisal concurrency outcomes.
- `006G-submit-to-sanction` now depends on 006F3. No production code was changed in this review.

The codebase-design skill materially shaped the correction: historical complexity stays behind the
existing `AppraisalWorkflow` interface, with an immutable internal record instead of leaking review
history or concrete models to callers.

## Test Quality And Requirement IDs

Most tests are substantive: frozen same-UUID projections, strict validation, permission/object
denials, maker-checker, state transitions, rejection-note uniqueness, metadata redaction, and forced
rollback are asserted through public interfaces. The four gaps above are missing cases/proofs, not
coverage-padding complaints.

Epic 006 is not Complete. M04-FR-008/009 facts are implemented; M04-FR-010 remains partial until
006G enforces sanction gating; M04-FR-011 is reachable but requires 006E3/006F3 hardening.
M04-FR-001/002 are explicitly deferred to 012EA by A-053; M04-FR-003 uses the explicit A-054 TAT
anchor. No completed epic has uncovered unowned requirement IDs.

## Validation

- Backend check: pass.
- Migration sync: pass; no changes detected.
- Full default backend suite: 361 passed, 2 explicit PostgreSQL-only skips.
- Coverage: 95%, above the 85% floor.
- Frontend lint/typecheck: pass.
- Frontend tests: 107 passed across 16 files.
- Frontend build: pass; existing non-blocking bundle-size warning only.
- `git diff --check`: pass at the review checkpoint.

## PostgreSQL Diagnostic

`psycopg 3.3.4` is installed. `pg_isready` reports no server on localhost:5432. A sandbox-local
`initdb` attempt fails before cluster creation because System V shared-memory allocation is denied.
This is diagnostic evidence only, not acceptance; 006F3 must run on a provisioned PostgreSQL server.

## Recommended Next Action

Run 006E3, then 006F3. Do not run 006G until both are Complete and 006F3 records zero-skip
PostgreSQL results for loan-limit and appraisal concurrency.
