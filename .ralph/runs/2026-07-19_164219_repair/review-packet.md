# Review Packet: 2026-07-19_164219_repair

## Result
Ready for independent validation

## Slice
CR-012-epic-009-playwright-evidence-is-incomplete

## Demonstrated failure and repair

Run `2026-07-19_163229_repair` reached the genuine initiation endpoint but received HTTP 400 after
two overlapping workspace reads. The second React Strict Mode response could replace the action
descriptor and reset the final-verification form after Playwright filled it. The spec now waits for
workspace traffic to settle, asserts the server-projected amount and required comments immediately
before submission, and reports the safe Django envelope on a response failure.

The guarded backend regression now posts the exact projected action payload through Django and
proves the isolated fixture itself returns `initiated / pending / pending`. No production behavior,
API contract, business rule, permission, money rule, styling, or layout changed.

## Traceability

- The CR and slice require real staff login, no browser fulfilment of owned APIs, nine state-specific
  screenshots, immediate visible assertions, and nine distinct SHA-256 values. The declared spec
  uses `staffLogin`, real Django URLs, fresh evidence cleanup, state assertions before every capture,
  and a nine-entry distinct-hash manifest; static inspection confirms no `page.route`,
  `route.fulfill`, or token injection.
- Epic 009's parent contract says Senior Manager Finance initiates only after readiness and CFC
  independently authorises. The real projected-action backend regression verifies initiation only
  after the source-bank blocker is removed; the Playwright sequence then changes to the genuine CFC
  actor before authorisation.
- `docs/working/FRONTEND_DESIGN_RULES.md` forbids redesign during wiring. No production frontend file
  or styling was changed in this repair.

## Verification reviewed

- Guarded fixture and exact real initiation regression: PASS (one test).
- Impacted frontend tests: PASS (four files, fifteen tests).
- Exact Playwright collection and real-boundary static scan: PASS.
- Typecheck, lint, build, Django check, and diff check: PASS.
- Local exact browser attempt: Chrome closed during launch before the test body; no screenshot claim
  is made from the coding sandbox.

## Independent acceptance still required

Ralph must execute the exact declared Playwright contract twice outside the sandbox, with fresh
evidence each time, and accept only two complete sets of nine structurally valid, pairwise-distinct
PNGs plus deterministic manifests. Ralph also owns the authoritative complete backend suite under
coverage and all remaining gates.

## Recommended Next Action
Run full independent validation; commit only after the two trusted browser runs and all configured
gates pass.
