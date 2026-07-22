# Execution Plan

Selected slice: architecture-review

1. Pin the review boundary at the previous successful architecture-review commit
   (`bbc8aa74`) and inspect the single subsequently completed product slice, 010N5
   (`92053395`), while excluding later Ralph-orchestration-only changes from the
   product critique.
2. Read 010N5's slice contract, product-run review packet, finding-closure evidence,
   and the bounded Epic 010 digest/source citations needed to verify the three
   inherited Finding ID/Root ID pairs.
3. Run independent Standards and Spec review passes as required by the review skill,
   then inspect the product diff directly for test quality, edge cases, duplication,
   owner-seam drift, and source-contract fidelity.
4. Replay the exact inherited review probes and the permanent closure tests using the
   mandated backend interpreter and frontend tooling. Retain self-contained logs under
   this run's `evidence/review-probes/` directory, with stable finding/root identities,
   positive signals, and explicit exit codes for every finding that can close.
5. Update `docs/working/REVIEW_FINDINGS.md` newest-first with one structured section
   for each inherited finding, preserving its stable identity and recording only
   evidence-supported Closed or Carried dispositions. Create no production changes.
6. If any inherited finding remains Carried, create exactly one compliant successor
   retaining the complete recurrence-repair contract; otherwise add no corrective.
   Record any genuinely new findings under their proper root and severity, applying
   Ralph's convergence rules.
7. Check Epic 010 requirement traceability, repository-context truth, and stale Blocked
   prerequisites; validate any new corrective slice's runtime contracts if one is
   created.
8. Complete `risk-assessment.md`, `review-packet.md` (including exact convergence
   metrics and Finding Closure Manifest), and `final-summary.md`; set the packet Result
   to exactly `Ready for independent validation` only after evidence and candidate
   scope checks pass.
