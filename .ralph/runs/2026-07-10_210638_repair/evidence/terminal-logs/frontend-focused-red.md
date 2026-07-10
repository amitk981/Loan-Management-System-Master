# Frontend Focused Test — Red

Command:
`npm test -- --run src/services/creditAssessmentApi.test.ts src/pages/appraisal/AppraisalWorkbench.test.tsx`

Exit code: 1

```text
FAIL  src/services/creditAssessmentApi.test.ts
Error: Cannot find module './creditAssessmentApi'

FAIL  src/pages/appraisal/AppraisalWorkbench.test.tsx
14 tests failed: AppraisalWorkbenchView is not exported by the prototype workbench.

Test Files  2 failed (2)
Tests       14 failed (14)
Duration    743ms
```

This is the intended red-capable signal: the tests require the missing typed Epic 006 API client
and an API-backed public workbench view, including exact sanction request/error behavior and stored
eligibility, limit, review-history, permission, and workflow-state rendering.
