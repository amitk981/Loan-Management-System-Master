# Execution Plan

Selected slice: architecture-review

## Boundary

- Run a documentation-only targeted corrective-closure review for Epic 009 generation 2.
- Review only the slice merged since the last successful architecture review (`009L7`), the active
  findings it claims to close, and its declared acceptance evidence.
- Do not modify production code, protected files, orchestrator-owned state/progress, or historical
  run evidence.

## Review Steps

1. Resolve the previous successful architecture-review fixed point and verify the bounded commit
   list and three-dot diff are non-empty.
2. Read the active portion of `docs/working/REVIEW_FINDINGS.md`, slice `009L7`, the Epic 009 digest
   shared invariants and `009L7` section, and the slice's own review/evidence artifacts.
3. Run independent Standards and Spec reviews over the same pinned diff, covering real test
   assertions and edge cases, source fidelity, duplication, and architecture drift.
4. Re-run only focused acceptance checks needed to verify the claimed closures; save terminal logs
   and a concise evidence index in this run folder.
5. Prepend the targeted closure result to `docs/working/REVIEW_FINDINGS.md`. Admit no further leaf
   corrective at generation 2; if a Critical/High recurrence remains, fail closed and recommend a
   root-boundary correction.
6. Verify Epic 009 functional-requirement traceability, stable repository context, and absence of
   stale `Blocked` slices without rescanning unaffected historical modules.
7. Complete `risk-assessment.md`, `review-packet.md` with exact convergence metrics and the required
   result, and `final-summary.md`; finish with a scoped diff/status audit.
