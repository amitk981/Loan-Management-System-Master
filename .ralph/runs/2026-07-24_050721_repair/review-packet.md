# Review Packet: 2026-07-24_050721_repair

## Result
Ready for independent validation

## Slice
012B-register-exports

## Repair Outcome

The independent backend lane's only failure is repaired. The report export module no longer embeds
the retired `PERMISSION_DENIED` production value; denied-request audit metadata and permission
failure classification now reuse the canonical shared `FORBIDDEN` constant.

The same-worktree candidate is otherwise preserved.

## Root Cause

The initial slice's focused tests did not include the repository-wide AST contract harness, so two
new permission-code literals passed local behavior tests but failed the authoritative coverage
lane's API-contract regression.

The existing contract harness was the correct regression seam. It was reproduced red before editing
and rerun green after the minimal repair.

## Validation Evidence

- Exact failed harness: reproduced 1 failing test, then 1 passing test
  (`evidence/terminal-logs/01-api-contract-harness-red.txt`,
  `evidence/terminal-logs/02-api-contract-harness-green.txt`).
- Focused report-export behavior: 8 tests passed
  (`evidence/terminal-logs/03-report-exports-focused.txt`).
- Django system check: no issues (`evidence/terminal-logs/04-django-check.txt`).
- Migration sync: no changes detected (`evidence/terminal-logs/05-migrations-check.txt`).
- Scope/cleanup and whitespace check:
  `evidence/terminal-logs/06-scope-and-cleanup-check.txt`.
- Self-contained repair narrative: `evidence/permission-contract-repair.md`.

## Traceability

The repository contract requires production permission denials to use the canonical public
`FORBIDDEN` code. The report export module now imports that shared constant and uses it for both
denial audit metadata and permission-related worker failure classification. The exact
`test_production_code_does_not_use_legacy_permission_denied_literal` test verifies the retired
literal cannot reappear.

In plain language: export permission failures now speak the same error vocabulary as the rest of
the public API, while all focused export behavior remains unchanged.

## Review Focus

- Confirm the independently rerun API contract harness remains green inside the authoritative
  complete backend lane.
- Confirm the preserved original candidate and this bounded repair pass protected-path, diff,
  PostgreSQL acceptance, and artifact validation.

## Recommended Next Action
Run Ralph independent validation and commit only if every selected gate passes.
