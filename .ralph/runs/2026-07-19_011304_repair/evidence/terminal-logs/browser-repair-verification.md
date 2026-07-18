# Browser Repair Verification

## Playwright collection

```text
Listing tests:
  [chromium] › portal-disbursement-status.spec.ts:11:5 › MP14 preserves the borrower composition for current SAP-complete processing
  [chromium] › portal-disbursement-status.spec.ts:27:5 › MP14 preserves masked transfer facts and accepted-advice availability
  [chromium] › portal-disbursement-status.spec.ts:41:5 › MP14 renders a safe unavailable state for an exact status failure
Total: 3 tests in 1 file
```

Exit code: 0.

## Focused portal tests

Command:

```text
npm test -- src/pages/borrower/portal/PortalMemberViews.test.tsx src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx
```

Result: 2 files passed, 10 tests passed, exit code 0. This includes opposite-order application
selection and the MP14 explicit selected-id request contract.
