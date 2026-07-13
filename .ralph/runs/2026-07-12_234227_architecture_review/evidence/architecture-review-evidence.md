# Architecture Review Evidence

## Boundary

- Previous successful architecture review: `099e2a675934d5b91ce3c9e4e5cc872d4dc133d5`
- Reviewed range: `git diff 099e2a6...HEAD`
- Reviewed commits: `b9f5d9b` (006X8), `c6ae9bf` (006Y12), `7daaa61` (006Y13),
  `b76936f` (006Z5).
- The comparison was non-empty. Production code was read only.

## Independent Axes

Standards review checked codebase-design §§22.1, 26.1-26.3, 27.1, 42.1-42.3; auth §§3-3.1;
API/error conventions; transactional integrity; frontend design rules; and public-interface test
quality. Spec review checked all four slice files, Epic 004/006 digests, source data-model §§10.2-
11.6/34, auth §§12.2/25.1/34.2, BR-003..007, and M02-FR-001/004/005/006/012.

## Reproducible Observations

1. `ActiveMemberStatusModule.verify` locks Member but reads unlocked supply/service evidence before
   persisting the effective snapshot. Its PostgreSQL test races two verifiers only.
2. Witness PATCH resolves a missing parent application to `404` before authority, while an existing
   out-of-scope parent reaches `403`; the 006Y12 test varies only child witness IDs.
3. Active status directly calls the low-level object evaluator with a role policy different from
   `MemberRegistry._member_access`.
4. Running only
   `test_credit_action_parity_matrix.ZExecutedObjectScopeLedgerTests.test_zz_executed_ledger_equals_all_eight_public_actions`
   fails because its module-global ledger is populated by other tests.
5. BR-006 service evidence is an existence predicate; its dated recipient/reference/verifier facts
   are absent from `ActiveMemberStatusResult`, `result_id`, and the stored effective snapshot.
6. A later verification always sets the prior `effective_to = as_of_date - 1` with no chronological
   guard, so a backdated result can close a record before its `effective_from`.

## Queue Reconciliation

- Added executable High-risk correctives 006X9, 006Y14, and 006Z6 with real dependencies.
- Changed 006Z2 dependency from 006Z5 to 006Z6.
- No `Blocked` entries exist in `.ralph/state.json`; none required reopening.
- `docs/working/CONTEXT.md` remains accurate; no ADR is necessary because existing source documents
  already prescribe the architectural direction.

## Quality Gates

See `terminal-logs/quality-gates-summary.md` for commands and results from this worktree. Independent
orchestrator validation remains authoritative.
