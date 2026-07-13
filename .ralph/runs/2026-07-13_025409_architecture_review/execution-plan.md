# Execution Plan

Selected slice: architecture-review

1. Pin the previous successful architecture-review commit and inventory the four merged product
   slices, their diffs, run evidence, cited source sections, and functional requirement IDs.
2. Run independent standards and specification reviews over `git diff c31ac79...HEAD`, including
   test quality, edge cases, duplication, module boundaries, API/auth contracts, and source fidelity.
3. Reconcile both review axes against retained evidence; inspect significant findings directly and
   create corrective slices only where the defect is material and not already owned.
4. Verify Epic 004/006 functional-requirement disposition, `CONTEXT.md` truthfulness, Blocked slice
   prerequisites, dependency integrity, and the next two Not Started slices (007A and 007B).
5. Append the newest review entry, refresh the relevant digest/state/progress/handoff, and complete
   the run evidence artifacts without modifying production code.
6. Run docs/queue validation plus proportionate frontend/backend regression gates, record outputs,
   changed files, risk, review packet, and final summary.
