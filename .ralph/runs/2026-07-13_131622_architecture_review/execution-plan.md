# Execution Plan

Selected slice: architecture-review

1. Pin the previous successful architecture-review commit and enumerate the four completed product
   slices merged afterward, excluding orchestrator evidence and the protected AGENTS.md maintenance
   commit from product findings.
2. Read each completed slice, its Epic 006/007 digest, cited source sections, retained run packets,
   and focused evidence; inspect the corresponding production and test hunks.
3. Run independent Standards and Spec reviews in parallel, then reconcile both against direct code,
   test, evidence, and functional-requirement spot checks without modifying production code.
4. Record significant findings newest-first in REVIEW_FINDINGS.md; create or sharpen executable
   corrective slices only where a material gap remains. Re-check Context truth and Blocked slices.
5. Run documentation/queue/integrity and proportionate full quality gates, then save self-contained
   evidence, changed-files.txt, risk assessment, review packet, final summary, progress, state, and
   handoff updates for orchestrator validation.
