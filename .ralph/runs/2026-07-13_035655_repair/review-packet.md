# Review Packet: 2026-07-13_035655_repair

## Result
Repair ready for independent validation

## Slice
006Z10-portal-limit-interaction-and-boundary-proof

## Demonstrated Failure and Fix

Both prior trusted runs passed the first three scenarios, then timed out waiting for
`getByRole('button', { name: 'Mark Uploaded' }).nth(4)`. The helper had captured locators by index;
each click changed the clicked button's accessible name to `Uploaded`, shrinking and re-indexing the
remaining live locator set. The same defect applied to `Self-attested?`.

The repair repeatedly clicks a fresh first matching action until none remain. This follows the real
dynamic UI behavior and changes no production code.

## Verification

- Frontend build, typecheck, and lint pass.
- Vitest: 29 files, 207 tests pass.
- Backend check and migration sync pass.
- Backend: 500 tests pass, 12 expected PostgreSQL-only skips, 93% coverage.
- Playwright collection resolves exactly the four declared scenarios.
- Focused local execution reaches the expected Chromium sandbox denial before page creation; no
  screenshot or browser-pass claim is fabricated.
- `git diff --check` passes and no debug instrumentation remains.

## Traceability

The slice requires a real submit/refetch/reload browser lifecycle. The repaired helper completes
the existing document interaction deterministically so the fourth scenario can reach its submit,
canonical refetch, reload, retained provenance assertion, and screenshot.

## Recommended Next Action
Run the declared trusted browser contract twice outside the sandbox and require all four non-empty
screenshots before committing. If green, continue with sharpened slice 007A.
