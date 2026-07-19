# Focused Validation

## Backend owner-evidence regression

Command:

`/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py test tests.test_seed_e2e_users.SeedE2eUsersTests.test_epic_009_seed_is_idempotent_and_reaches_real_owned_endpoints --verbosity 2`

Result: PASS — 1 test ran in 1.106 seconds. The guarded fixture remained idempotent and the real
workspace endpoint exposed `initiate_disbursement` after `--make-ready`.

## Playwright collection

Command:

`RALPH_EVIDENCE_DIR=/private/tmp/cr012-collection E2E_DJANGO_PYTHON=/Users/amitkallapa/LMS/.ralph/venv/bin/python npx playwright test e2e/epic-009-staff-disbursement-closure.e2e.spec.ts --list`

Result: PASS — exactly 1 Chromium test collected from the declared spec.

## Impacted frontend tests

Command:

`npm test -- --run src/pages/disbursement/DisbursementHub.test.tsx src/pages/disbursement/PaymentAuthorisationHub.test.tsx`

Result: PASS — 2 files, 8 tests.

## Frontend gates

- `npm run typecheck`: PASS.
- `npm run lint`: PASS.
- `npm run build`: PASS; 1,882 modules transformed. The existing Vite chunk-size advisory remains
  non-failing.

## Static and diff checks

- PASS: no `page.route`, `route.fulfill`, `addInitScript`, or auth-session `localStorage.setItem`
  exists in the declared spec.
- PASS: `git diff --check`.
- PASS: no `[DEBUG-*]`, TODO, or FIXME marker in the changed implementation.
- PASS: no production file was changed by this repair attempt; its candidate delta is two reloads
  and one navigation reopen in the existing Playwright spec.
