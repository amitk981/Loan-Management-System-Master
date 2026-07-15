# Review Packet: 2026-07-13_205450_normal_run

## Result

Ready for independent validation

## Slice

`CR-004-member-governance-container-recurring-ci-timeout`

## Outcome

- The member-governance production-container suite has an explicit 15-second integration budget
  and sequential row execution.
- The global `npm test` command and Vitest's 5000 ms default remain unchanged for every other suite.
- A retained package command runs all 16 affected rows with one worker and file parallelism off.
- No production component, assertion, API, UI, dependency, or migration changed.

## Traceability

- The CR says mounted coverage must preserve authenticated App navigation, registration, the exact
  POST ledger, canonical profile refetch, response non-disclosure, and cleanup. The test body is
  byte-for-byte unchanged; verified by the named create-ledger journey in the focused and full-suite
  logs.
- The CR says integration-style tests must not inherit the 5000 ms unit ceiling and the timeout must
  not be raised globally. The suite declares `{ timeout: 15_000 }` while `vite.config.ts` and the
  canonical `test` script remain unchanged. The same `--testTimeout=1` command is RED before and
  GREEN after the suite-local policy.
- The CR asks for explicit CI contention behavior and a retained CI-shaped command. `package.json`
  provides `test:member-governance-container:ci` with one worker and file parallelism disabled;
  all 16 rows pass under that command.
- The CR asks for repetition plus complete-suite coverage. Ten fresh-process exact journeys and
  all 208 frontend tests pass; backend safety remains 670 tests at 93% coverage.

## Independent two-axis review

### Standards

No documented standards violations. The targeted script is additive and the suite metadata changes
scheduling/tolerance without changing assertions, production behavior, UI design, or canonical
quality gates. Judgement call: the helper could conceal isolation issues only if it later replaced
the full suite; it does not do so here.

### Spec

No code-side findings. The scoped timeout, sequential execution, retained command, unchanged
journey, RED/GREEN evidence, repeated executions, complete container file, and full frontend suite
satisfy every locally implementable criterion. External staging/PR checks remain post-push follow-up.

Summary: Standards 0 findings; Spec 0 findings.

## Evidence

- `evidence/terminal-logs/tdd-red-member-governance-timeout.txt`
- `evidence/terminal-logs/tdd-green-member-governance-timeout.txt`
- `evidence/terminal-logs/member-governance-stress.txt`
- `evidence/terminal-logs/member-governance-ci-shaped.txt`
- `evidence/terminal-logs/frontend-tests.txt`
- `evidence/terminal-logs/frontend-quality-gates.txt`
- `evidence/terminal-logs/backend-quality-gates.txt`

## Recommended Next Action

Run independent Ralph validation and commit/push if it passes. Confirm the resulting staging push
and PR #5 frontend required checks are green before merge, then execute 007G2.
