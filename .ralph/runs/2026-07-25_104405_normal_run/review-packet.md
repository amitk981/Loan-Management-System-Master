# Review Packet: 2026-07-25_104405_normal_run

## Result
Ready for independent validation

## Slice
012H-deployment-readiness-and-smoke-checks

## Recommended Next Action
Run the orchestrator-owned risk-selected backend lane and the trusted
`deployment-smoke-readiness.e2e.spec.ts` browser contract.

## Delivered Behaviour

- Added public `GET /health/live/` with a fixed `200 {"status":"live"}` response and
  zero database queries.
- Added public `GET /health/ready/` with cheap database, migration, and critical
  signing/encryption configuration checks plus terse sanitized 503 reasons.
- Added `manage.py smoke_check --base-url` with legible stage failures, environment-only
  credentials, current-user identity/permission validation, and eight bounded read-only
  workflow checks spanning every 012G module group.
- Added an isolated `deployment_smoke_reader` E2E role rather than changing a canonical
  production role. Its dashboard context uses the existing compliance pattern.
- Added API contracts, deployment assumption A-258, response examples, performance
  evidence, and the exact two-repetition trusted-browser spec.

## Standards Review

Independent standards review found two issues:

1. evidence logs contained machine-specific absolute paths;
2. readiness duplicated field-encryption configuration knowledge.

Both are resolved: final evidence is path-sanitized, and readiness exercises the shared
`FieldEncryption` owner and catches its configuration error. Existing URL, command,
dashboard, auth, pagination, test, and frontend patterns are reused.

## Spec Review

Independent spec review found four implementation gaps and one environment-dependent
acceptance item:

1. authentication success was not bound to the current-user payload;
2. an arbitrary or admin credential could drive the command;
3. workflow reads did not span all four 012G module groups;
4. a database failure while constructing migration state could escape unsanitized;
5. Chromium exited during launch, leaving trusted screenshots outstanding.

Items 1-4 are resolved and covered by focused tests. `/auth/me/` must match the configured
email, cannot include `system_admin`, and must expose exactly the dedicated read-only
permission set. Eight bounded reads cover the application/approval,
documentation/security/disbursement, servicing/default/closure/compliance, and
reports/export/audit groups. Migration construction failures return the fixed
`database_unavailable` reason. Item 5 is correctly deferred to trusted validation under
the slice's `localhost-e2e-server` rule after two bounded local attempts; no screenshot
was fabricated.

## Traceability

- `deployment-ops.md` §§20.1-20.3 → root health endpoints and health failure tests.
- `deployment-ops.md` §13.1 steps 10-14 → runnable smoke command, isolated-server
  transcript, and browser contract.
- `security-privacy.md` → fixed response tokens, environment-only credentials,
  admin rejection, and secret/stack/path leak assertions.
- `test-plan.md` and 012G digest → representative workflow groups, focused red/green
  tests, and configured validation evidence.

## Validation Evidence

- Focused backend: 22 tests passed (`terminal-logs/backend-focused-final.log`).
- Local server: eight workflows passed with no business writes
  (`terminal-logs/smoke-local-server-final.log`).
- Isolated deployed-process transcript: all stages passed in 0.87 seconds
  (`terminal-logs/smoke-check-local-transcript.log`).
- Django system/migration checks and `git diff --check` passed.
- Impacted frontend tests: 9 passed; typecheck, lint, and production build passed.
- Playwright spec discovery lists both required repetitions.
- Browser launch attempts and the outstanding trusted screenshot are documented in
  `evidence/browser-acceptance.md`.

## Residual Risks

- Production provider/worker/monitoring probes require the owner-selected hosting
  architecture and are not represented as passing.
- Trusted Chromium must produce `deployment-smoke-readiness.png` during independent
  validation.
