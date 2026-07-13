# Execution Plan

Selected slice: `007E2-conflict-authority-projection-and-scope-closure`

## Scope and permissions

- Work only in the active Ralph worktree and only on the selected approval/conflict slice.
- Permitted edits are limited to `sfpcl_credit/**`, `docs/working/**`, `docs/slices/**`,
  `.ralph/state.json`, `.ralph/progress.md`, and this run folder under `.ralph/runs/**`.
- Do not edit any protected path, `docs/source/**`, frontend visual code, or Ralph scripts/config.
- One approvals migration is allowed by the configured diff limits. No dependency is required.

## Module design

- Keep the external approval-case interfaces (enrich, list/detail, approve/reject/return/abstain)
  stable and put derived coherence/read authority behind one explicit approval-owned projection
  updater. The updater owns the coherent flag and exact actor index atomically.
- Remove cross-table workflow behavior from `ApprovalCase.save()` and make every production writer
  call the updater explicitly: case creation, workflow-event linkage, enrichment, action/abstention,
  appraisal-driven refresh, and migration backfill.
- Preserve `required_approvers_json` as immutable route provenance. Build one canonical public
  authority/action projection that attributes originals, effective replacements, exclusions, and
  immutable actions consistently across collection, detail, action responses, and old cycles.

## TDD tracer bullets

1. RED: reproduce the architecture-review distinct-authority defect for both excluded Director
   directions on a CFO + two-Director route. GREEN: allocate unique users to unique role slots and
   block atomically with the exact missing role and no sanction when cardinality cannot be met.
2. RED: prove a lower-route alternate is missing from canonical public history. GREEN: project the
   replacement mapping and action facts without mutating immutable route provenance; assert parity
   across collection, detail, action response, final readback, and returned-cycle history.
3. RED: prove an unused committee alternate leaks list count/read scope. GREEN: use an exact
   approval-owned actor projection before count/pagination and require attributable participation
   before COI-005 limited read.
4. RED: prove general-meeting classification misses related parties outside current approvers and
   whitespace reasons pass persistence/enrichment. GREEN: separate related-party detection from
   actual candidate exclusions and reject blank/whitespace declaration reasons.
5. RED: prove an ordinary model save causes hidden cross-table projection writes and/or a production
   writer can leave projection stale. GREEN: add the explicit updater plus deterministic migration
   backfill and exercise every writer through its public interface.

Each RED and GREEN command uses `/Users/amitkallapa/LMS/.ralph/venv/bin/python` and is retained under
`evidence/terminal-logs/`. Tests assert public response/status/count/action and immutable ledger
behavior rather than private helper calls except for the explicit projection module interface.

## Verification and handoff

- Run focused approvals tests after each tracer bullet, then Django check, migration sync, and the
  full backend coverage suite. Run the configured frontend build, typecheck, lint, and tests even
  though no frontend change is planned.
- Update `docs/working/API_CONTRACTS.md`, the Epic 007 digest, assumptions only if needed, slice
  status, state, progress, and handoff. Sharpen the next one or two Not Started slices using only
  already-opened source material.
- Save changed-files, exact test/gate evidence, focused response examples, migration proof, risk
  assessment, review packet, and final summary. Do not run git add/commit/push.
