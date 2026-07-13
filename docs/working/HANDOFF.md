# Ralph Handoff

## Last Run

2026-07-14_023135_normal_run

## Current Status

`007L-sanction-workbench-contract-and-browser-closure` is complete. Credit now freezes borrower
name/type in the mandatory `approval-review-v2` package. The approval-owned case interface validates
that package and returns a complete S21 `workbench_summary`: frozen borrower/amount/authority/flags/
risk facts, submitted time, immutable partial-decision state, and an honestly labelled elapsed-
pending value with no invented target or breach. Missing legacy/partial packages remain hidden;
there is no live appraisal/member/configuration row repair and no migration/backfill.

The sanction client sends `approval_type=sanction` for every collection and adds
`current_status=pending&assigned_to_me=true` for the assigned queue. S22 separately renders every
immutable action actor, role, decision/abstention, comment, and acted-at confirmation. All decisions
still intersect server resource availability with `/auth/me` permission, preserve mandatory reasons,
one-call stale/conflict/meeting failures, canonical refetch, cycle isolation, and independent sanction
decision permission.

Authenticated JSON and multipart calls now share one frontend transport seam for stored sessions,
bearer headers, FormData construction, envelope parsing, and normalized errors. Sanction feature
code owns typed paths/payload fields only. Changed General Meeting evidence always uploads three new
application-scoped legal files; exposed case/register ids are not reused or labelled referenceable.

## Validation

RED/GREEN evidence is retained in
`.ralph/runs/2026-07-14_023135_normal_run/evidence/terminal-logs/`. Django check and migration sync
pass; all 686 backend tests pass with 19 expected PostgreSQL-only skips and 93% coverage. Frontend
build/typecheck/lint and all 253 tests pass. The named Playwright spec collects successfully. A real
local launch reached Django/Vite but Chromium hit the expected macOS Mach-port sandbox denial; no
screenshots were fabricated, and the orchestrator owns the two trusted browser runs.

## Next Run

Run `007M-exception-supporting-evidence-and-register-closure`, then
`007N-register-matrix-settings-contract-and-browser-closure`. Both were inspected and are already
concretely sharpened with fields, authority rules, exact browser specs, and screenshot contracts.
Do not close Epic 007 browser/fidelity evidence until both complete.
