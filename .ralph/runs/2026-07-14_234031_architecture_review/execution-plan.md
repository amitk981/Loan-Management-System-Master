# Execution Plan

Selected slice: `architecture-review`

1. Establish the prior architecture-review commit and enumerate the four slice commits merged
   since it (008G2, 008F2, 008H, and 008I); confirm the review diff is non-empty.
2. Read each reviewed slice, its retained run evidence/review packet, and only the Epic 008 digest,
   maps, and cited source sections needed to verify the implementation contracts.
3. Run independent Standards and Spec reviews over the fixed diff, then locally inspect test
   assertions, edge cases, module boundaries, duplication, requirement-ID coverage, blocked-slice
   prerequisites, and `CONTEXT.md` fidelity.
4. Reproduce significant findings with focused read-only or test commands. Do not modify production
   code and do not fabricate browser evidence.
5. Append the newest review entry to `docs/working/REVIEW_FINDINGS.md`; create or sharpen executable
   corrective slices for significant issues, and sharpen the next one or two Not Started slices
   using only already-opened source material.
6. Run documentation/queue and relevant focused quality checks, save terminal evidence, and finish
   `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`.
7. Update `.ralph/state.json`, `.ralph/progress.md`, `docs/working/HANDOFF.md`, the architecture-review
   descriptor, and any truthful context/digest/assumption records required by the findings.
