# Tracer Permission URLconf Repair Diagnosis

## Authoritative symptom

The prior orchestrator-owned impacted backend lane reached
`TracerApiTests.test_authenticated_user_without_tracer_permission_cannot_write_domain_rows` and
received HTTP 404 instead of the source-required HTTP 403. The request therefore missed the
tracer view before its permission guard could run.

The same failure summary also records two Chrome closures during `browserType.launch`, before a
page existed. Those are browser infrastructure evidence and are not an application assertion.

## Tight feedback loop

The orchestrator-owned red excerpt is retained locally in
`terminal-logs/backend-impacted-authoritative-red.md`: 1,401 tests ran before fail-fast stopped on
the 404/403 mismatch.

The minimized order-sensitive loop runs:

1. all three `ProductionDemoIdentityTests`, which temporarily disable demo surfaces; then
2. the authenticated tracer permission-negative test, which must resolve the tracer route and
   return 403 without writing domain or audit rows.

Current green evidence: `terminal-logs/urlconf-permission-focused-green.log` — 4 tests passed.

The original full feedback loop is the exact six-worker impacted command copied from the prior
orchestrator result. Current green evidence: `terminal-logs/backend-impacted-green.log` — 1,694
tests passed with 170 expected skips.

## Ranked hypotheses

1. **Conditional URLconf state leaked after a production-settings override — confirmed.**
   `sfpcl_credit.config.urls` constructs tracer patterns at module import time from
   `ENABLE_DEMO_SURFACES`. Restoring the setting does not reconstruct an already materialized
   module/resolver, so a later tracer request in the same worker can return 404.
2. **The tracer route is absent under normal development settings — disproved.** The isolated
   permission test passes and returns the required 403.
3. **The tracer permission guard returns the wrong denial status — disproved.** Once the route
   resolves, the existing guard returns the standard `FORBIDDEN` response and writes no rows.
4. **The endpoint in the regression is obsolete — disproved.** The public tracer lifecycle tests
   and the critical UAT seed use the same registered surface.

## Retained repair

`ProductionDemoIdentityTests.tearDownClass` now verifies the production override has been restored,
reloads `sfpcl_credit.config.urls` under the normal setting, and clears Django URL resolver caches.
This repairs test-worker isolation without registering tracer routes in production, weakening
permissions, or changing a production API.

File timestamps show the cleanup was written after the prior authoritative impacted result, so
the current exact green run is the first full impacted-lane verification of the retained fix.

## Verification

- Exact six-worker impacted backend validator: `terminal-logs/backend-impacted-green.log`
- Ordered URLconf/permission regression: `terminal-logs/urlconf-permission-focused-green.log`
- Isolated permission contract: `terminal-logs/tracer-permission-isolated-green.log`
- Django system check: `terminal-logs/django-check.log`
- Migration drift: `terminal-logs/migration-check.log`
- Diff hygiene: `terminal-logs/git-diff-check.log`

The first full-lane attempt in this run was invalid before test execution because spawned workers
bypassed the owner-provided arm64 wrapper and loaded an x86_64 interpreter with arm64 native
packages. `terminal-logs/backend-impacted-worker-architecture-invalid.log` retains that
infrastructure evidence. The valid rerun set `PYTHONEXECUTABLE` to the mandated wrapper for worker
spawns; this changed execution architecture only, not test scope or repository code.
