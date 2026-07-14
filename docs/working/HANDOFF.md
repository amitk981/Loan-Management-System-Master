# Ralph Handoff

## Last Run

2026-07-14_070825_normal_run

## Current Status

007R is complete. New review packages use `approval-review-v3`; exact pre-007O v2 packages remain
actor-scoped/readable but cannot approve/reject until the existing return -> correction -> fresh
independent review -> new-cycle path produces complete v3 facts. Unknown/malformed current schemas
remain nondisclosing and every denied terminal attempt is zero-write with canonical permission,
assignment, and optimistic-version precedence.

Legacy approved/rejected Credit Sanction Register rows now serialize missing source, terminal,
approver, and communication facts as explicit null/empty values without live reconstruction.
Original approver names come from routed immutable facts; replacement names come from an immutable
action-time field. Legacy unavailable names remain null and user ids remain attributable.

## Validation

Evidence is in `.ralph/runs/2026-07-14_070825_normal_run/evidence/`. Frontend build, typecheck,
lint, and all 269 tests pass. Django check/migration sync and all 707 backend tests pass with 20
expected PostgreSQL-only skips at 93% coverage. The 124-test approval suite and independent
standards/spec verification are green. This slice declares no browser or PostgreSQL runtime.

## Next Run

Run sharpened 007S next. Its selector/stale-response/register-pattern work must preserve v2
historical visibility, v3 malformed-package nondisclosure, remediation action availability, and
nullable legacy identity/register fields. Then run 008A2 before sharpened 008B; generation must
consume its race-safe effective selector, provenance-aware file reference, and explicit borrower-
variant resolver without treating metadata as generation/download authority.
