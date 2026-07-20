# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_070519_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1090ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  308ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  572ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1343ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  600ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  356ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1798ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  303ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2371ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1172ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  910ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2348ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  482ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  432ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1251ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  400ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1094ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  386ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  461ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 716ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 538ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  435ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 639ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  403ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 398ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 397ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 320ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 228ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 250ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 62ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 62ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 159ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 149ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5329ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  512ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  393ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  319ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  339ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  391ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  356ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  507ms
 ✓ src/services/authSession.test.ts (36 tests) 40ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 26ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 60ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 46ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 36ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 12ms
 ✓ src/services/portalApi.test.ts (7 tests) 32ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 31ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 13ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4302ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2172ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  313ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 10ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 15ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 9ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 10ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2128ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1969ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  08:10:20
   Duration  7.96s (transform 4.56s, setup 0ms, collect 11.78s, tests 27.35s, environment 5.75s, prepare 2.49s)


Duration milliseconds: 8491
Exit code: 0
