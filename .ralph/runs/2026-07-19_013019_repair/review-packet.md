# Review Packet: 2026-07-19_013019_repair

## Result

Ready for independent Ralph validation.

## Slice

009I2-portal-disbursement-stage-and-visual-closure

## Demonstrated failure

The previous external browser run passed MP14's processing and accepted-advice cases, then failed
only the safe-error case. The exact HTTP 503 response became an `AuthSessionError` whose message was
`Unavailable.`; MP14 displayed that server copy instead of its declared borrower-safe fallback, so
the assertion failed and `mp14-safe-error.png` was not created.

## Repair delivered

- Replaced the shallow plain-`Error` unit fixture with the real shared-client 503
  `AuthSessionError` shape and asserted that raw `Unavailable.` copy is absent.
- Preserved tailored borrower messages for 401 and 403, while mapping all other API/client errors to
  MP14's existing operation-specific safe fallback.
- Preserved the two passing browser cases, exact selected-application route seam, real Django
  authentication/list/selection path, masking assertions, visual composition, and screenshot names.
- Added no styling, component, API, backend, migration, dependency, or business-stage change.

## Source-to-evidence traceability

- The slice requires a borrower-safe error state and forbids exposing internal evidence. The code
  now renders `Disbursement status could not be loaded. Please try again.` for the exact 503 client
  shape and suppresses its raw `Unavailable.` message.
- The corrected regression is
  `MP14_DisbursementStatus.test.tsx > shows processing, blocked, empty, session, and safe error
  states`; red and green outputs are retained under `evidence/terminal-logs/`.
- The declared Playwright spec still collects all three cases. Ralph's external browser gate owns
  the twice-run visual proof and the three non-empty screenshots.

## Verification

- Focused red proof: 1 expected failure, with DOM showing `Unavailable.`.
- Focused green proof: 4/4 MP14 tests passed.
- Impacted portal tests: 10/10 passed across 2 files.
- Typecheck, ESLint, and production build passed.
- Playwright collection: 3 tests in the declared spec, exit code 0.
- Local Chrome launch was blocked before page creation; no screenshot was fabricated.

## Recommended Next Action

Run Ralph's complete independent validation, including the declared browser contract twice. Commit
and merge only after every configured gate passes and all three screenshots are non-empty.
