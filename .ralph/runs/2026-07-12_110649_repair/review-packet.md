# Review Packet

## Outcome

The trusted-browser witness flow no longer depends on the borrower remaining KYC verified after
the preceding identity-governance scenario. It uses a distinct seeded, verified shareholder with
an active positive shareholding.

## Demonstrated failure and fix

- Before: the governance test moved member `...0602` to KYC pending; witness capture reused
  `...0602` and deterministically returned `400` in both independent runs.
- After: member `...0611` / shareholding `...0612` are idempotently seeded for witness capture.
- Regression: `test_seeded_witness_capture_is_independent_of_borrower_reverification` sets the
  borrower to pending and proves the authenticated witness POST returns `200` for `...0611`.

## Validation

- Frontend: build, typecheck, lint, 27 test files / 173 tests pass.
- Backend: system check and migration sync pass; 419 tests pass with five expected skips; coverage
  is 94% against the 85% floor.
- Browser contract: both tests collect. Local execution is blocked before test code by Chromium's
  denied macOS Mach service registration, so Ralph's two independent runs remain authoritative.
- Hygiene: `git diff --check` passes; no debug instrumentation remains.

## Traceability

The slice says witness capture must use verified shareholder/KYC evidence and the code correctly
enforces that rule. The repair preserves it: instead of weakening KYC validation, it supplies a
separate source-shaped verified shareholder. The real API regression verifies that distinction.
