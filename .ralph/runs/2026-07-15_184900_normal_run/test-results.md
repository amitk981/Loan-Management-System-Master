# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-15_184900_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1249ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  714ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1472ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  492ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1618ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  727ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  439ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2058ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  359ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  356ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2688ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1368ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  989ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 809ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  315ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (7 tests) 621ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  422ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 554ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  478ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 315ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 78ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 180ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 91ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 197ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 69ms
 ✓ src/services/authSession.test.ts (36 tests) 49ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 32ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 37ms
(node:8455) ExperimentalWarning: buffer.File is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
 ✓ src/services/portalApi.test.ts (6 tests) 34ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 35ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 42ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 14ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 4ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 4ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2747ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2506ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5618ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  523ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  397ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  383ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  303ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  363ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  358ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  736ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 3968ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2208ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  332ms

 Test Files  35 passed (35)
      Tests  304 passed (304)
   Start at  19:24:54
   Duration  7.76s (transform 6.36s, setup 0ms, collect 12.32s, tests 24.67s, environment 5.02s, prepare 2.23s)

