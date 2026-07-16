# Execution Plan

Selected slice: architecture-review

## Fixed Review Window

- Fixed point: `e1e3c665` (the previous successful architecture-review commit).
- Review diff: `git diff e1e3c665...HEAD`.
- Completed product/change-request slices in scope: `008K5`, `008L4`, `CR-008`, and `008M`.
- Production code is read-only for this run.

## Steps

1. Read the four slice specifications, their Epic 008 digest/source references, the prior findings
   they claim to close, and each commit diff/evidence packet.
2. Run independent parallel Standards and Spec reviews, then reproduce any suspected significant
   defect with focused read-only tests or probes where practical.
3. Check test quality, edge cases, source fidelity, functional-requirement coverage, duplication,
   module boundaries, repository context, and every blocked slice prerequisite.
4. Append a newest-first entry to `docs/working/REVIEW_FINDINGS.md`; create or sharpen corrective
   slices for significant findings, and record any durable architecture decision if one emerges.
5. Sharpen the next one or two `Not Started` slices using only already-opened Epic 009 material.
6. Run documentation/queue validation and proportionate existing quality gates, save self-contained
   evidence, and update state, progress, handoff, slice descriptor, changed-files, risk assessment,
   review packet, and final summary.

## Stop Conditions

Stop without production edits for a protected-path change, unsafe git state, a dependency-cycle or
dangling queue reference, a never-do action, repeated gate failure, or Ralph diff-limit breach.
