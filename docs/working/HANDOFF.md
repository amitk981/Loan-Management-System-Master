# Ralph Handoff

## Last Run
2026-07-11_020739_repair

## Current Status

006H2 hardened the real Appraisal Workbench request and reload contracts; repair corrected the
run-artifact template failure that prevented the prior gated attempt from completing.

- Appraisal responses are projected to the exact writable appraisal/risk allowlist before editing
  or PATCH; response IDs, snapshots, status, reviewer/history/TAT and case summaries cannot leak.
- Reload reads the 006G2 sanction case and retains its canonical UUID/status facts; submit consumes
  returned statuses and no longer mutates them locally.
- Controls intersect backend `/auth/me.available_actions` with permission/role/state usability;
  legacy revalidation uses its dedicated response action and update+risk authority.
- Credit calls reuse shared authenticated envelope handling with field errors, malformed-response
  detection, and one-call stale `409` behavior.

## Validation

All configured gates passed: Django check, migration sync, 387 backend tests with five expected
default-SQLite skips, 94% coverage (85% floor), frontend lint/typecheck, 130 tests, and build.
Focused red/green, exact request examples, and gate logs are under
`.ralph/runs/2026-07-11_020739_repair/`.

## Next Run

An architecture review remains due. Then run already-sharpened 006H3 before the `006X` two-role
tracer.
