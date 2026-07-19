# Slice 012E2: Tracer and Demo Route Production Isolation

## Status
Not Started

## Parent Epic
Epic 012: Reports, Exports, Hardening, and UAT
Epic file: `docs/epics/012-reports-exports-hardening-uat.md`

## Goal
Remove, environment-gate, or separately authorize every tracer/demo-only surface before production, with a negative deployment test. The 002EX tracer app and its API routes are currently unconditionally installed, and assumption A-011 requires production isolation (PRODUCTION_COMPLETION_BLUEPRINT.md §6.3).

## User Value
No demo user, tracer route, or role-switching shortcut is reachable in a production deployment; auditors can verify the boundary mechanically.

## Depends On
- 012E

## Runtime Capabilities

- `none`

## Source References
- docs/source/security-privacy.md production configuration and environment isolation requirements
- docs/source/deployment-ops.md environment/settings expectations
- docs/working/ASSUMPTIONS.md A-011
- docs/slices/002EX-early-end-to-end-tracer-bullet.md (tracer surface inventory)
- docs/slices/002K-seed-data-and-demo-users.md and 002K2 (demo user/permission isolation)
- `docs/working/digests/epic-012-reports-exports-hardening-uat.md` §012E2 / §012E3

## Prototype Reference
- sfpcl-lms dev-only Tracer screen and any demo role-switching affordances (RoleContext)

## Concrete Requirements
1. Inventory every tracer/demo surface: Django tracer app + URL routes, tracer frontend screen/route, demo seed users, demo role-switching UI, and any dev-only endpoints. Known members of the inventory: `VITE_ENABLE_DEMO_AUTH`/`DEMO_AUTH_ENABLED` (services/authSession.ts), the staff LoginScreen demo selector, `handleDemoLogin` in App.tsx, RoleContext `setRole`/`ROLE_USERS` fixtures, and the TracerBullet screen/routes. The portal MP00 demo fallback is closed earlier by 005FA2 — verify it stayed closed. Record the full inventory in the review packet.
2. Gate each behind an explicit non-production flag derived from the environment/settings module — default OFF for production settings; no ad-hoc env checks scattered in code.
3. Negative deployment test: under the production settings module, tracer URLs return 404/are unregistered, the tracer screen/route is absent from the build or unreachable, demo users are absent/disabled, and role-switching UI does not render. The test must fail closed if a new tracer surface is added unguarded.
4. Frontend production build must not ship the tracer/demo code paths where the bundler supports elimination; otherwise route-guard and document the residual.
5. Update ASSUMPTIONS.md A-011 disposition with the evidence.

## Test Cases
- Production-settings negative tests for every inventoried surface (backend routes, seed users, frontend routes).
- Development settings keep the tracer working (002EX/006X evidence paths unaffected).
- Regression guard that unregistered tracer surfaces stay unregistered.

## Out of Scope
Production settings hardening beyond this boundary (012F enumerates it), secret/key management (012E3), deployment pipeline (012H).

## Evidence Required
Saved RED/GREEN production-settings tests for every inventoried backend, frontend, seed, and role-switch
surface; production-build/static exclusion proof; development tracer reverse-consumer results;
updated A-011 disposition and configured full gates.

## Risk Level
High

## Acceptance Criteria
- A production-configured deployment provably exposes zero tracer/demo surfaces; dev/test tracer evidence still works.
- All gates pass; negative-test output saved.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] Permissions tested, if needed
- [ ] Audit events tested, if needed
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Substantive unresolved risk or decision recorded only if needed
- [ ] Commit created only after passing gates
