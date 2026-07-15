# Execution Plan — 007K Frozen Review Snapshot and Selector Boundary Closure

1. Add one public-boundary regression to `test_approval_case_routing_api.py` that corrupts only
   `appraisal_facts_json` while leaving the stored coherence/read projections true, then proves
   collection/detail/action/sanction-decision/Exception Register/Credit Sanction Register all
   nondisclose and create no ledger rows. Save the focused failing output as RED evidence.
2. Make the approval engine validate a non-empty, schema-complete, case-consistent frozen review
   snapshot without consulting the live appraisal. Remove the detail serializer's live fallback.
3. Make `approval_case_selector` a query-shaping-only module. Add one engine-owned public selector
   boundary that validates frozen truth and actor scope before caller filters/counts/pagination;
   move case, decision, and both register consumers to that boundary.
4. Add observable immutable-history and cycle-2 regressions plus a static import-boundary test.
   Replace brittle literal-SQL/query-count assertions encountered in this seam with bounded/public
   outcome assertions. Run each RED→GREEN tracer separately and retain terminal logs.
5. Inspect retained/migration fixtures for rows missing frozen review truth. Add at most one
   conservative data migration only if immutable historical evidence can prove the exact snapshot;
   otherwise keep such rows nondisclosing and document that remediation result.
6. Run focused approval tests, Django check, migration sync, the full backend coverage gate, and
   unchanged frontend build/typecheck/lint/tests. Save evidence and review artifacts.
7. Update the selected slice to Complete, state/progress/handoff, Epic 007 digest/API contract if
   the public boundary changes documentation, and sharpen the next one or two Not Started slices
   using only already-opened Epic 007 material.

Risk controls: fail closed before counts/pagination/serialization; do not trust stored Boolean or
reader indexes as authority; do not restore signals/model-save side effects; preserve atomic
zero-write denials; never backfill older cycles from later mutable appraisal state.
