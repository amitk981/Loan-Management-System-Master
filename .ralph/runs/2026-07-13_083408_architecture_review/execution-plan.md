# Execution Plan

Selected slice: architecture-review

- [x] Read the required Ralph context in order, confirm permissions, and identify the selected
  architecture-review descriptor.
- [x] Pin the review window at architecture-review commit `8b1af41` through `HEAD`, enumerate the
  four completed slices, and retain the commit/diff inventory as evidence.
- [x] Read only those slice specs, their Epic 006/007 digests and cited source sections, plus the
  repository architecture/API/data standards needed to judge the changed hunks.
- [x] Inspect production and test diffs, retained RED/GREEN/PostgreSQL/CI evidence, functional-spec
  requirement coverage, duplication, and module-boundary drift; run independent Standards and Spec
  review agents as required by the review skill.
- [x] Append evidence-backed findings to `docs/working/REVIEW_FINDINGS.md`; create or sharpen
  dependency-valid corrective slices for significant issues and sharpen the next one or two
  `Not Started` slices from already-opened source material.
- [x] Reconcile stale `Blocked` slices and verify `CONTEXT.md`; update state, progress, and handoff.
- [x] Run the required frontend/backend/documentation gates and save self-contained terminal logs,
  `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`.
