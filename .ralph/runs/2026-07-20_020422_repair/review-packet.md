# Review Packet: 2026-07-20_020422_repair

## Result
Ready for independent validation

## Slice
010C2-manual-allocation-and-financial-reversal-controls

## Repair Outcome

- Preserved the quarantined implementation byte-for-byte during this repair.
- Replaced invalid Django dotted labels in the current run's closure artifact with the validator's
  required candidate-relative `test_file.py::Class::method` selectors.
- Bound the retained TDD RED and current focused GREEN evidence to the exact permanent selector.
- The real semantic-closure validator now passes 1 finding and exactly AC-ALLOC-1 through
  AC-ALLOC-6.

## Root Cause

The original `review-closure-evidence.md` used executable Django test labels, but the Ralph closure
contract deliberately requires a file path and exact declaration selector so it can prove the test
is permanent, candidate-visible, discoverable, and AST-resolvable before expensive gates.

## Validation Evidence

- Failure reproduction: `evidence/terminal-logs/closure-validator-red.log`.
- Corrected contract gate: `evidence/terminal-logs/closure-validator-green.log` — pass, exit 0.
- Permanent regression evidence: `evidence/terminal-logs/allocation-admission-red.log` and
  `evidence/terminal-logs/closure-green.log`.
- Focused API/catalogue verification: 5 tests passed.
- Focused PostgreSQL cross-receipt idempotency verification: 1 test passed.

## Traceability

The fixed-point finding AR-010-ALLOCATION-001 requires canonical admission, idempotency, exact
schedule reconciliation, immutable evidence, governed correction, and narrow role authority. The
current `review-closure-evidence.md` maps its exact root and AC-ALLOC-1 through AC-ALLOC-6 to
permanent tests in `sfpcl_credit/tests/test_repayment_adjustment_api.py`; the closure validator
confirmed the mapping.

## Recommended Next Action
Run full independent validation against the preserved quarantined candidate; commit only if every
authoritative gate passes.
