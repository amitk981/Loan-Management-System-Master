# Ralph Handoff

## Last Run

2026-07-13_232007_normal_run

## Current Status

007I is complete. The S21/S22/S24 Sanction Workbench now loads the actor-scoped approval-case queue
and frozen case detail through one typed authenticated service. It renders the ten review facts,
required and excluded approvers, immutable decisions, exception/conflict facts, General Meeting
scope, and terminal sanction decision without reading the live appraisal or either register.

Approval controls preserve the prototype's single decision-button/radio-modal composition. Only an
enabled case resource action intersected with `/auth/me` permissions is usable. Reject/return reasons
and server field errors remain in the modal; successful actions refetch the case and sanction truth.
Loading, empty, stale, denied, nondisclosing, gate, conflict, partial, terminal, and old/new-cycle
states have container coverage. CFO and Director assigned action behavior, Credit Manager read-only,
and unauthorized access are explicit regressions.

Evidence-required case detail now projects a backend-owned
`record_general_meeting_approval` action. The workbench uploads three exact-application legal files
when permitted, then submits their distinct ids through §25.11. It never treats metadata visibility
or a global permission as document-reference authority. A-090 records the missing documents-owned
selector for a recorder who must reuse previously uploaded referenceable files.

## Validation

Focused RED/GREEN evidence is retained. Frontend build/typecheck/lint and all 227 tests pass.
Backend check/migration sync and all 680 tests pass with 19 expected PostgreSQL-only SQLite skips;
coverage is 93% against the 85% floor. Playwright discovers the deterministic visual contract, but
the sandbox denies its localhost web-server process with `Operation not permitted`; the genuine
attempt log is retained and the orchestrator's declared external browser gate remains authoritative.

## Next Run

Run `007J-registers-and-approval-matrix-frontend-wiring`, following 007I's fail-closed resource
action pattern and the already sharpened scoped pagination/frozen-row requirements. Then run 007J2.
