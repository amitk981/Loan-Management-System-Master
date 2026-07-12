# Ralph Handoff

## Last Run
2026-07-12_083250_repair

## Current Status

006Y2 makes the 006Y member contract reachable from the staff directory/profile and replaces the
Application Detail witness placeholder with 004E2 capture/read wiring. Member create supports
individual and institution variants; profile update/reverification sends the current version and
canonically refetches detail. Witness capture canonically refetches immutable folio/shareholding
evidence. Profile mutation controls use resource actions; witness controls use exact canonical
permissions because the delivered witness response has no resource-action projection.

## Validation

Evidence is under `.ralph/runs/2026-07-12_083250_repair/`. Frontend lint/typecheck/build and 171
tests passed. Backend check/migration sync and 411 tests passed with five expected PostgreSQL skips
at 94% coverage. The browser spec collects one real-session test; local Chromium launch was denied
by macOS services, so the trusted two-run gate owns the five screenshots and encoded baselines.

## Next Run

Run the due architecture review, then High-risk 006Z and 006Z2. Both have fresh mounted-container
and trusted-browser notes. Witness edit remains deliberately deferred: 004E/004E2 expose no PATCH
contract, editable-field list, optimistic version, update action, or audit rule; A-066 records it.
