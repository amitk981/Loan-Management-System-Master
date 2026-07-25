# Review Packet: 2026-07-25_101057_repair

## Result
Ready for independent validation

## Slice

012G-critical-e2e-uat-smoke-scenarios

## Demonstrated validation domain

The authoritative backend impacted lane showed an authenticated user without tracer permission
receiving 404 instead of the required 403. The request failed at URL resolution, before the
permission guard.

The trusted-browser excerpts in the same failure summary ended during Chrome launch before page
creation. They are infrastructure evidence, not a product assertion, and were not used to widen
this backend repair.

## Repair reviewed

- Production-isolation tests restore `ENABLE_DEMO_SURFACES` and then rebuild the conditional
  runtime URLconf and clear resolver caches.
- The tracer route therefore remains available under normal test settings and reaches the
  existing permission guard.
- Production settings still omit the tracer application/routes.
- No permission was granted, no production endpoint was added, and the denied request writes no
  domain or audit rows.

## Verification summary

- Exact six-worker impacted validator: 1,694 passed, 170 skipped
- Ordered production-isolation plus permission regression: 4 passed
- Isolated permission contract: 1 passed
- Django system check: passed
- Migration drift: no changes detected
- Diff hygiene: passed

## Traceability

The source test plan says an unauthorized endpoint call returns 403
(`docs/source/test-plan.md` §18.2, SEC-AUTHZ-003), and the product requirements say the backend
enforces permissions independently of frontend visibility
(`docs/source/product-requirements.md` §11.2). The retained cleanup ensures the public tracer route
resolves after a production-settings isolation test, then the unchanged backend guard returns the
standard 403 denial. This is verified by
`TracerApiTests.test_authenticated_user_without_tracer_permission_cannot_write_domain_rows` in both
the minimized ordered loop and the full impacted lane.

## Recommended next action

Run full independent Ralph validation, retaining the exact impacted backend mapping and the two
trusted executions of `e2e/critical-uat-smoke.e2e.spec.ts`.
