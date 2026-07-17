# Review Packet: 2026-07-17_223410_repair

## Result
Ready for independent validation

## Slice
009G3-post-transfer-aggregate-and-checklist-integrity-closure

## Demonstrated Failure

The prior run's full parallel coverage failed in
`test_public_post_disbursement_signature_binds_current_transfer_evidence`: the test attempted to
delete `LoanRegisterUpdate`, while 009G3 deliberately makes the exact register relation protected.
The underlying `ProtectedError` then triggered Django's secondary traceback-pickling error.

## Repair Review

- Preserved the quarantined 009G3 production implementation and migration unchanged.
- Added `ProtectedError` to the legacy test's imports.
- Replaced the obsolete delete/reinsert tamper with an explicit protected-deletion assertion and a
  reversible checksum mutation that still proves public checklist replay rejects changed register
  evidence with HTTP 409.
- Rechecked 009G4 and 009H3; both remain concrete and executable, so no speculative sharpening was
  needed.

## Verification

- Exact failing test: RED before the repair, GREEN after it.
- Impacted classes: 61 tests pass.
- Django check and migration sync pass.
- A supplemental local parallel attempt ran zero tests because spawned workers could not load the
  arm64 CFFI extension from x86_64; it was stopped and excluded from the passing evidence.
- No protected path is modified. Full coverage and twice-run PostgreSQL acceptance remain the
  orchestrator's independent gates.

## Traceability

The slice says successful transfer truth must protect its exact Loan Register relation and that
changed retained evidence must fail closed. The repaired test now proves both behaviors directly:
deletion raises `ProtectedError`, and a changed register checksum makes checklist replay return 409.

## Recommended Next Action

Run complete independent Ralph validation. After 009G3 commits, run 009H3, then 009G4 once both of
its prerequisites are complete.
