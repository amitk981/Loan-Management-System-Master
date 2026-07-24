# Review Packet: 2026-07-24_123250_normal_run

## Result
Ready for independent validation

## Slice
012E2-tracer-and-demo-route-production-isolation

## Implementation summary

- Added a fail-closed production Django settings module and a centralized demo-surface setting.
- Removed the tracer app and all tracer route imports/registrations from production.
- Disabled every inventoried predictable demo/E2E seed command in production and denied existing
  synthetic staff/member identities before session creation.
- Added a centralized frontend production flag, production route/nav denial, and lazy isolation for
  tracer, demo identities, login selection, and role switching.
- Updated A-011 and the working API contract with the production disposition.

## Tracer/demo inventory and disposition

| Surface | Production disposition | Development disposition |
|---|---|---|
| Django `sfpcl_credit.tracer` app/models/views | Not installed by production settings | Installed by default development settings |
| Seven `/api/v1/tracer/**` routes | Not imported or registered; recursive regression guard + 404 | Existing lifecycle API remains available |
| `tracer.lifecycle.run` role grant | Cannot reach routes; synthetic identities denied | Guarded tracer users retain exact permission |
| `seed_demo_users` | Refused by centralized setting | Existing DEBUG + explicit seed guard retained |
| `seed_approval_configuration` | Refused by centralized setting | Existing demo committee path retained |
| `seed_e2e_users` | Refused by centralized setting | Existing Playwright fixtures retained |
| `seed_portal_e2e_fixture` | Refused; existing synthetic portal login denied | Existing portal acceptance fixture retained |
| `seed_epic_009_e2e_fixture` | Refused by centralized setting | Existing Epic 009 fixture retained |
| Frontend `TracerBullet` + `tracerApi` | Route denied and modules absent from production bundle | Lazy-loaded when dev demo surfaces are enabled |
| Sidebar Tracer item | Absent even if backend returns tracer permission | Visible only with explicit tracer permission |
| Staff LoginScreen demo selector / App demo login | Absent from production bundle; forced flag ignored | Existing `VITE_ENABLE_DEMO_AUTH=true` behavior retained |
| RoleContext fixtures / Header role switch | Moved to eliminated demo bundle; no production UI/identities | Existing labels, grouping, and switch behavior retained |
| MP00 portal demo fallback | Remains closed; production demo flag cannot reactivate it | Existing separately flagged test behavior unchanged |
| Agentation `localhost:4747` dev endpoint | Endpoint/package markers absent from production build | Existing `import.meta.env.DEV` behavior retained |

## Traceability

The source says environments must be separated and production must apply strict controls
(`docs/source/security-privacy.md` §30; `docs/source/deployment-ops.md` §§6 and 9). The code now
centralizes that boundary in `sfpcl_credit.config.production_settings`,
`ENABLE_DEMO_SURFACES`, and frontend `DEMO_SURFACES_ENABLED`. This is verified by
`test_production_demo_isolation`, `productionSurfaceIsolation.test.ts`, `demoAuthFlag.test.tsx`,
and the production static-exclusion log. A-011’s deferred production isolation is marked resolved.

## Test evidence

- Backend RED/GREEN tracer deployment:
  `evidence/terminal-logs/backend-production-tracer-red.log`,
  `evidence/terminal-logs/backend-production-tracer-green.log`
- Backend RED/GREEN seed isolation:
  `evidence/terminal-logs/backend-production-seeds-red.log`,
  `evidence/terminal-logs/backend-production-all-seeds-red.log`,
  `evidence/terminal-logs/backend-production-all-seeds-green.log`
- Backend RED/GREEN pre-existing identity denial:
  `evidence/terminal-logs/backend-production-existing-demo-user-red.log`,
  `evidence/terminal-logs/backend-production-existing-demo-user-green.log`
- Final backend impacted lane: 61 tests green in
  `evidence/terminal-logs/backend-final-impacted-tests.log`
- Backend checks: normal/production check and migration sync green in
  `evidence/terminal-logs/backend-final-check-and-migrations.log`
- Frontend RED/GREEN:
  `evidence/terminal-logs/frontend-production-demo-auth-red.log`,
  `evidence/terminal-logs/frontend-production-demo-auth-green.log`,
  `evidence/terminal-logs/frontend-production-tracer-red.log`,
  `evidence/terminal-logs/frontend-production-tracer-green.log`
- Final frontend: 437 tests, typecheck, lint, and build green in
  `evidence/terminal-logs/frontend-final-gates.log`
- Production bundle: all tracer/demo/role-switch/dev-endpoint markers absent in
  `evidence/terminal-logs/frontend-production-static-exclusion.log`

## Review notes

- Self-review found and closed two inventory gaps before handoff: portal/Epic 009 seed commands and
  pre-existing synthetic identities.
- Development UI structure was retained while moving demo-only code behind eliminated imports.
- No migrations, dependencies, source documents, protected configuration, or orchestrator-owned
  mechanical state were changed.

## Recommended Next Action
Run Ralph’s independent High-risk validation lane and commit only if it passes.
