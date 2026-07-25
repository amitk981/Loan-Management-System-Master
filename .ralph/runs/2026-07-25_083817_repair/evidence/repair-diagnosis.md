# Trusted-Browser Replay Assertion Diagnosis

## Authoritative symptom

The prior orchestrator-owned trusted-browser run launched Chrome and reached
`UAT-014/015/016/017`. The first subsidiary-deduction request returned the created repayment.
The same public request and idempotency key then returned:

- `idempotency_replayed: true`
- `original_response`: the frozen first response

The E2E spec incorrectly compared that replay wrapper directly with the first response.

## Ranked hypotheses

1. The E2E assertion expected the wrong public replay shape. Confirmed by the validator payload and
   `test_subsidiary_deduction_reconciliation_api.py`.
2. The public repayment endpoint returned an accidental extra wrapper. Disproved by the existing
   endpoint regression, which explicitly requires that wrapper.
3. The seeded state or request body caused a second repayment rather than a replay. Disproved by
   `idempotency_replayed: true`, the frozen `original_response`, and the focused backend regression.
4. The failure was browser infrastructure. Disproved for the authoritative failure because that
   run completed public UI/API actions before the assertion; this run's later pre-page launch
   failures are separately retained as infrastructure evidence.

## Repair

The E2E assertion now requires the established public contract exactly:
`{ idempotency_replayed: true, original_response: subsidiary.data }`.
No production code, API contract, business rule, permission, model, or fixture behavior changed.

## Verification

- Authoritative RED: prior run
  `.ralph/runs/2026-07-25_082003_repair/evidence/terminal-logs/trusted-browser-acceptance-1.log`
- Current focused GREEN:
  `terminal-logs/subsidiary-replay-contract-green.log` — 1 backend contract test passed.
- Current frontend GREEN:
  `terminal-logs/frontend-seed-focused-green.log` — 5 tests passed.
- Current static/build GREEN:
  `terminal-logs/frontend-typecheck.log`, `frontend-lint.log`, and `frontend-build.log`.
- Current browser infrastructure evidence:
  `terminal-logs/trusted-browser-replay-red.log` and
  `terminal-logs/trusted-browser-acceptance-1.log` both ended before a page existed.

Independent trusted validation must execute the declared spec and produce both declared screenshots.
