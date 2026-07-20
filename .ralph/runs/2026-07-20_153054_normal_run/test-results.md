# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_153054_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 847ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  315ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1052ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  623ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1423ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  658ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  378ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1934ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  380ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  345ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 615ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  361ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 301ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2643ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  650ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  431ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 571ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  482ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 191ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2317ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1129ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  942ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 996ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  348ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  401ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1165ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  375ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 413ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 255ms
 ✓ src/services/authSession.test.ts (36 tests) 50ms
 ✓ src/services/portalApi.test.ts (7 tests) 21ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 168ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 56ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 323ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 175ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 105ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 9ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5587ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  499ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  414ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  338ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  392ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  324ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  360ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  376ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  321ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  645ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 75ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 34ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 18ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 36ms
 ✓ src/services/tracerApi.test.ts (2 tests) 6ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 32ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 73ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4506ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2088ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  339ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  337ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1091ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  992ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  16:13:14
   Duration  8.47s (transform 4.26s, setup 0ms, collect 12.66s, tests 27.16s, environment 6.05s, prepare 2.85s)


Duration milliseconds: 9277
Exit code: 0
