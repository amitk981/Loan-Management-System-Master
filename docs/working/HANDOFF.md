# Ralph Handoff

## Last Run
2026-07-13_094017_normal_run

## Current Status

007C is complete. CFO/Director queue and detail reads expose only complete version-2-or-later 007B
snapshots. `assigned_to_me` uses the stored ordered required list, exclusions, pending case state,
and immutable action ledger; it never re-resolves or re-derives authority from current matrix or
committee rows. Global readers see routed detail without assignment-scoped actions.

Detail includes §44 approve/reject/return projections, stored rule/committee/policy provenance,
per-approver decision slots, and M05-FR-002 review facts read through from application/appraisal
owners. Version-1 shells, missing provenance, acted users, excluded users, makers without read
permission, and unrelated users are covered. The optional action signature UUID remains an
unenforced reference until the source signature-record aggregate lands (A-077).

## Validation

Evidence is under `.ralph/runs/2026-07-13_094017_normal_run/`. RED/GREEN logs cover absent queue/
detail routes, acted and closed assignment removal, and incomplete policy provenance. Thirteen
focused routing tests pass. Frontend build/typecheck/lint and 208 tests pass; backend check,
migration sync, and 566 tests pass with 16 expected PostgreSQL-only skips and 93% coverage.

## Next Run

Architecture review is due after four completed slices. Review through 007C before running the
already-sharpened `007D-approval-action-api-approve-reject-return`.
