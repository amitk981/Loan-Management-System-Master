# Execution Plan

Selected slice: 007C2-approval-case-read-scope-and-snapshot-contract-closure

## Scope and permissions

- Change only the approval-owned backend read/enrichment seam, its public API tests, the contract
  ledger, Ralph evidence/state/handoff, the selected slice, and the next one or two queued slice
  files required by run-ahead sharpening.
- Do not add frontend behavior or styling, change database schema, query live approval
  configuration to reconstruct a historical route, or implement approval actions owned by 007D.
- Permitted edit roots were checked in `.ralph/permissions.json`: `sfpcl_credit/**`,
  `docs/working/**`, `docs/slices/**`, `.ralph/state.json`, `.ralph/progress.md`, and this run folder.
  Protected and forbidden paths remain untouched.

## Interface design

- Keep `approvals.modules.approval_case_engine` as the deep approval-owned module for routability,
  object access, list/detail reads, and canonical routed-case serialization.
- Compose the sanction-handoff enrichment response from that canonical serialization so §25.2,
  list, and detail cannot disagree about `current_status`, routing completeness, or frozen
  provenance.
- Treat the stored case snapshot as the complete authority. The interface denies unrelated actors
  by default and never rebuilds scope from live roles, matrix rows, committees, or user membership.

## TDD tracer bullets

1. RED → GREEN: add public list/detail permission-without-object-scope rows and acted-history rows;
   implement one approval-case object-access predicate applied before count/pagination and detail
   serialization, returning `403 OBJECT_ACCESS_DENIED` for direct scoped denial without writes.
2. RED → GREEN: add independently named contradictory-snapshot cases for arbitrary user injection,
   duplicate users, wrong role/count, amount/condition disagreement, and incomplete joint/register
   facts; deepen one coherent routability validator used by reads and action projection.
3. RED → GREEN: add exact enrichment replay rows for changed reviewed decision, assessment,
   application, exception, calculation rule, policy id/name, and calculation time; compare locked
   current credit provenance before returning an idempotent replay and preserve all ledgers on 409.
4. RED → GREEN: require §25.2 `current_status` and parity of the common routed snapshot across
   enrichment, list, and detail; consolidate/combine serializers behind the approval-owned module.
5. RED → GREEN: replace the manual governance fixture with submit → enrich → canonical read, then
   rejected/later-approved configuration proposals, asserting exact winner evidence and complete
   byte-for-byte case/public-projection immutability.

## Verification and evidence

- Save each failing and passing focused backend command under
  `evidence/terminal-logs/` using `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
- Run focused approval routing/submission/configuration tests, then backend check, migration sync,
  and the full coverage suite. Run frontend build, typecheck, lint, and vitest even though no
  frontend change is planned.
- Update `docs/working/API_CONTRACTS.md`, digest/assumptions only if needed, then produce
  changed-files, risk assessment, review packet, final summary, progress/state/handoff, slice
  completion, and run-ahead sharpening artifacts.
