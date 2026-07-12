# Execution Plan

Selected slice: 006Y4-witness-correction-and-resource-action-closure

1. Add failing backend API tests for resource-owned witness read/create/update actions, optimistic
   correction, the mutable-field allowlist, immutable evidence, object access, permission,
   maker-checker separation, protected identity masking, and zero-write 400/403/409 outcomes.
2. Implement an application-owned witness module, the witness version/history persistence needed
   by the public contract, the exact `members.witness.update` permission, and list/detail/PATCH
   routes that share one action evaluation with the write predicates.
3. Add failing mounted Application Detail interaction tests for action-driven capture/correction,
   exact request bodies, canonical refetch, and disabled/absent-action denial; then minimally wire
   the existing witness card/form/alert/modal patterns to the resource envelope.
4. Extend the trusted-browser governance spec for capture, correction, stale, and denied states;
   collect locally where Chromium is unavailable and leave screenshot execution to Ralph's
   independent trusted-browser gate.
5. Update API contracts and the documented source-gap assumption, run the configured frontend and
   backend gates, save red/green and contract evidence, then complete Ralph run artifacts/state,
   handoff, progress, and slice status. Recheck the next two Not Started slices using only already
   opened Epic 004/006 extracts.

Permissions check: intended edits are limited to `sfpcl_credit/**`, `sfpcl-lms/src/**`,
`sfpcl-lms/e2e/**`, `docs/working/**`, `docs/slices/**`, `.ralph/state.json`, `.ralph/progress.md`,
and this run folder. Product and run paths are allowed by `.ralph/permissions.json`; no protected,
approval-required, forbidden, or `docs/source/**` path will be modified.
