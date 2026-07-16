# Execution Plan

Selected slice: architecture-review

1. Pin the review window at the previous successful architecture-review commit and enumerate every merged slice/change request through `HEAD`.
2. Read the completed slice specifications, accepted change requests, relevant epic digests, and documented architecture/frontend standards.
3. Run independent Standards and Spec review passes over `git diff 8dbefb17...HEAD`, covering test quality, edge cases, source fidelity, duplication, module direction, and architecture drift.
4. Verify functional-requirement traceability, repository context accuracy, blocked-slice prerequisites, and queue consistency.
5. Append newest-first findings to `docs/working/REVIEW_FINDINGS.md`; create or sharpen corrective slices only for significant actionable defects. Do not modify production code.
6. Run documentation/queue validation appropriate to architecture-review mode and save self-contained evidence, changed-files, risk assessment, review packet, final summary, state, progress, handoff, and architecture-review descriptor updates.
