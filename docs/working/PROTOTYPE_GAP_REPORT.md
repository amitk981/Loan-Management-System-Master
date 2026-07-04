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
| Prototype MP screen numbering diverges from `screen-spec-member-portal.md` | Risk of wiring a screen against the wrong spec section | `MP22_ProduceSupply.tsx` (spec MP22 = Grievance Detail & Tracking); `MP24_SupportGrievance.tsx` covers spec MP21+MP22 (spec MP24 = Help Guide) | Slices 005FB and 011NA name both the spec IDs and the prototype files explicitly; spec IDs are authoritative. |
| No real end-to-end proof | Structural frontend/API/database issues surface late | Whole staff lifecycle | Partially closed by 002EX with a dev-only Tracer screen backed by real APIs, persistent SQLite smoke evidence, audit/workflow rows, and explicit `tracer.lifecycle.run`; full-fidelity module rules remain in later epics. |
| Missing admin user-management screen | System Administrator had no reachable shell for user role/team/status administration | Settings/admin area | Closed by 002G with `AdminUsers`, real `/api/v1/admin/users/` API calls, `manage_users` navigation/route guard, assignment controls, and backend audit/session-revocation enforcement. |

## Major Conflict Policy
If prototype behavior conflicts with `docs/source/`, source docs win. Record conflicts in `ASSUMPTIONS.md`, an ADR, or a slice blocker.
