# Review Packet: 2026-07-13_122527_normal_run

## Result
Success

## Slice
007C2-approval-case-read-scope-and-snapshot-contract-closure

## Outcome

- Approval-case permission no longer grants global object scope; list counts are scoped before
  pagination and direct unrelated detail returns canonical nondisclosure.
- One approval-owned deep module validates complete immutable routing/credit coherence and exposes
  the predicates later action code must reuse.
- Enrichment/list/detail share one canonical routing serializer with `current_status`; replay is
  exact across reviewed decision and loan-limit policy provenance.
- The governed configuration test now uses a real enriched case and proves exact winner evidence,
  loser omission, and unchanged case/public projection.

## Traceability

- The source says Directors view assigned cases and unassigned cases are denied
  (`auth-permissions.md` §§15.9, 32.1, 37.3). The code applies `can_read_approval_case` before
  pagination/detail serialization; verified by
  `test_read_permission_without_snapshot_scope_cannot_list_or_retrieve_the_case` and
  `test_assigned_approver_can_retrieve_own_acted_history`.
- The source says approval matrix and decision facts are immutable snapshots
  (`api-contracts.md` §3; `data-model.md` §15.3). The code validates stored case/matrix/committee/
  approver/provenance coherence without live resolution; verified by the independently named
  contradiction rows in `test_approval_case_routing_api.py`.
- The source §25.2 response contains `current_status`. The canonical serializer supplies that field
  to enrichment/list/detail; verified by
  `test_enrichment_list_and_detail_share_the_canonical_routing_projection`.
- The slice requires identical frozen credit facts for replay. `_matches_enrichment` now compares
  the locked date, amount, application/assessment, exception, calculation rule, policy, and time;
  verified by the six named replay/no-write rows in `test_sanction_submission_api.py`.

## Evidence and gates

- Evidence index: `evidence/approval-case-contract.md`.
- Backend: Django check and migration sync clean; 585 tests pass, 16 expected PostgreSQL-only
  skips, 93% coverage.
- Frontend: build, typecheck, lint, and 208 tests pass.
- No protected paths, schema, dependencies, frontend files, or source documents changed.

## Recommended Next Action
Run `007D-approval-action-api-approve-reject-return` using the public coherent-route,
object-scope, and pending-actor predicates after locking.
