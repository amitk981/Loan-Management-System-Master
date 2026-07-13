# Execution Plan

Selected slice: 006Z11-member-scope-assignment-and-list-nondisclosure-closure

## Public behaviours

1. Persist explicit, action-specific member scope assignments (`global`, `team`, `assigned`,
   `created_by`) without deriving scope from permission or role provenance.
2. Filter the member directory by that authority predicate before search, count, and pagination;
   apply the identical predicate to detail, update, identity approval, active calculation,
   evidence maintenance, and verification.
3. Retain every service-evidence creator/material updater as immutable maker provenance and deny
   any such maker active-status verification without status/history/audit/workflow writes.
4. Document final permission/scope separation and equivalent list/detail nondisclosure.

## TDD sequence

1. RED: list/detail tests prove read permission is not global and pagination totals include only
   assigned/owned rows. GREEN: add the assignment model and shared authority query.
2. RED: action tests prove verify/identity permission without scope is denied and explicit
   action-specific assignment enables only that action. GREEN: route member actions through it.
3. RED: create/update/verify evidence test proves all prior makers remain ineligible and denial is
   zero-write. GREEN: persist immutable maker provenance and enforce it.
4. Run focused tests, migration sync, then all configured gates; retain terminal evidence and
   complete Ralph artifacts/state.

## Risk controls

High-risk authorization and maker-checker work: permission remains independent of scope, absent
assignment denies, no new business authority is seeded, filtering precedes counts, and only one
migration is introduced. Protected/source/frontend files remain untouched.
