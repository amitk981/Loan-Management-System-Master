# Review Packet: 2026-07-12_103847_repair

## Result
Ready for independent validation

## Slice
006Y3-member-registry-and-identity-change-approval-closure

## Recommended Next Action
Run the declared trusted-browser contract twice and require all five non-empty screenshots, then
run the normal independent gates and commit only if they pass.

## Demonstrated Failure and Repair

- Both prior trusted runs completed member create, canonical update, request, and checker approval,
  then received the expected HTTP 403 from the zero-permission mutation.
- The response used `error.code = FORBIDDEN`, as required by the shared 002J2 API contract and the
  endpoint adapter; the E2E assertion alone expected the retired `PERMISSION_DENIED` value.
- The repaired spec asserts `FORBIDDEN` and still requires the real denied POST before capturing
  `member-governance-denied.png`. No production file changed in this repair.

## Validation

- Playwright collection: 1 declared Chromium test collected.
- Frontend: build, typecheck, lint, and 171 tests pass.
- Backend: system check and migration sync pass; 415 tests pass; coverage is 94% (floor 85%).
- Local browser: Chromium is denied at macOS Mach service startup before the test body. This is the
  documented sandbox limitation, not fabricated screenshot evidence.

## Traceability

`docs/source/api-contracts.md` §7.1, distilled in `docs/working/API_CONTRACTS.md` under "Shared
authenticated permission denial (002J2)", requires authenticated missing-permission responses to
use `403 FORBIDDEN`. The 006Y3 browser contract requires a real denial and its screenshot. The code
already returns that standard response; the corrected assertion now allows the executed denial path
to reach its required screenshot without weakening any permission or business rule.

## Run-Ahead Review

006Y4 and 006Z are both `Not Started` and already concretely sharpened with resource fields,
permissions, optimistic versions, frontend authority boundaries, tests, and evidence requirements
from the Epic 004 material opened in this run. No further slice edit was warranted in this narrow
repair.
