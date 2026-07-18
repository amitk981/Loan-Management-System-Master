# Execution Plan

Selected slice: architecture-review

1. Pin the prior-review boundary and the four completed product slices under review; exclude unrelated owner-maintenance changes from slice findings while noting any review-scope effect.
2. Read each reviewed slice specification, its Epic 009 digest sections, current active findings, and the documented architecture/API/frontend standards cited by the slices.
3. Run independent Standards and Spec review passes over the exact slice commits, while the primary review inspects assertions, edge cases, duplication, module boundaries, migrations, permissions, immutable evidence, and source-contract fidelity.
4. Execute focused retained tests and bounded review probes only where they materially validate or falsify review hypotheses; save all outputs under this run's evidence directory.
5. Classify and group findings by root owner. Close prior findings only with implementation and test evidence; add or map corrective slices only for new Critical/High findings.
6. Prepend the bounded findings ledger, re-check blocked-slice prerequisites and repository-context truth, then write the convergence metrics, risk assessment, review packet, and final summary.
7. Verify the documentation-only candidate scope, queue dependency contracts, required artifacts, and final diff without modifying production code or orchestrator-owned bookkeeping.
