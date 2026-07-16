# Execution Plan

Selected slice: `008M5-documentation-durable-actions-and-blocker-closure`

1. Reproduce the architecture-review failures and inspect the existing staff-workspace legal,
   checklist, security, API, and frontend seams without changing production code.
2. Add failing backend tests through public owner/HTTP interfaces for immutable signed-copy
   succession, correction/return/condition durability and replay protection, downstream blocking,
   role/object nondisclosure, and the A-125 governed-attorney blocker. Save red output.
3. Introduce legal-owner persistence and explicit decision/execute interfaces, including one
   migration at most, immutable action/audit/workflow/version identities, stable opaque action
   identities, and current projections consumed by checklist completion and ordered approvals.
4. Extend the security owner with an injectable governed-attorney decision seam that is blocked in
   production under A-125, projects `governed_attorney_unconfigured`, and creates nothing when the
   decision is absent or stale.
5. Update the shallow workspace coordinator/API projection so checklist, Document Pack, blockers,
   timeline, and independent sibling actions refetch the owner truth; preserve redaction,
   pagination, download behavior, and the fixed prototype composition.
6. Add/update focused frontend tests and the declared real-Django Playwright flow for upload,
   re-upload, correction, blocker display, persisted refetch state, and all five screenshot names.
7. Run focused green backend tests with the mandated Ralph interpreter, frontend tests,
   typecheck, lint, build, backend check, and migration sync. Collect browser tests/screenshots only
   if Chromium is available; otherwise preserve collection evidence for the orchestrator contract.
8. Review against the slice/source contract, verify diff limits and protected paths, sharpen the
   next one or two Not Started slices using only opened source/digests, and complete Ralph evidence,
   risk, review, API-contract, state, progress, handoff, slice-status, changed-file, and summary
   artifacts. Do not stage, commit, or push.
