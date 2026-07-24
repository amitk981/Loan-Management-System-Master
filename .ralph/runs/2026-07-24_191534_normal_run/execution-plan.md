# Execution Plan

Selected slice: 012F2-performance-readiness-evidence

## Boundary and permissions

- Work only in the active worktree and only on the prepared 012F2 slice.
- Product/test edits are limited to `sfpcl_credit/**`, `sfpcl-lms/e2e/**`, and
  `docs/working/**`; run evidence is limited to this run folder. These paths are allowed by
  `.ralph/permissions.json`.
- Do not edit protected orchestrator/configuration/source paths, mechanical state/progress/handoff
  facts, business APIs, database models, or production UI/styling.
- Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every backend command. Do not install
  dependencies or run the complete backend suite/coverage lane.

## Source-backed implementation plan

1. Add one public management command and a small `performance_readiness` module whose declarative
   matrix contains every `PERF-001..010`, every distinct test-plan §24.1 target, and every §24.3
   probe. Each row records its public route/job seam, safe role, dataset/load, warm-up, repetitions,
   metric, source threshold, and bounded-local versus release-environment authority.
2. TDD the fail-closed contract vertically: first missing scenarios, then malformed thresholds and
   unsupported skips/failed measurements, then wrong/stale commit evidence. Retain focused red and
   green logs under `evidence/terminal-logs/`.
3. Implement deterministic result evaluation and a machine-readable schema containing environment
   identity, tool versions, commit, dataset counts, measurements/percentiles or batch metrics,
   failures/skips, raw-result hashes, and an explicit `release_evidence_required` outcome for all
   §24.3 rows. A local result can prove the lane but can never claim R8-AC-004 release readiness.
4. Add the exact trusted browser spec `e2e/performance-readiness.e2e.spec.ts`, reusing the existing
   dashboard/auth fixture and visual patterns. Run it twice against the real local auth/shell,
   retaining `performance-readiness-dashboard.png` plus the second-run evidence.
5. Document the stable command, scenario/threshold matrix, result schema, and the exact 012F3
   handoff in `docs/working/PERFORMANCE_READINESS.md`.

## Verification and evidence

- Run each focused backend test red, then green, with the mandated interpreter.
- Run the focused performance-lane backend test file, Django check, and migration drift check.
- Run the exact Playwright spec twice when browser infrastructure permits, plus frontend typecheck,
  lint, test, and build because a frontend E2E spec is added.
- Save representative bounded-local summary/raw results, controlled-failure output, environment and
  dataset manifest, hashes, exact commands, and browser screenshots in this run folder.
- Inspect diff limits and protected paths, complete `risk-assessment.md`, and independently review
  against the slice/source contract. Set the review result exactly to
  `Ready for independent validation`; leave commit/state/status mechanics to the orchestrator.
