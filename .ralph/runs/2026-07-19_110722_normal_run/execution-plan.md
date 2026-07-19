# Execution Plan

Selected slice: 009L4-epic-009-canonical-read-and-bounded-pagination-closure

## Impact Boundary

- SAP owner: establish one public current-completion decision and make member/account consumers
  delegate to it, preserving fail-closed evidence coherence and masked output.
- Loan Account read owner: replace full-portfolio deep projection with one canonical eligibility
  selector whose count, ordering, and pagination operate on the same eligible identity set.
- Staff disbursement workspace: consume only the requested bounded account window plus a documented
  constant reconciliation window; do not walk all Loan Account pages or refetch rows one-by-one.
- Action projection: delegate each advertised workspace action to the exact public mutation-owner
  predicate so projection and unchanged-row mutation outcomes remain identical.
- Tests/evidence only beyond those product seams: add focused SAP reverse-consumer, 1/21/101 mixed
  pagination/query-ceiling, action parity, transport/error, and MP14 opposite-order coverage where
  the repository's existing test owners make those gaps executable.
- Excluded: Epic 010 servicing behavior, CR-012 hosted browser screenshots, new UI/styling, and any
  unsupported SAP posting-confirmation governance under A-135.

## Execution Steps

1. Read the bounded Epic 009/API/source contracts and inspect the existing SAP, Loan Account,
   readiness, workspace, mutation-authority, transport, and MP14 seams.
2. RED: copy the retained architecture-review SAP divergence probe into the owning test surface;
   add focused failing tests for exact eligible-set pagination/bounded queries and any demonstrably
   omitted action/transport/MP14 matrices. Save command output under `evidence/terminal-logs/`.
3. GREEN: implement the smallest deep-owner changes: canonical SAP decision, canonical eligible
   identity selector, bounded workspace composition, and mutation-owner action delegation.
4. Run focused reverse-consumer and regression labels with the mandated Ralph Python interpreter;
   save GREEN output, then run backend `check` and migration-sync checks. Run impacted frontend
   tests/typecheck/lint/build only if frontend files or contracts are touched.
5. Inspect targeted diffs and query behavior, perform the skill-directed independent review against
   this slice as the specification, and finish `risk-assessment.md`, `review-packet.md`, and
   `final-summary.md`. Leave commit, complete-suite coverage, state/status, and mechanical handoff
   bookkeeping to the Ralph orchestrator.

## Safety and Validation

- No protected/source path, dependency, migration, or frontend design change is planned.
- Backend/business changes follow test-first RED/GREEN with retained terminal evidence.
- Query ceilings must be stable for 1, 21, and 101 mixed rows and pages/totals must exclude denied
  or incoherent identities before pagination.
- Stop on a protected-path diff, owner-veto condition, repeated focused-gate failure, or slice-size
  limit breach; do not weaken or duplicate authoritative acceptance gates.
