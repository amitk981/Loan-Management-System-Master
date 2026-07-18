# Execution Plan

Selected slice: architecture-review

1. Pin the review boundary at the previous successful architecture-review commit `1be0a281` and
   inventory every product, test, migration, documentation, and Ralph-maintenance change through
   `HEAD` (`4a0c03ad`). The four product slices in scope are 009H3A, 009H3BA, 009H3BB, and 009G4.
2. Read each reviewed slice contract, its retained run packet/evidence summary, the Epic 009
   requirements digest, and only the cited source sections needed to verify communications
   ownership/idempotency and legal migration ownership. Identify the repository standards sources
   that apply to the diff.
3. Run isolated Standards and Spec reviews in parallel, then independently inspect the complete
   diff for real assertions and edge cases, requirement-ID coverage, duplication, dependency
   direction, architecture drift, CONTEXT accuracy, stale Blocked slices, and next-slice readiness.
4. Reproduce any suspected significant defect with read-only inspection and focused review probes
   or retained focused tests. Store commands and outputs under this run's `evidence/terminal-logs/`;
   do not modify production code or fabricate passing evidence.
5. Append a newest-first entry to `docs/working/REVIEW_FINDINGS.md`. For each significant confirmed
   issue, create or sharpen an executable dependency-correct corrective slice; record an ADR only
   if the sources do not already settle the decision. Refresh the Epic 009 digest and CONTEXT only
   where repository truth moved.
6. Recheck the next one or two Not Started slices, queue validity, protected paths, documentation-
   only scope, and artifact completeness. Update Ralph state/progress/handoff, changed-files,
   risk-assessment, review-packet, and final-summary for independent validation.

No production code, protected file, `docs/source/` file, dependency, or historical run evidence will
be modified. Product gates are intentionally left to Ralph's architecture-review docs-only lane.
