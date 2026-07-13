# Execution Plan

Selected slice: architecture-review

1. Pin the review window at the previous successful architecture-review commit `c87586d` and
   inventory the four completed product slices, their repair commits, run packets, and changed
   production/test files. Exclude the protected orchestrator-only commit from product findings.
2. Read the four completed slice contracts, Epic 004/Epic 006 digests, cited source sections, and
   functional requirement IDs needed to evaluate fidelity; inspect tests for real assertions,
   boundary cases, and authoritative browser/PostgreSQL evidence.
3. Run independent Standards and Spec review agents against `git diff c87586d...HEAD`, then verify
   their findings directly in the repository and reconcile them without changing production code.
4. Check architecture drift, duplication, public-module ownership, API action/write parity,
   CONTEXT truth, every Blocked slice, functional-ID dispositions, and the next two queued slices.
5. Append newest-first findings to `docs/working/REVIEW_FINDINGS.md`; create or sharpen corrective
   slices for significant gaps and update the relevant digest/index/assumptions only when required.
6. Run configured backend/frontend gates plus review-specific protected-path, production-code,
   queue, state, JSON, and diff-limit checks. Save terminal evidence, changed-files, risk assessment,
   review packet, final summary, progress, state, and handoff for independent validation.
