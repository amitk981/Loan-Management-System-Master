# Review Packet

## Demonstrated Failure

Both trusted runs completed the real login, create POST, and canonical detail GET, then timed out on
`Back to Members`. That control does not exist; the routed destination is the created member's
profile heading. The same logs also showed two identical initial detail GETs under React Strict Mode.

## Root Cause and Fix

The confirmed hypothesis was an obsolete E2E destination assertion plus Strict Mode replay of an
unshared initial fetch. The scenario now asserts the legal-name heading, consumes the disabled/enabled
Registry-projected approval controls, targets only the primary checker mutation control, and checks
the backend's last-four PAN mask. `MemberProfile` retains the in-flight initial request per member ID
so the replay attaches to it instead of issuing a duplicate.

## Traceability

The slice says successful registration must perform one POST plus one canonical detail GET, render
masked protected identities, and consume the Registry-projected six-field approval action before
checker POST. The component regression proves one initial GET under Strict Mode; the routed scenario
asserts exact create bodies/cardinality, masked readback, requester denial reason, enabled checker
projection, and the separate primary approval POST.

## Verification

- Focused regression: red at two calls, green at one call.
- Playwright collection: one declared scenario.
- Frontend: build, typecheck, lint, and 177 tests pass.
- Backend: Django check and migration sync pass; 451 tests pass with 7 expected SQLite skips; 94%
  coverage exceeds the 85% floor.
- `git diff --check` passes and no protected path appears in the diff.

## Post-mortem

The bug would have been prevented by mounting the routed profile under React Strict Mode and by
using destination/action locators already established in `member-governance-closure.e2e.spec.ts`.
The new container regression locks down the request-cardinality seam.
