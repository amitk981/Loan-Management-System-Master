# Repair Diagnosis

## Bounded Failure Signal

The prior trusted-browser run launched successfully and exposed two deterministic contract failures:

- S44 rendered `Receipt Posted and Allocated` but not the principal-allocation line. The test still
  mocked three retired endpoints, while `postAndAllocateDirectRepayment` now issues one canonical
  `POST /api/v1/loan-accounts/{id}/direct-repayment-command/` request.
- S50-S52 timed out locating the Monitoring navigation button with accessible name exactly
  `Monitoring`. The existing sidebar button also contains its visible badge count, so its accessible
  name is not an exact match for that string.

## Correction

- The S44 browser route now returns the canonical combined command projection and asserts one
  request with one non-empty caller-stable idempotency key.
- The Monitoring selector now accepts the existing badge-bearing accessible name.
- No production code was changed during repair.

## Verification

- `playwright-collection.log`: all four declared scenarios collect successfully.
- `frontend-focused-green.log`: 12/12 repayment and interest/monitoring component tests pass.
- `e2e-lint.log`: repaired spec passes ESLint.
- `frontend-typecheck.log`: TypeScript check passes.
- `trusted-browser-acceptance-1.log`: local Chrome aborted before creating a page for every test.
  This is the documented sandbox browser-infrastructure condition, not a product assertion result;
  no screenshots were fabricated. The independent orchestrator must run the declared contract twice.
