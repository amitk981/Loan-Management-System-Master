# Review Packet: 2026-07-25_094752_repair

## Result
Ready for independent validation

## Slice

012G-critical-e2e-uat-smoke-scenarios

## Demonstrated validation domain

The authoritative trusted-browser run reached the DPD public API and showed one stale test
expectation: repayments dated `2026-07-25` were incorrectly expected to reduce overdue principal
for the earlier `2026-07-01` cutoff.

## Repair reviewed

- The historical DPD expectation is `400000.00`.
- The scenario explicitly asserts `principal_paid_as_of=0.00` for the earlier cutoff.
- The separate current-state assertion still proves the later direct allocation reduces principal
  to `300000.00`.
- No production business logic or permission was broadened.

## Verification summary

- Focused backend DPD and seed/public-API tests: 3 passed
- Frontend seed tests: 5 passed
- Typecheck: passed
- Lint: passed
- Production build: passed
- Django system check: passed
- Migration drift check: no changes detected
- `git diff --check`: passed

Two exact browser retries and the dedicated probe ended before page creation because Chrome closed
during launch. No current screenshot is claimed or fabricated; trusted independent validation must
produce the two declared screenshot sets.

## Traceability

The source says DPD is calculated from schedule truth and repayments update outstanding according
to their recorded dates (`docs/source/product-requirements.md` §§11.23 and 11.25; the critical E2E
path is required by `docs/source/test-plan.md` §§16.11 and 29.4). The browser scenario now keeps the
`2026-07-01` snapshot at the full `400000.00` scheduled principal because both receipts are dated
`2026-07-25`, while separately proving the later direct allocation reduces current principal to
`300000.00`. This is verified by
`DpdPaymentTimingApiTests.test_later_posted_repayment_does_not_reduce_earlier_snapshot` and the
critical-UAT public scenario assertions.

## Recommended next action

Run full independent Ralph validation, including two fresh executions of
`e2e/critical-uat-smoke.e2e.spec.ts` and both required screenshot manifests.
