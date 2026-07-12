# Review Packet: 2026-07-12_225603_repair

## Result
Ready for independent validation

## Slice
006Y13-member-mutation-success-interaction-closure

## Demonstrated Failure and Cause

Both trusted browser runs failed because the exact ordinary-update expectation required the original
plain mobile while the real canonical detail correctly returned a masked mobile. The production form
hydrated that masked display value and sent it in the PATCH. The correct hypothesis was blind
resubmission of canonical masked state; request ordering and canonical refetch timing were sound.

## Repair

- A routed production-container test now seeds `********3210` and asserts the exact PATCH omits it.
- `MemberGovernanceForm` omits only an unchanged masked mobile; a replacement value remains writable.
- The browser ledger's exact PATCH expectation now reflects the source-compliant partial body.

## Traceability

`api-contracts.md` §13.3 requires canonical member detail with masked values and §13.4 defines PATCH
as a partial update containing changed contact/address fields. The form now preserves that boundary:
display masks are never treated as replacement contact values. The mounted real-App regression proves
the exact request and the existing canonical GET/readback sequence.

## Validation

- Focused red: exact PATCH unexpectedly contained `mobile_number: "********3210"`.
- Focused green: routed test passed; mounted member matrix 14/14 passed.
- Frontend: build, typecheck, lint, and 201/201 tests passed.
- Backend: check and migration sync passed; 462 tests passed with 8 expected skips; coverage 93%.
- Browser: declared Playwright test collects. Local Chromium launch is blocked by macOS Mach-port
  sandboxing; independent Ralph execution owns the two trusted runs and five screenshots.

## Recommended Next Action

Run full independent validation and the declared trusted-browser contract twice. Commit and merge only
if both runs and all five screenshots pass.
