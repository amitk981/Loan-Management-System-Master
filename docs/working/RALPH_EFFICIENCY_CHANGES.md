# Ralph Efficiency Changes — 2026-07-17

These changes cap recurring work without weakening slice acceptance. Normal and repair runs still validate the complete candidate; only proven duplication, fixture setup, artifact retention, and documentation-only work are treated differently.

## Fixture pilot

The largest static test fixture in `test_approval_case_routing_api.py` was moved from per-test `setUp()` to Django's transactional `setUpTestData()` class fixture. The same 127 tests passed before and after the change.

- Test execution: 6.113s → 3.980s (35% faster)
- Whole command: 20.825s → 18.068s (13% faster)
- Current staging baseline: 80 `setUp()` methods and 0 `setUpTestData()` methods (the earlier 77-method audit predated intervening slices)
- After this first incremental conversion: 79 `setUp()` methods and 1 `setUpTestData()` method; the separately audited 26 nested constructions are deferred to later, individually proved refactors

Further fixture work should follow the same one-class-at-a-time pattern and prove identical test behavior before moving to the next hotspot.

## Parallel coverage proof and decision

The shadow pilot ran the complete backend test label once under the existing serial coverage command and once with two Django workers. It compared exact outcome counters and canonical per-file executed, missing, and excluded line sets—not only the rounded coverage percentage.

- Serial: 950.1s
- Two workers: 569.7s
- Speedup: 1.668×
- Both lanes: 1,095 discovered and run, 62 skipped, 0 failures, 0 errors
- Both lanes: 45,130 statements, 41,256 covered, 3,874 missing, 14 excluded, 91.4159095945%
- Exact line-set SHA-256 in both lanes: `5eb9c68285ac6d6ae235ea2ff5492760f13c2a5c32b70f91bb0097c249585a9f`

Because every proof predicate matched, authoritative backend coverage is bounded at two workers. The helper still runs the full suite, combines worker coverage, and enforces the existing 85% floor. Setting the worker count to 1 restores the original serial command.

## Documentation-only architecture reviews

Architecture reviews now have a fail-closed documentation lane. Candidate scope must remain entirely under `docs/` or `.ralph/`, while protected-path checks, queue validation, artifact checks, and the frozen-candidate hash still run. Product gates are skipped with an explicit reason only after that scope proof; any product path rejects the lane.

## Agent transcript retention

New raw Codex and Claude transcripts are stored outside the candidate under Git's common directory and retained for at most 20 runs or 14 days by default. Committed evidence contains only a bounded final excerpt, byte and line counts, session id, and SHA-256 digest. Existing historical transcripts are not rewritten.
