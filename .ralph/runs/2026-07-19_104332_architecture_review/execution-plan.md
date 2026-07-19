# Execution Plan

Selected slice: `architecture-review`

1. Pin the previous successful architecture-review commit and enumerate only the product slices merged since that boundary.
2. Read the bounded active findings ledger, the reviewed slice specification, its Epic 009 digest section and cited source excerpts, plus the reviewed run's retained evidence.
3. Review the bounded diff independently along separate Standards and Spec axes, then inspect test assertions, edge cases, duplication, module boundaries, API/source-contract fidelity, Epic 009 requirement coverage, current context truth, and stale blocked-slice prerequisites.
4. Record findings newest-first in `docs/working/REVIEW_FINDINGS.md`. Create a dependency-valid numeric corrective slice only for an unmapped Critical/High root cause; otherwise map an existing actionable corrective or bundle Medium/Low observations per the runbook.
5. Save self-contained review evidence, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`; validate documentation scope and queue contracts without running unchanged product gates.

Constraints: no production-code changes, no protected-file edits, no source-document edits, and no orchestrator-owned state/progress/status bookkeeping.
