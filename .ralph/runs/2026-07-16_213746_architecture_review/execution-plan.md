# Execution Plan

Selected slice: architecture-review

Review range: `0d90bc19...HEAD` (the merge-base after the previous successful architecture review
through the current staging head). Product slices in scope are `008M5`, `009B3A`, `009B3B`, and
`009D2`; intervening Ralph-orchestrator commits will be identified separately and are not product
slice implementations.

1. Capture the commit list, per-slice changed files, diff statistics, and the prior-review baseline.
2. Run independent Standards and Spec reviews in parallel, using the four completed slice files,
   their Epic 008/009 digests, and documented architecture/API/data/permission rules.
3. Independently inspect test quality and execute focused read-only review probes where static
   evidence is insufficient; save commands and outputs under `evidence/terminal-logs/`.
4. Check source requirement IDs for the completed Epic 009 work, duplication/dependency direction,
   migration ownership, current-truth reconciliation, and `CONTEXT.md` accuracy. Re-check every
   blocked slice against `.ralph/state.json`.
5. Append verified findings newest-first to `docs/working/REVIEW_FINDINGS.md`. Create fully
   sharpened corrective slices for significant findings and adjust downstream dependencies without
   changing production code.
6. Sharpen the next one or two eligible `Not Started` slices using only already-opened Epic 009
   requirements, then validate slice-queue structure and documentation consistency.
7. Save `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, `final-summary.md`, and review
   evidence; update state, progress, handoff, architecture-review descriptor, and context if needed.
