# Execution Plan

Selected slice: architecture-review

1. Pin the previous successful architecture-review commit and inspect the commits/diffs for
   006X9, 006Y14, 006Z6, and 006Z2 without changing production code.
2. Read each completed slice, its retained run evidence, the Epic 006 digest/spec references, and
   the repository standards relevant to the changed files.
3. Review independently along standards/architecture and source-spec/test-quality axes, including
   edge cases, duplication, module boundaries, functional-requirement disposition, context truth,
   and stale blocked slices.
4. Append evidence-backed findings newest-first to REVIEW_FINDINGS.md. Create or sharpen executable
   corrective slices for significant findings, and sharpen the next one or two Not Started slices
   using only source material already opened.
5. Run queue/document validation and proportionate project gates, save terminal evidence, then
   produce changed-files.txt, risk-assessment.md, review-packet.md, and final-summary.md.
6. Update Ralph state, progress, handoff, digest, and the architecture-review descriptor status as
   required for a completed review run.
