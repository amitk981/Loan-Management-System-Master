# Execution Plan

Selected slice: 006X2-credit-action-predicate-and-container-closure

1. Inspect the existing eligibility, loan-limit, appraisal, sanction-handoff, and workbench seams and
   their public-boundary tests. Map each advertised six-field action to the exact corresponding
   write operation and preserve ADR-0005's approvals-owned sanction case boundary.
2. TDD the backend vertically: add one failing public-interface parity case at a time, save RED
   output, centralize the matching transition evaluation, then save GREEN output. Cover role,
   permission, object scope, state/provenance, immutable history, maker-checker, rejection facts,
   concurrent re-checks, and absence of success evidence on denial.
3. TDD the frontend default container: replace proxy/source assertions with Testing Library tests
   that mount `AppraisalWorkbench`, mock authenticated HTTP, select a real resource, exercise every
   named mutation, and assert exact request bodies/counts plus the canonical four-read refresh and
   one-call 400/403/409 behavior. Remove any remaining client-side workflow authority without
   changing the restored UI design.
4. Run focused backend/frontend tests throughout, then the complete configured backend and
   frontend quality gates. Preserve PostgreSQL race tests and run the package-aware dependency
   scan. Save self-contained terminal evidence and exact HTTP examples in the run folder.
5. Review the diff against the slice and source contracts, record changed files and risk, update
   API/working documentation only if the public contract changed, sharpen the next one or two
   Not Started slices from already-opened sources, and finish state/progress/handoff/slice status.

Permission check: intended edits are confined to `sfpcl_credit/**`, `sfpcl-lms/src/**`,
`docs/working/**`, `docs/slices/**`, `.ralph/state.json`, `.ralph/progress.md`, and this run folder;
all are allowed by `.ralph/permissions.json`. No protected or forbidden path will be modified.
