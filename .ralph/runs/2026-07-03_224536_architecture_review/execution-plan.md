# Execution Plan

Selected slice: architecture-review

Mode: architecture-review. Production code must not be modified.

1. Pin the review window from prior architecture-review artifacts and git history.
2. Read the completed slice files, run packets, changed-file lists, and gate evidence for the slices in that window.
3. Inspect the relevant git diffs for source fidelity, test quality, duplication, architecture drift, and frontend design-rule compliance.
4. Use existing Epic 002 digest/source extracts first; open `docs/source/` only if the digest or slice references are insufficient to judge a finding.
5. Append newest-first findings to `docs/working/REVIEW_FINDINGS.md`; create or sharpen corrective slices for significant issues.
6. Sharpen the next 1-2 `Not Started` slices using only source context already opened or existing digests.
7. Run docs-only validation checks and full configured gates where feasible, saving output under this run folder.
8. Save `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, `final-summary.md`, update Ralph progress/state/handoff, and leave git commit/add/push to the orchestrator.
