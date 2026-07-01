# Prototype Gap Report

The prototype is useful as visual and workflow reference, not production truth.

| Gap | Impact | Where Seen | Recommended Handling |
|---|---|---|---|
| Mock data only | Frontend/backend contract mismatch risk | `sfpcl-lms/src/data/mockData.ts` | Create API contracts and replace one vertical slice at a time. |
| No backend implementation | Cannot validate business rules server-side | Entire app | Backend slices must start from source docs and tests. |
| Demo role handling | Not production-grade auth/RBAC | `RoleContext`, login/dashboard | Implement auth and permission tests before real access control. |
| Missing test infrastructure | Low confidence for future changes | `package.json` test script placeholder | First product slice should add focused test infrastructure or create a testing-enablement slice. |
| Missing error/loading/empty states | User experience and API readiness risk | Many screens | Include state coverage in frontend/API slices. |
| Financial and compliance rules in UI/mock form | High-risk drift from source docs | Appraisal, sanction, repayment, default | Move to backend/service layer with tests when backend exists. |

## Major Conflict Policy
If prototype behavior conflicts with `docs/source/`, source docs win. Record conflicts in `ASSUMPTIONS.md`, an ADR, or a slice blocker.
