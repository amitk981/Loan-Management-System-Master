# Focused Green Evidence

## Playwright contract collection

- Command: `npm run e2e -- --list e2e/epic-009-staff-disbursement-closure.e2e.spec.ts`
- Required Django interpreter and evidence environment variables were set.
- Result: PASS
- Collected: 1 test in 1 file

## Impacted frontend tests

Command:

`npm test -- --run src/pages/loan-accounts/LoanAccount360.test.tsx src/pages/disbursement/DisbursementHub.test.tsx src/pages/disbursement/PaymentAuthorisationHub.test.tsx`

- Result: PASS
- Test files: 3 passed
- Tests: 13 passed

## Guarded seed and real-owner backend boundary

Command:

`<ralph-venv>/bin/python manage.py test sfpcl_credit.tests.test_seed_e2e_users --verbosity 2`

- Result: PASS
- Tests: 11 passed
- Django system check: no issues
- Includes double-guard refusal, idempotence, real owned endpoint reachability, and seeded actor scope
  coverage retained from the preserved implementation.
