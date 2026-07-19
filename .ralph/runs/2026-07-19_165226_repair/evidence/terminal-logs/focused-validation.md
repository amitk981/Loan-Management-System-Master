# Focused Validation

## Guarded backend fixture (TDD)

- Red: the fixture regression failed because Senior Finance did not yet have
  `finance.disbursement.mark_success`; see `backend-transfer-actor-red.log`.
- Green: the same exact test passed after the guarded fixture assigned the existing grant and
  synthetic evidence to Senior Finance; see `backend-transfer-actor-green.log`.
- The final green in `backend-handoff-final-green.log` additionally proves the real CFC
  authorisation response, empty post-action CFC queue, and Senior Finance transfer action.
- The test also retains guard refusal, idempotent seeding, real workspace/account reads, real
  initiation, and immutable upload provenance checks.

## Browser and frontend contract

- Playwright collection: PASS, exactly one Chromium test from the declared spec.
- Static browser boundary: PASS, three real form actors, nine unique screenshot declarations,
  genuine authorisation/transfer response assertions, pairwise SHA-256 enforcement, and no
  `page.route`, `route.fulfill`, `addInitScript`, or token injection.
- Impacted frontend tests: PASS, four files and sixteen tests.
- Focused payment-authorisation regression: PASS, five tests including terminal CFC queue removal.

## Proportional gates

- `npm run typecheck`: PASS.
- `npm run lint`: PASS.
- `npm run build`: PASS; 1,882 modules transformed. The existing chunk-size warning is non-failing.
- `/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py check`: PASS, zero issues.
- `git diff --check`: PASS.

The complete backend suite under coverage and both exact trusted-browser executions are reserved for
Ralph's independent validator by the run contract.
