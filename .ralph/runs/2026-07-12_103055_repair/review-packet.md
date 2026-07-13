# Review Packet: 2026-07-12_103055_repair

## Result
Ready for independent validation

## Slice
006Y3-member-registry-and-identity-change-approval-closure

## Recommended Next Action
Run the declared trusted-browser contract twice and require all five non-empty screenshots, then
run the normal independent gates and commit only if they pass.

## Demonstrated Failure and Repair

- Both prior trusted runs reached the checker profile and failed because the global accessible-name
  locator resolved the real primary mutation button and the generic secondary action projection.
- The repaired spec scopes visibility, click, and post-approval disappearance to
  `button.btn-primary` with the exact approval label.
- No production file was changed in this repair.

## Validation

- Playwright collection: 1 declared Chromium test collected.
- Frontend: build, typecheck, lint, and 171 tests pass.
- Backend: system check and migration sync pass; 415 tests pass; coverage is 94% (floor 85%).
- Local browser: Chromium is denied at macOS Mach service startup before the test body. This is the
  documented sandbox limitation, not fabricated screenshot evidence.

## Traceability

M02-FR-012 and the 006Y3 slice require a different, permissioned actor to approve a persisted
identity-change request and require the routed browser flow to prove that approval. The code already
exposes the real primary approval control and a six-field resource-action projection with the same
label. The repaired E2E contract now clicks the mutation control specifically and continues to
assert the approval POST, canonical member GET, control disappearance, denial response, and required
screenshots. Independent trusted-browser execution is the final proof.

## Run-Ahead Review

006Y4 and 006Z are both `Not Started` and already concretely sharpened with fields, permissions,
optimistic-version rules, frontend authority boundaries, tests, and evidence requirements from the
Epic 004 material opened in this run. No further slice edit was warranted in this narrow repair.
