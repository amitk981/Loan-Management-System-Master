# Focused Validation

## Playwright collection

Command:

`RALPH_EVIDENCE_DIR=/tmp/cr012-playwright-collection E2E_DJANGO_PYTHON=/Users/amitkallapa/LMS/.ralph/venv/bin/python npm run e2e -- --list e2e/epic-009-staff-disbursement-closure.e2e.spec.ts`

Result: PASS. One Chromium test was collected from the exact declared spec.

## Guarded Epic 009 backend regression

Command:

`/Users/amitkallapa/LMS/.ralph/venv/bin/python sfpcl_credit/manage.py test sfpcl_credit.tests.test_seed_e2e_users.SeedE2eUsersTests.test_epic_009_seed_is_idempotent_and_reaches_real_owned_endpoints`

Result: PASS. One test ran in 1.133 seconds. The guarded fixture seeded, its idempotent rerun was
accepted, system checks were clean, and the test database was destroyed normally.

`/Users/amitkallapa/LMS/.ralph/venv/bin/python sfpcl_credit/manage.py check`: PASS; no issues.

## Impacted frontend regressions

Command:

`npm test -- --run src/pages/disbursement/DisbursementHub.test.tsx src/pages/disbursement/PaymentAuthorisationHub.test.tsx`

Result: PASS. Two files and eight tests passed.

## Frontend gates

- `npm run typecheck`: PASS.
- `npm run lint`: PASS.
- `npm run build`: PASS; 1,882 modules transformed. Vite retained its existing large-chunk warning.

## Boundary and diff checks

- Static scan: PASS; the declared spec contains no `page.route`, `route.fulfill`, `addInitScript`,
  or `localStorage.setItem` browser stub/auth injection.
- `git diff --check`: PASS.
- No production code or protected path was changed by this repair delta.

## Browser execution boundary

The local exact Playwright invocation started the real Django and Vite servers but Chrome closed at
launch after 4 ms with `browserType.launch: Target page, context or browser has been closed`. The
test body did not run and no screenshots were fabricated. Independent validation must execute the
declared spec twice and retain both nine-image manifests.
