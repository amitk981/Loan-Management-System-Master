# Risk Assessment

Risk level: High

- Selected slice: `CR-004-member-governance-container-recurring-ci-timeout`
- Mode: `normal_run`
- Standing approval: active; the veto list contains no revoked slice.
- Protected/source files: unchanged.
- Production UI/backend/database impact: none.
- Dependency/migration impact: none.

## Material risks and controls

- False-green risk: a longer timeout could hide a broken or needlessly slow test. The 15-second
  value is suite-local, the exact journey still completes in 1.27-1.35 seconds locally, every
  assertion is unchanged, and all other suites retain the 5000 ms default.
- Isolation risk: mounted DOM work could overlap later rows. The suite is explicitly sequential,
  existing `afterEach` cleanup remains unchanged, and the complete 16-row file passes in one worker.
- Gate-weakening risk: a focused script could replace the full suite. It is additive only;
  `npm test` remains `vitest run`, and the complete 208-test gate passed after the focused stress.
- CI scheduling risk: hosted runners can still be slower than the worktree. The local policy leaves
  more than 10x the measured exact-journey time and the retained CI-shaped command makes worker/file
  behavior reproducible.

## Residual risk

The sandbox cannot push or inspect the resulting GitHub Actions runs. The orchestrator must perform
independent validation, commit and push `staging`; the staging push and PR #5 frontend required check
must be observed green before merge. This external follow-up is an acceptance gate, not evidence of
a local code defect.
