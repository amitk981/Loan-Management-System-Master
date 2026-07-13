# Review Packet — 006Y9 Browser Declaration Repair

## Result
Ready for independent trusted-browser validation

## Slice
006Y9-member-form-real-session-closure

## Demonstrated failure

Ralph discovered the spec text but rejected the strict contract before browser execution. Its parser
requires `e2e/*.spec.ts` project-relative spec paths, `Screenshot: <basename>.png` entries, and no
free-form prose inside `Trusted Browser Acceptance`. The slice used a `sfpcl-lms/e2e/...` path,
scenario prose, and nested `evidence/screenshots/...` bullets, producing zero declared screenshots.

## Repair

- Changed only the selected slice declaration: `e2e/member-governance-variants.e2e.spec.ts` plus the
  four exact screenshot basenames.
- Moved the two scenario bullets under `Trusted Browser Scenario` so the strict section contains only
  recognized machine entries.
- Preserved the existing 153-line Playwright scenario and all production code unchanged.

## Verification

- Red loop: Ralph parser deterministically rejected the invalid spec path and all prose/screenshot
  entries; saved in `evidence/terminal-logs/browser-contract-red.log`.
- Green loop: Ralph parser emits one spec and four screenshots; saved in
  `evidence/terminal-logs/browser-contract-green.log`.
- Playwright collection: one Chromium scenario in the declared file.
- Frontend: build, typecheck, lint, and 176 tests pass.
- Backend: check and migration sync pass; 451 tests pass with 7 expected SQLite skips; coverage is
  94% against the 85% floor.

## Traceability

The slice requires two complete §13.2 member variants plus M02-FR-012's approved protected identity
change through distinct real sessions. The preserved browser scenario supplies that proof; this
repair makes its exact spec and four evidence outputs executable by Ralph's trusted acceptance gate.

## Queue readiness

The next grabbable 006Z4 and its dependent 006Z2 are already concretely sharpened with fields,
authority, validation, concurrency, snapshot, portal, and evidence requirements. No run-ahead edit
was needed in this narrowly scoped repair.

## Recommended Next Action
Run the declared browser contract twice, verify all four screenshots, and commit/merge only after
full independent Ralph validation passes. Then run the due architecture review before 006Z4.
