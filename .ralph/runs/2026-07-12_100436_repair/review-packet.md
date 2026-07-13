# Review Packet: 2026-07-12_100436_repair

## Result
Ready for independent validation

## Slice
006Y3-member-registry-and-identity-change-approval-closure

## Demonstrated Failure and Fix

Both trusted runs created a member successfully, then received `500` from the canonical PATCH.
The traceback showed `MemberChangeHistory.old_value_json/new_value_json` attempting to serialize a
Python `date` for `membership_start_date`. The history projection now emits the same canonical
`YYYY-MM-DD` form accepted and returned by the API.

## Traceability

- The slice requires complete field-level member history: `services._safe_member_values` now keeps
  membership dates complete and JSON-safe instead of failing the entire mutation.
- The slice requires mutations through the public Member Registry interface: regression test
  `test_update_with_membership_date_persists_json_safe_history` drives authenticated PATCH through
  the URL/view/registry/service boundary and asserts the stored old/new history.
- The slice requires the real-session browser create/update flow: the original Playwright contract
  remains unchanged and collects successfully; its prior exact `500` is covered at the backend seam.

## Validation

- Focused backend regression: red with the trusted-run traceback, then green.
- Frontend: build, typecheck, lint, 171/171 tests pass.
- Backend: Django check, migration sync, 415/415 tests pass; coverage 94% (floor 85%).
- Playwright: one declared test collects. Local Chromium launch is denied by the macOS Mach service
  sandbox before the test body; no screenshots were fabricated.
- `git diff --check` passes; no debug instrumentation remains.

## Recommended Next Action
Run the declared browser contract twice outside the coding sandbox and accept only if all five
screenshots are non-empty on both runs; then proceed to already-sharpened 006Y4.
