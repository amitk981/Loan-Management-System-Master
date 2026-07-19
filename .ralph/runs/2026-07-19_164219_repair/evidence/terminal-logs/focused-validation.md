# Focused Validation

## Backend guarded fixture and real initiation boundary

Command:

`/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py test sfpcl_credit.tests.test_seed_e2e_users.SeedE2eUsersTests.test_epic_009_seed_is_idempotent_and_reaches_real_owned_endpoints --verbosity 2`

Result: PASS. One test ran; the guarded fixture seeded idempotently and the exact projected
initiation action returned HTTP 200 with `initiated / pending / pending`.

## Browser contract collection

Command:

`RALPH_EVIDENCE_DIR=<collection> E2E_DJANGO_PYTHON=/Users/amitkallapa/LMS/.ralph/venv/bin/python npx playwright test e2e/epic-009-staff-disbursement-closure.e2e.spec.ts --list`

Result: PASS. Exactly one Chromium test was collected from the declared file.

Static boundary scan: PASS. The declared spec contains no `page.route`, `route.fulfill`, or token
injection through `addInitScript`.

## Impacted frontend tests

Command:

`npm test -- src/services/disbursementApi.test.ts src/pages/disbursement/DisbursementHub.test.tsx src/pages/disbursement/PaymentAuthorisationHub.test.tsx src/pages/loan-accounts/LoanAccount360.test.tsx`

Result: PASS. Four files and fifteen tests passed.

## Proportional gates

- `npm run typecheck`: PASS.
- `npm run lint`: PASS.
- `npm run build`: PASS; 1,882 modules transformed. The pre-existing Vite chunk-size warning is
  non-failing.
- `/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py check`: PASS, zero issues.
- `git diff --check`: PASS.

The complete backend coverage gate and both exact trusted-browser executions are intentionally left
to Ralph's independent validator, per the run contract.
