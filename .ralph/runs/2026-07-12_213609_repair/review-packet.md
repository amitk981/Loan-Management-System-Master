# Review Packet: 2026-07-12_213609_repair

## Result
Ready for independent validation

## Slice
006Y11-member-form-container-and-error-matrix-closure

## Diagnosis

Both trusted runs reached the enabled approval action and returned the same six-field Registry fact:
`required_permission` was `members.member.identity_change.approve`. The E2E test alone expected
`members.member.update`, so it failed before the approval POST and final screenshot.

## Repair

Changed only the stale E2E expected value to the dedicated permission already defined by
`MemberRegistry.APPROVE_PERMISSION`, the permission catalogue, the E2E manager seed, and focused
backend API tests. No production code or behavior changed.

## Standards and Spec

- API §44 requires resource-projected actions to retain their exact authority facts. The repaired
  assertion now checks the backend's dedicated identity-approval permission verbatim.
- M02-FR-012's separate checker approval remains exercised through the real-session scenario; the
  correction does not broaden authority or replace backend decisions with frontend logic.
- Frontend design rules are unaffected because no UI or styling changed.

## Verification

- Focused backend public Registry authority test: pass.
- Mounted Member Form/Profile containers: 17 tests pass.
- Playwright collection: one scenario in one file.
- Frontend build/typecheck/lint and full 199-test suite: pass.
- Backend check/migration sync and full 453-test coverage suite: pass, 7 expected skips, 93% coverage.
- Local Chromium launch: sandbox-denied before the test body; not treated as a product failure.

## Recommended Next Action
Run the declared trusted browser contract twice, verify all five screenshots, then let the Ralph
orchestrator commit and merge only after full independent validation.
