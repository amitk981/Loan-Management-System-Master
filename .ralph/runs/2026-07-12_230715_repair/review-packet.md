# Review Packet: 2026-07-12_230715_repair

## Result

Ready for independent validation.

## Demonstrated Failure and Cause

Both trusted browser runs reached the protected-identity POST but the exact request ledger found 13
surplus ordinary-profile fields. `MemberGovernanceForm` constructed the ordinary update object for
every existing member, then appended PAN/reason in reverification mode. The HTTP client correctly
forwarded that overly broad object; mode switching and request ordering were not at fault.

## Repair

- Added a shared authenticated HTTP-transport regression asserting the exact identity-request body.
- Observed it fail on the same surplus fields as the trusted browser.
- Split identity-request serialization from ordinary update serialization. The request now contains
  only `version`, entered PAN/Aadhaar values, and `reason`.
- Preserved the prior ordinary-PATCH masked-mobile fix and all existing UI composition.

## Traceability

The slice requires exact identity-request bodies and no client-side authority inference. The source
API boundary separates ordinary member PATCH from protected identity-change requests. The production
form now enforces that separation, verified by
`MemberGovernanceForm.container.test.tsx` (`posts only the protected identity delta through the shared HTTP transport`).

## Validation

- Focused red: exact POST contained legal/display/contact/address fields in addition to identity facts.
- Focused green: exact-body regression passed.
- Frontend: build, typecheck, lint, and 202/202 tests passed.
- Backend: check and migration sync passed; 462 tests passed with 8 expected skips; coverage 93%.
- Browser: declared spec collects. Chromium launch is locally blocked by macOS Mach-port sandboxing;
  independent Ralph execution owns the two trusted runs and five screenshots.

## Recommended Next Action

Run full independent validation and the trusted-browser contract twice. Commit and merge only if
both executions and all five screenshots pass.
