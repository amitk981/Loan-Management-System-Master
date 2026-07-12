# Review Packet: 2026-07-12_175317_repair

## Result
Ready for independent validation

## Slice
006Y9-member-form-real-session-closure

## Demonstrated Failure and Fix

Both independent trusted runs completed individual creation, canonical readback, ordinary update,
and the first screenshot. Institution registration then failed before submission because
`getByLabel('PAN')` matched the common `PAN` input and `Signatory PAN`. The repair makes the shared
common-field label lookup exact. Production behavior is unchanged.

## Verification

- Playwright collection: exactly 1 scenario in the declared spec.
- Focused locator check: the common helper uses `{ exact: true }`.
- Frontend: build, typecheck, lint, and 177/177 tests pass.
- Backend: Django check and migration sync pass; 451 tests pass with 7 expected SQLite skips.
- Coverage: 93%, above the 85% floor.
- Browser: local launch is denied before page creation by macOS Mach-port sandbox policy. The
  orchestrator must run the contract twice and verify all four named screenshots.
- Cleanup: no debug instrumentation exists; `git diff --check` passes; protected files are clean.

## Traceability

The slice requires complete individual and institution registration through real routed sessions.
The trusted trace proves the individual path and first screenshot completed, then the institution
form exposed the locator ambiguity. Exact label selection now addresses the common PAN field while
leaving the distinct signatory field for its own exact accessible label.

## Post-mortem

The confirmed root cause was substring matching between semantically distinct accessible labels.
Using exact accessible-name matching in helpers that operate on forms with prefixed identity fields
would have prevented the failure.

## Recommended Next Action

Run full independent validation, including two trusted-browser executions and all four screenshots.
If green, commit the preserved slice and perform the due architecture review.
