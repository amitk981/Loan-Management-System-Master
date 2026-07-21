# Execution Plan

Selected slice: architecture-review

## Boundary

- Pin the previous successful architecture-review commit and review every completed slice merged
  after it: terminal corrective `CR-015-epic-010-terminal-servicing-owner-finalizer`,
  `010MB-interest-and-monitoring-frontend-wiring`, and `010N-global-search-api-and-ui`.
- Do not modify production code, protected files, orchestrator-owned state/progress, or historical
  run evidence.
- Use the Epic 010 digest, each reviewed slice, its retained run evidence, and only the cited source
  sections needed to assess fidelity.

## Review Work

1. Inventory each product commit and map changed code/tests/docs to the slice acceptance contract.
2. Run independent Standards and Spec reviews, then inspect test assertions, edge cases, mock
   removal, API/permission ownership, pagination, duplication, and architecture seams directly.
3. Execute bounded review probes or focused existing tests only where static inspection cannot
   establish correctness; retain self-contained logs under this run's `evidence/` directory.
4. Check active finding closures/recurrences, Epic 010 requirement coverage, `CONTEXT.md` accuracy,
   and stale `Blocked` prerequisites.
5. Prepend structured findings to `docs/working/REVIEW_FINDINGS.md` only when evidence supports them.
   Add one grouped corrective slice only for an actionable Critical/High root not already covered.
6. Write `risk-assessment.md`, `review-packet.md`, and `final-summary.md`; include exact convergence
   metrics and a bijective Finding Closure Manifest.

## Validation

- Verify the candidate diff is documentation/evidence-only and within permissions.
- Validate every new corrective candidate with Ralph's runtime-capability helper and PostgreSQL
  acceptance helper when applicable.
- Run queue/runtime validation relevant to any changed slice documents.
- Set the review packet Result exactly to `Ready for independent validation` only after the retained
  evidence, metrics, and manifest agree.
