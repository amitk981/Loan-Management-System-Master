# Frontend red tracer

Command:

`npm test -- --run src/pages/loan-accounts/LoanAccount360.test.tsx`

Expected RED observed before implementation:

```text
FAIL  src/pages/loan-accounts/LoanAccount360.test.tsx
Error: Failed to resolve import "../../services/loanAccountsApi"
Test Files  1 failed (1)
Tests       no tests
```

The initial-view test named the missing authenticated API boundary before it was added.
