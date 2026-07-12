# Review Packet: 2026-07-13_020824_repair

## Result
Ready for independent validation

## Slice
006Z8-portal-limit-provenance-module-and-interaction-closure

## Repair Finding

The prior trusted logs show four deterministic 30-second timeouts waiting for the borrower sidebar's
`New Application` button. That action is unconditional once the borrower portal is mounted, so the
dashboard fixture and limit projection cannot explain its absence. The failing spec alone used a
storage bootstrap shortcut; the established portal interaction contract signs in through MP00.

The repair makes the limit spec use that proven real-login boundary, waits for the portal member
identity, and selects the exact sidebar action. No production file or limit assertion changed.

## Verification

- Playwright collects the four declared cases from the repaired spec.
- Frontend build, typecheck, lint, and all 204 tests pass.
- Django check and migration sync pass; all 494 backend tests pass with 12 expected PostgreSQL-only
  skips and 93% coverage against the 85% floor.
- `git diff --check` passes. No protected/source file was changed.
- Local Chromium is denied by macOS sandbox services before test bodies; no screenshot was
  fabricated. Independent validation owns both real runs and all four PNGs.

## Traceability

- The slice says to mount the routed real portal container and prove server-only available,
  unavailable, advisory, and review-maximum states. The repaired spec reaches that container through
  the real member-login UI and retains those four exact assertions and screenshots.
- Source BR-003 through BR-007 and M04-FR-005 through M04-FR-007 financial behavior remains in the
  preserved implementation and is covered by `test_credit_modules`, `test_portal_member_api`, and
  `MP05_NewApplication.test.tsx`.

## Recommended Next Action
Run full independent validation and commit only after both trusted browser runs and all screenshots pass.
