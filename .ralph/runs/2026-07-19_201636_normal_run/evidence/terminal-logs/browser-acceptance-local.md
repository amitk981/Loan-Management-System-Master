# Local Browser Acceptance Feedback

Collection with `E2E_DJANGO_PYTHON` and `RALPH_EVIDENCE_DIR` set:

```text
Listing tests:
  [chromium] › epic-009-staff-disbursement-closure.e2e.spec.ts:36:5 ›
  S36-S41 and initial Loan Account 360 use real Django and retain distinct evidence
Total: 1 test in 1 file
```

The local execution started the real Django and Vite servers and received a 200 readiness response.
Chrome then exited during sandbox launch with `browserType.launch: Target page, context or browser
has been closed`. This is the sandbox failure explicitly anticipated by the run contract. No
screenshot was fabricated; Ralph's independent browser gate runs the contract twice outside the
sandbox and is authoritative.
