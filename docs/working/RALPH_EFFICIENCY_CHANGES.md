# Ralph Efficiency Changes — 2026-07-17

These changes reduce safe sources of recurring work without weakening Ralph's binding full-gate acceptance policy. Candidate-scope selection remains in shadow measurement until its evidence and the quality policy support activation.

## Fixture pilot

The largest static test fixture in `test_approval_case_routing_api.py` was moved from per-test `setUp()` to Django's transactional `setUpTestData()` class fixture. The same 127 tests passed before and after the change.

- Test execution: 6.113s → 3.980s (35% faster)
- Whole command: 20.825s → 18.068s (13% faster)
- PostgreSQL transaction races: 2/2 passed with the shared fixture builder and per-test transaction isolation
- Current staging baseline: 80 `setUp()` method definitions and 0 `setUpTestData()` methods (the earlier 77-method audit predated intervening slices)
- After this first incremental conversion: 80 explicit `setUp()` definitions and 1 `setUpTestData()` method. The main 127-test class no longer rebuilds the fixture per test; one explicit `setUp()` was added for its two PostgreSQL `TransactionTestCase` races, which cannot use class-level data. The separately audited 26 nested constructions are deferred to later, individually proved refactors.

Further fixture work should follow the same one-class-at-a-time pattern and prove identical test behavior before moving to the next hotspot.

## Parallel coverage proof and decision

The shadow pilot ran the complete backend test label once under the existing serial coverage command and once with two Django workers. It compared exact outcome counters and canonical per-file executed, missing, and excluded line sets—not only the rounded coverage percentage.

- Serial: 950.1s
- Two workers: 569.7s
- Speedup: 1.668×
- Both lanes: 1,095 discovered and run, 62 skipped, 0 failures, 0 errors
- Both lanes: 45,130 statements, 41,256 covered, 3,874 missing, 14 excluded, 91.4159095945%
- Exact line-set SHA-256 in both lanes: `5eb9c68285ac6d6ae235ea2ff5492760f13c2a5c32b70f91bb0097c249585a9f`

The initial proof enabled two workers. A later six-worker pilot exposed nondeterministic branch coverage in a ciphertext-tampering test: the random encrypted token and an A/B replacement of its last Base64 character could exercise either the noncanonical-Base64 rejection path or the authenticated-decryption rejection path. CR-009 split that test into two deterministic cases, preserving the expected `InvalidCiphertext` behavior while making both rejection paths explicit and repeatable.

The corrected 1,097-test suite was then piloted at six workers and, only after that passed, at eight workers. Both pilots compared a serial lane with the bounded parallel lane using the same exact predicates:

- Both worker counts: 1,097 discovered and run, 62 skipped, 0 failures, 0 errors
- Both worker counts and serial controls: 45,147 statements, 41,275 covered, 3,872 missing, 14 excluded, 91.4235718874%
- Exact line-set SHA-256 in every corrected lane: `1e9a93c0cb3dbb7c10cc8acaa776049aa800c0458cc45ff1a757874387baff6e`
- Six workers: 932.1s serial control, 362.9s parallel, 2.568x speedup
- Eight workers: 1,001.7s serial control, 381.5s parallel, 2.626x speedup
- Eight workers were 18.6s (5.1%) slower than six in absolute parallel runtime on the current 8-core host

Because every proof predicate matched and six had the best measured wall time, authoritative backend coverage is bounded at six workers. The helper still runs the full suite, combines worker coverage, and enforces the existing 85% floor. Setting the worker count to 1 restores the original serial command. Re-pilot before changing the bound on a different host or after material test-suite growth.

## Documentation-only architecture reviews

Architecture reviews now have a fail-closed documentation lane. Candidate scope must remain under `docs/`, explicit state/progress bookkeeping, or the current review's own run-evidence directory, while protected-path checks, queue validation, artifact checks, and the frozen-candidate hash still run. Product gates are skipped with an explicit reason only after that scope proof; any product path, configuration edit, or historical run-evidence edit rejects the lane.

## Backend validation shadow

Normal and repair runs classify the frozen candidate and record a future lane recommendation, reason, backend paths, and test labels in `backend-validation-lane-results.md`. The recommendation is deliberately non-authoritative: full configured backend gates still execute for every candidate, including frontend/docs-only changes.

The shadow selector recommends full coverage for High risk, every fourth slice, schema/infrastructure/shared/package-root work, multiple or broad backend modules, deletions/renames, missing changed tests, or tests that do not import the one changed backend module. Unknown policy values and malformed inputs also resolve to full. This preserves the current quality contract while collecting the data needed to decide whether a later policy change is justified.

## Pending-age CI flake

The failed 1,116-test GitHub run compared two otherwise identical approval queue payloads across separate requests. `workbench_summary.pending_age.elapsed_seconds` advanced from 12 to 13, which is correct live behavior, but the regression expected the entire payload to remain byte-identical. A forced one-second boundary reproduced the failure. The test now compares the stable historical routing payload separately and asserts that the dynamic pending age keeps its label, non-empty display, and monotonic elapsed seconds. The focused test and the complete 1,117-test suite pass.

## GitHub CI controls

The regular backend CI job continues to run the complete `sfpcl_credit.tests` label and enforce the 85% floor, but now uses the already-proved multiprocessing coverage helper with four workers, matching GitHub's public Linux runner allocation. Setup-python caches pinned pip dependencies, superseded runs on the same ref are cancelled, and the job has a 30-minute hard timeout. A separate 75-minute serial canary runs nightly against `staging` and can be dispatched for epic or release checkpoints. This preserves serial/order-sensitive detection without charging every slice for a second slow lane.

## Agent transcript retention

New raw Codex and Claude transcripts are stored outside the candidate under Git's common directory and retained for at most 20 runs or 14 days by default. Committed evidence contains only a bounded final excerpt, byte and line counts, session id, and SHA-256 digest. Existing historical transcripts are not rewritten.
