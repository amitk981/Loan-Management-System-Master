# Review Packet: 2026-07-19_174320_repair

## Result
Ready for independent validation

## Slice
CR-012-epic-009-playwright-evidence-is-incomplete

## Repair Finding

The prior trusted run proved the browser reached the real Django CFC authorisation and transfer
endpoints. The spec nevertheless derived transfer time from the browser clock. Django correctly
rejected that evidence when it preceded the server-owned `authorised_at`, preventing the final three
screenshots and both manifests.

The repaired spec derives the next representable local form minute from the successful Django
authorisation response and asserts its ISO round trip is strictly later before submitting. This is a
test-contract repair only; backend chronology and all production behavior remain unchanged.

## Traceability

- The CR and `screen-spec.md` S36-S42 require real authenticated Django workflow states and distinct
  evidence; the spec continues through real form login and contains no owned-API route fulfilment.
- Slice CR-012 requires each screenshot to follow a state-specific visible assertion; the preserved
  spec asserts all nine states immediately before the declared captures.
- Slice CR-012 requires exactly nine distinct per-run SHA-256 values; `writeAndVerifyManifest` checks
  file existence, unique hashes, sorted deterministic rows, and the exact nine declared basenames.
- The chronological backend contract requires transfer evidence not to predate CFC authorisation; the
  new pre-submit assertion verifies that exact rule using the real response's `authorised_at`.

## Verification

- Playwright collection: 1 declared test collected, PASS.
- Impacted frontend tests: 13/13 PASS.
- Guarded seed/backend boundary tests: 11/11 PASS.
- Typecheck, lint, build, and diff check: PASS.
- Local browser execution: infrastructure-only Chrome launch closure, documented in repair evidence;
  no browser result is fabricated or claimed green.

## Scope Review

- No production UI, API, business rule, permission, money logic, styling, model, or migration changed
  in this repair.
- No protected path or `docs/source/` file changed.
- The existing uncommitted CR implementation and earlier run evidence are preserved.

## Independent Validation Contract

Run `e2e/epic-009-staff-disbursement-closure.e2e.spec.ts` twice outside the sandbox. Each run must
freshly retain the nine declared PNGs plus a deterministic manifest with exactly nine distinct hashes.
Then run the complete configured frontend/backend gates. Any new real-boundary failure should fail
closed.
