# Risk Assessment

Risk level: High.

- Selected slice: 011M2-member-portal-kyc-correction-request
- Mode: repair
- Manual review required: Ralph independent validation remains authoritative before integration.

## Demonstrated failure and root cause

The failed complete-backend lane projected current migration leaves while constructing the
historical pre-credit-ownership application state. The new `members.0016_kyc_correction_request`
leaf depends on later state and was not excluded, so the projection could advance beyond the
declared `applications.0010` boundary and remove
`applications.EligibilityAssessment` before the test created its fixtures.

The preserved repair adds `members` to the affected historical leaf exclusions. It changes test
state construction only; it does not modify the 011M2 production migration or any business rule.
The immediately preceding same-worktree repair also made the related global-search no-echo
assertion ignore volatile response metadata, removing a separate full-suite nondeterminism exposed
by the same fail-fast validator.

## Evidence

- Prior exact RED:
  `evidence/terminal-logs/backend-red-credit-model-ownership-migration.log`.
- Current focused GREEN:
  `evidence/terminal-logs/backend-repro-migration-test.log` — 1 test passed.
- Current authoritative complete lane:
  `evidence/terminal-logs/backend-full-coverage-validator-final.log` — 1,699 tests passed, 173
  expected skips, 89% coverage against the 85% floor, exit zero.
- Candidate integrity: `git diff --check` passed and no `[DEBUG-*]` instrumentation remains in the
  three repair tests.

## Execution-environment note

Two initial validator launches failed before product execution because spawned macOS workers
selected the x86_64 slice of universal CPython while the orchestrator-managed virtualenv contains
arm64 native extensions. The successful run set Python's standard `PYTHONEXECUTABLE` worker
override to the mandated virtualenv wrapper. No dependency, virtualenv, runner, or protected-file
change was made.

## Residual risk

The candidate remains a High-risk full-stack slice and must still receive Ralph's independent
validation. The repaired backend lane now covers every backend test and the global coverage floor;
no additional repair scope is justified.
