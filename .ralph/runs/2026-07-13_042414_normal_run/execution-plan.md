# Execution Plan

Selected slice: 007A-approval-matrix-configuration

1. Confirm the source contract, existing configuration/audit/permission patterns, migration limits, and the approval module seam. Keep all threshold and condition authority in persisted approval-owned configuration.
2. Add one public resolver behavior test, run it RED with the mandated backend interpreter, and save the failure in `evidence/terminal-logs/`. Implement the smallest models/module behavior to make it GREEN, then repeat vertically for boundaries, condition authority, dates, invalid inputs, ambiguity, and historical projections.
3. Add API behavior tests one at a time for standard envelopes, list/create/supersede semantics, committee management, 401/403 permission denials, validation conflicts, audit/version-history evidence, and complete zero-write failures. Implement views/routes around the same module interface.
4. Add one non-destructive approvals migration with the source-backed three rules and one active committee derived from existing seeded CFO/director users. Verify migration sync and seed facts through public interfaces.
5. Update the API contract and focused epic digest, then run scoped tests, Django checks/migration sync, and the full configured backend/frontend quality gates. Save self-contained logs and API examples.
6. Review the diff against source requirements and Ralph limits; sharpen the next one or two eligible Not Started slices using only already-opened source material. Produce changed-files, risk, review, final summary, progress/state/handoff updates, and mark only 007A Complete after all gates pass.

Risk controls: no frontend or source/protected-file edits; no hard-coded routing thresholds; atomic mutation with consistent lock order; failed validation/permission/race paths must leave rules, committees, version history, and audit unchanged; no git add/commit/push.
