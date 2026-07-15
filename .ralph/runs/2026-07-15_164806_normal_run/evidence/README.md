# Evidence Index

## TDD timezone contract

- `terminal-logs/register-timezone-red.log`: `TZ=UTC` before implementation; S23 rendered `09:00`
  instead of `14:30` and S25 rendered `11:30` instead of `17:00` (2 expected failures).
- `terminal-logs/register-timezone-green-utc.log`: focused register suite under `TZ=UTC`, 8/8 pass.
- `terminal-logs/register-timezone-green-kolkata.log`: focused register suite under
  `TZ=Asia/Kolkata`, 8/8 pass with the same expected display values.

## Full gates

- `terminal-logs/frontend-lint.log`: pass.
- `terminal-logs/frontend-typecheck.log`: pass.
- `terminal-logs/frontend-tests.log`: 35 files, 304 tests, all pass.
- `terminal-logs/frontend-build.log`: pass.
- `terminal-logs/backend-check.log`: pass.
- `terminal-logs/backend-migrations.log`: no changes detected.
- `terminal-logs/backend-coverage.log`: 887 tests pass, 44 skipped, 92% total coverage against the
  85% floor.
- `terminal-logs/slice-queue-lint.log`: every slice parses and the pending dependency graph drains.
- `terminal-logs/final-sanity.log`: diff/capability/protected-path checks pass; its first queue-lint
  probe is superseded by the Bash-specific successful log above because the helper is not
  zsh-compatible.

No screenshot or browser contract is declared for this presentation-formatting CR.
