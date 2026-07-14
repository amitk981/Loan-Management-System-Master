# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-14_183058_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1597ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  398ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  986ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1680ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  578ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1724ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  838ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  453ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2364ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  356ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  332ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2817ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1554ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  989ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 318ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 194ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 742ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 81ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 193ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 90ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 61ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 37ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 37ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 34ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 35ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 39ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 12ms
 ✓ src/services/authSession.test.ts (36 tests) 47ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3088ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2487ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > exposes only approved staff demo controls when the flag is true  310ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 16ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5707ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  581ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  391ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  375ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  323ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  348ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  348ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  311ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  392ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  473ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 3812ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2310ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  328ms

 Test Files  33 passed (33)
      Tests  293 passed (293)
   Start at  18:54:24
   Duration  7.71s (transform 5.77s, setup 0ms, collect 10.24s, tests 24.79s, environment 4.96s, prepare 2.43s)

