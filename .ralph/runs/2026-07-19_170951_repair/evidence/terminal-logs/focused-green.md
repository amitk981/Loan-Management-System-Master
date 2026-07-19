# Focused Green Evidence

## Backend fixture and real-endpoint boundary

Command:

`/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py test tests.test_seed_e2e_users --verbosity 1`

Result: exit 0; 11 tests ran in 2.266s; `OK`. The Epic 009 fixture was created and replayed
idempotently. The focused regression asserts that the real loan-account endpoint includes the
sanctioned account for Senior Finance and excludes it for Credit Manager before activation.

The narrower exact test also passed independently: 1 test ran in 1.487s; `OK`.

## Impacted frontend modules

Command:

`npm test -- src/pages/loan-accounts/LoanAccount360.test.tsx src/pages/disbursement/DisbursementHub.test.tsx src/pages/disbursement/PaymentAuthorisationHub.test.tsx --run`

Result: exit 0; 3 files passed; 13 tests passed. Counts were LoanAccount360 4,
DisbursementHub 4, and PaymentAuthorisationHub 5.

## Playwright collection

Command:

`RALPH_EVIDENCE_DIR=/tmp/cr012-repair-collection E2E_DJANGO_PYTHON=/Users/amitkallapa/LMS/.ralph/venv/bin/python npx playwright test e2e/epic-009-staff-disbursement-closure.e2e.spec.ts --list`

Result: exit 0; exactly 1 Chromium test collected from the declared spec.

Local browser execution was not substituted for the trusted gate. Per the localhost-e2e-server
contract, Ralph must run this exact spec twice outside the coding sandbox and retain the nine PNGs
plus each deterministic manifest.
