# Review Packet: 2026-07-16_091335_repair

## Result

Ready for independent validation

## Slice
008M3-documentation-workspace-executable-action-closure

## Recommended Next Action

Run configured validation, execute `e2e/staff-documentation-workspace.e2e.spec.ts` twice against
real Django, and verify the four declared PNGs. If green, let the orchestrator commit/merge; then run
the already-sharpened 008M4 slice.

## Root Cause and Repair

- Root cause: the browser spec asked the completed, fully signed Term Sheet fixture for actions that
  the owner correctly suppresses.
- Repair: seed one pending Power of Attorney on the same sanctioned application and drive the exact
  multi-action browser flow through that source-correct instrument.
- Scope: seed/test/spec only for this repair; the quarantined 008M3 production implementation is
  preserved unchanged.

## Review Focus

- Confirm the Term Sheet remains complete/downloadable and exposes no repeated evidence actions.
- Confirm the PoA row and Document Pack each render borrower signature, nominee signature, stamp,
  notary, signed-copy upload, and correction controls.
- Confirm upload/correction reach Django, invalid stamp remains non-optimistic, the tampered opaque
  action returns 404, and the restricted Term Sheet download remains 404.
- Confirm all four declared screenshots are non-empty on both independent runs.

## Traceability

The Epic 008 digest (V10 p.14 §4.3) says PoA is signed by borrower and nominee, uses ₹500 stamp
paper, and is notarised. The E2E seed now creates a pending PoA renderer row; the staff workspace
projects those owner-backed actions; `test_seed_portal_e2e_fixture` verifies the exact HTTP action
set before Playwright consumes it.

## Validation Snapshot

- Backend: 944 passed, 51 skipped, 91% coverage; check and migration drift passed.
- Frontend: 321 passed; typecheck, lint, and build passed.
- Focused: seed HTTP regression, 39 affected backend tests, and 16 documentation UI tests passed.
- Playwright: one real-Django test collected; local launch blocked only by the documented macOS
  Mach-port sandbox denial before page creation.
- Diff: 23 tracked slice files, 1,334 changed lines; within 30 files / 2,000 lines. No protected or
  source path changed.
