# Failure Summary

- Run: 2026-07-19_003418_normal_run
- Mode: normal_run
- Slice: 009I2-portal-disbursement-stage-and-visual-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
e2e-results.md:- FAIL: first trusted slice-specific browser run did not pass.
e2e-results.md:- FAIL: one or more declared browser screenshots are missing or empty.
```

## Last 50 lines: e2e-results.md

```
# e2e Results

- PASS: slice-specific trusted browser contract is valid.
- PASS: README E2E command resolves the shared venv through Git's common directory.
- PASS: Playwright pins the dashboard baseline timezone to Asia/Kolkata.
- FAIL: first trusted slice-specific browser run did not pass.
- SKIP: second trusted slice-specific browser run deferred because the first run failed.
- FAIL: one or more declared browser screenshots are missing or empty.

Declared specs:
- e2e/portal-disbursement-status.spec.ts
Declared screenshots:
- mp14-processing.png
- mp14-disbursed-advice.png
- mp14-safe-error.png
```

## Changed files (git status)

```
docs/slices/009I2-portal-disbursement-stage-and-visual-closure.md
docs/working/API_CONTRACTS.md
docs/working/digests/epic-009-sap-loan-account-disbursement.md
sfpcl-lms/playwright.config.ts
sfpcl-lms/src/pages/borrower/BorrowerPortal.tsx
sfpcl-lms/src/pages/borrower/portal/PortalMemberViews.test.tsx
sfpcl-lms/src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx
sfpcl-lms/src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.tsx
sfpcl_credit/disbursements/modules/current_disbursement_evidence.py
sfpcl_credit/disbursements/modules/post_transfer_evidence.py
sfpcl_credit/legal_documents/modules/disbursement_readiness.py
sfpcl_credit/loans/modules/loan_account_lifecycle.py
sfpcl_credit/processes/portal_disbursement_status.py
sfpcl_credit/sap_workflow/modules/sap_customer_profile.py
sfpcl_credit/tests/test_portal_disbursement_status_api.py
.ralph/runs/2026-07-19_003418_normal_run/
sfpcl-lms/e2e/portal-disbursement-status.spec.ts
```
