# Execution Plan

Selected slice: architecture-review

Mode: architecture-review. No production code changes are allowed.

Review window:
- Derive the fixed point from the latest prior architecture-review commit/run.
- Review only the completed slices merged since that point. Ralph state and handoff indicate four slices:
  `005F2-deficiency-return-status-contract-hardening`, `005FA-member-portal-authentication`,
  `005FB-member-portal-dashboard-profile-and-supply-view`, and
  `005G-member-portal-application-start-status`.

Plan:
1. Confirm the exact fixed point with git history and verify the comparison diff is non-empty.
2. Read the four reviewed slice files, Epic 005 digest, working contracts, and only targeted source
   extracts already referenced by those slices/digests when needed for doc-fidelity checks.
3. Inspect product diffs, focused tests, and run evidence for:
   - real assertions and edge cases,
   - source-doc/API-contract fidelity,
   - object-scope and portal own-data boundaries,
   - duplicated service/API logic,
   - architecture drift from the modular-monolith/service-boundary direction.
4. Append newest-first findings to `docs/working/REVIEW_FINDINGS.md`.
5. Create or sharpen corrective slices for significant findings; otherwise sharpen the next one or two
   `Not Started` slices using already opened Epic 005 facts.
6. Update Ralph run artifacts: changed files, risk assessment, review packet, final summary, state,
   progress, handoff, and terminal-log evidence.
7. Run applicable docs/review validation checks and save output under this run folder.
