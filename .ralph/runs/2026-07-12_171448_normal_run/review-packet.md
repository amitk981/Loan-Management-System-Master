# Review Packet: 2026-07-12_171448_normal_run

## Result
Ready for independent validation

## Slice
006Y9-member-form-real-session-closure

## Recommended Next Action
Run the declared trusted-browser scenario twice, verify all four screenshots, then commit/merge only
if the independent Ralph checks remain green.

## Scope Review

- Added `sfpcl-lms/e2e/member-governance-variants.e2e.spec.ts`; production code is unchanged.
- The test starts at real login, uses no interception or token injection, submits both complete
  §13.2 variants, performs ordinary correction, requests protected identity correction, proves the
  requester cannot approve, signs out visibly, and approves as the separate checker.
- Unique generated identity facts plus exact POST bodies and request cardinalities prevent stale-row
  and client-retry false positives. Only masked values are asserted after canonical reads.

## Traceability

The source contract says API §13.2 requires distinct complete individual/institution payloads and
functional-spec M02-FR-012 requires approved protected identity change. The production form and
Registry already implement those rules; the new Playwright test verifies them through the routed
staff/auth/API boundary, including Registry-projected approval, canonical GETs, and masked readback.

## Validation

- Playwright collection: 1 scenario in the exact declared spec.
- Frontend: build, typecheck, lint, and 176 tests pass.
- Backend: check and migration sync pass; 451 tests pass with 7 expected SQLite skips; coverage 94%.
- Local browser: servers start, Chromium launch is denied by sandbox Mach-port policy before test
  execution. Independent trusted-browser acceptance remains required and authoritative.
