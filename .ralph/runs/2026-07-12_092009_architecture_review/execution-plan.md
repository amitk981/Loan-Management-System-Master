# Execution Plan

Selected slice: architecture-review

1. Pin the prior successful architecture-review commit and enumerate every product slice and repair
   commit merged afterward.
2. Read those slice contracts, run packets, epic digests, cited requirement extracts, and focused
   implementation/tests; inspect the complete merge-base diff for architecture drift, duplication,
   test quality, and source fidelity.
3. Perform independent Standards and Spec reviews, then reconcile both axes against functional
   requirement IDs, existing assumptions/ADRs, repository context, and blocked-slice state.
4. Append evidence-backed findings to `docs/working/REVIEW_FINDINGS.md`; create or sharpen only the
   corrective slices warranted by significant findings, and update durable/context/state records
   only where repository truth requires it. Do not modify production code.
5. Run documentation/queue and proportionate project quality gates, save terminal evidence,
   changed-files, risk assessment, review packet, final summary, progress, handoff, and review state.
