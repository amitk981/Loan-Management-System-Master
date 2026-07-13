# Ralph Handoff

## Last Run
2026-07-13_171041_normal_run

## Current Status

007E2 closed the Critical duplicate-Director route and both High public-boundary regressions from
the preceding architecture review. Conflict replacement now fills exact frozen role slots with
distinct users; excluding either Director on a two-Director route closes the case as
`blocked_by_conflict` with the exact missing role and no sanction.

Canonical collection/detail/action/history reads preserve raw `route_approvers`, expose executable
`required_approvers` with `replacement_for_user_id`, and include every immutable
`approval_actions` row. The §25.2 enrichment response retains its backward-compatible raw required
approver shape. Unused committee alternates are absent from SQL counts and direct scope even when a
declaration exists.

Coherence and original/effective/acted reader synchronization moved out of `ApprovalCase.save()`
into one explicit approval-owned projection updater. Creation, workflow linkage, enrichment,
actions/abstention, appraisal refresh, and migration invoke that interface atomically. Migration
0013 backfills the exact reader set and rejects whitespace-only declaration reasons.

## Validation

Retained RED/GREEN logs cover duplicate identity, alternate-history omission, unused-alternate
count/scope disclosure, noncommittee general-meeting detection, whitespace reason validation, and
the hidden model-save projection seam. Public matrices cover both two-Director exclusion
directions and all source §17.1 declaration/maker classes. Migration acceptance proves unused
candidates are removed and effective replacements retained.

Frontend build/typecheck/lint and all 208 tests pass. Backend check and migration sync pass; the
full 651-test suite passes with 19 expected PostgreSQL-only SQLite skips and 93% coverage. One
initial full-suite failure exposed and repaired the §25.2 enrichment response compatibility issue;
the final full suite is green.

## Next Run

Run `007F-exception-approval-workflow` next. It now consumes the delivered canonical authority,
action, and exact-reader projections. Then run 007G in dependency order.
