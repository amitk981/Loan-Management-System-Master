# Execution Plan

Selected slice: architecture-review

1. Establish the last successful architecture-review fixed point and the exact Epic 009 closure
   commits merged after it. Confirm the comparison is non-empty and bounded to the active review
   lineage.
2. Read the bounded active findings, the owning closure/CR slice specifications, their Epic 009
   digest sections, and their declared run evidence. Do not rescan unaffected historical modules.
3. Run independent Standards and Spec reviews of the fixed diff in parallel, then independently
   inspect test assertions, source-contract fidelity, duplication, architecture boundaries, and
   whether active findings are genuinely closed.
4. Run only focused, non-mutating checks needed to substantiate review conclusions. Save commands
   and results under this run's `evidence/` directory; product code remains unchanged.
5. Prepend the bounded review outcome to `docs/working/REVIEW_FINDINGS.md`. Add at most one numeric
   corrective slice only if a new Critical/High root finding is not already owned; otherwise map it
   to one actionable existing slice. Bundle or record Medium/Low observations per policy.
6. Complete the risk assessment, review packet (including exact convergence metrics and the exact
   ready result), and final summary. Verify the candidate changes only review/evidence documentation
   permitted in architecture-review mode.
