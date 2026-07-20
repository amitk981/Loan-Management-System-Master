# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_153054_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1159ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  410ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1365ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  620ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  339ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1798ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  338ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2217ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1129ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  812ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2446ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  496ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  441ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1025ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  598ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1111ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  373ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  454ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 792ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 608ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  391ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 576ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  472ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 398ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 354ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 306ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 161ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 245ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 75ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 138ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 57ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 159ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5579ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  516ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  405ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  338ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  315ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  320ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  381ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  377ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  591ms
 ✓ src/services/authSession.test.ts (36 tests) 31ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 31ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 41ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 89ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 45ms
 ✓ src/services/portalApi.test.ts (7 tests) 20ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 31ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 14ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4508ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2488ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 7ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2437ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2268ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  16:48:16
   Duration  8.34s (transform 5.03s, setup 0ms, collect 12.58s, tests 27.90s, environment 5.97s, prepare 2.66s)


Duration milliseconds: 8879
Exit code: 0
