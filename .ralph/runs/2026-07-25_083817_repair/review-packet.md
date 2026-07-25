# Review Packet: 2026-07-25_083817_repair

## Result
Ready for independent validation

## Slice
012G-critical-e2e-uat-smoke-scenarios

## Repair outcome

The critical UAT spec now verifies the established subsidiary-repayment idempotency response:
replays carry `idempotency_replayed: true` and place the frozen first response under
`original_response`. The repair changes only this test assertion.

## Validator diagnosis

- Source of truth:
  `.ralph/runs/2026-07-25_082003_repair/failure-summary.md`
- Demonstrated post-launch failure:
  `UAT-014/015/016/017` compared the replay wrapper directly to the created response.
- Confirmed contract:
  `test_subsidiary_deduction_reconciliation_api.py` requires
  `replay.data.original_response == created.data`.
- Repair:
  `critical-uat-smoke.e2e.spec.ts` now asserts both replay metadata and frozen response equality.

## Verification

- PASS — focused backend public API replay contract: 1 test.
- PASS — focused Playwright seed selection: 5 tests.
- PASS — Playwright collected the declared critical UAT spec: 1 test in 1 file.
- PASS — frontend typecheck.
- PASS — frontend lint.
- PASS — frontend production build.
- INDEPENDENT VALIDATION REQUIRED — two current exact browser attempts ended during Chrome launch
  before a page existed. They did not test the repaired line and did not create valid screenshots.
  The infrastructure logs are retained without fabricating evidence.

Evidence:

- `evidence/repair-diagnosis.md`
- `evidence/terminal-logs/subsidiary-replay-contract-green.log`
- `evidence/terminal-logs/frontend-seed-focused-green.log`
- `evidence/terminal-logs/critical-uat-spec-collection-green.log`
- `evidence/terminal-logs/frontend-typecheck.log`
- `evidence/terminal-logs/frontend-lint.log`
- `evidence/terminal-logs/frontend-build.log`
- `evidence/terminal-logs/trusted-browser-replay-red.log`
- `evidence/terminal-logs/trusted-browser-acceptance-1.log`

## Traceability

The source requires retry-safe, idempotent critical UAT journeys (`test-plan.md` §29.4 and
`product-requirements.md` §11.23). The code now checks the repository's canonical replay wrapper
without weakening duplicate prevention. This is verified by the focused subsidiary-deduction
public-API regression and must be completed by the independent two-run trusted-browser acceptance.

## Scope review

No production code, business rule, API contract, UI design, permission, model, migration, source
document, protected file, mechanical state/progress fact, or unrelated slice was changed by this
repair.

## Recommended Next Action
Run full independent validation. The trusted browser gate must execute the declared spec twice and
produce `critical-uat-standard-loan.png` and `critical-uat-permission-negative.png` with complete
manifests before the candidate may commit.
