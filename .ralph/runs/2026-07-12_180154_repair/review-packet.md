# Review Packet: 2026-07-12_180154_repair

## Result
Ready for independent validation

## Slice
006Y9-member-form-real-session-closure

## Demonstrated Failure and Fix

Both independent trusted runs completed the requester-side identity request and real session switch.
The checker then received the canonical seeded-member detail but the shared navigation helper waited
for `Verified identity locked`. That banner belongs to the edit form, which is correctly hidden when
the Registry projects update as disabled and approval as enabled. The helper now waits for the
canonical profile heading; the requester path still proves the banner before requesting correction.

## Verification

- Playwright collection: exactly 1 scenario in the declared spec.
- Focused member-form/container tests: 5/5 pass.
- Frontend: build, typecheck, lint, and 177/177 tests pass.
- Backend: Django check and migration sync pass; 451 tests pass with 7 expected SQLite skips.
- Coverage: 93%, above the 85% floor.
- Browser: local launch is denied before page creation by macOS Mach-port sandbox policy. The
  orchestrator must run the contract twice and verify all four named screenshots.
- Cleanup: no debug instrumentation was introduced; protected paths remain clean.

## Traceability

The slice requires distinct requester/checker sessions and consumption of the Registry-projected
approval action. The backend projects member update disabled and identity approval enabled to the
checker; the E2E flow now respects that boundary and proceeds to assert both projected and primary
approval controls before POST.

## Post-mortem

The confirmed root cause was a shared readiness helper coupled to requester-only UI authority.
Using a role-neutral canonical profile marker for navigation readiness prevents this class of error.

## Recommended Next Action

Run full independent validation, including two trusted-browser executions and all four screenshots.
If green, commit the preserved slice and perform the due architecture review.
