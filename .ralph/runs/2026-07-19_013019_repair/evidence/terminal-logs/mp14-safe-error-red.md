# MP14 Safe-Error Red Evidence

Command:

```text
npm test -- --run src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx
```

Result: expected failure, exit code 1.

```text
FAIL MP14 disbursement status > shows processing, blocked, empty, session, and safe error states
Unable to find an element with the text:
Disbursement status could not be loaded. Please try again.

Rendered alert text:
Unavailable.

Test Files  1 failed (1)
Tests       1 failed | 3 passed (4)
```

The regression uses the real shared-client error shape produced by the trusted browser's HTTP 503:
`AuthSessionError('SERVICE_UNAVAILABLE', 'Unavailable.', 503)`. This exactly reproduces the missing
borrower-safe copy and raw server-message disclosure from the independent browser gate.
