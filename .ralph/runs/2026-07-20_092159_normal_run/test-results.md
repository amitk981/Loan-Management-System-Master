# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_092159_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 836ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  308ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1159ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  383ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  558ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1466ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  720ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  362ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1951ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  359ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  303ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 537ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  335ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2617ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  578ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  410ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 332ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 513ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  433ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 172ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1135ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  375ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 350ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 948ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  329ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  381ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2379ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1195ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  906ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 228ms
 ✓ src/services/authSession.test.ts (36 tests) 39ms
 ✓ src/services/portalApi.test.ts (7 tests) 19ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 13ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 153ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 67ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 283ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5189ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  423ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  373ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  334ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  314ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  311ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  309ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  371ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  355ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  555ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 10ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 162ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 108ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 9ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 9ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 29ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 61ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 50ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 62ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 8ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4453ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2345ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 35ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1033ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  936ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  09:53:51
   Duration  8.28s (transform 4.01s, setup 0ms, collect 12.85s, tests 26.46s, environment 5.64s, prepare 2.57s)


Duration milliseconds: 9106
Exit code: 0
