# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-14_070825_normal_run/sfpcl-lms

 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 46ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 69ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 40ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 79ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 214ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 207ms
 ✓ src/services/authSession.test.ts (27 tests) 26ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 29ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 45ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 69ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 22ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 9ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 15ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2967ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1956ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  412ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > exposes only approved staff demo controls when the flag is true  598ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 961ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  564ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1218ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  556ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  372ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1577ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  373ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2356ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1085ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  997ms
 ✓ src/pages/registers/RegistersHub.test.tsx (7 tests) 618ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 278ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1101ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  421ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (25 tests) 2774ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  316ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  376ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  372ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  604ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 2740ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1491ms

 Test Files  33 passed (33)
      Tests  269 passed (269)
   Start at  07:39:01
   Duration  7.37s (transform 4.54s, setup 0ms, collect 9.10s, tests 17.54s, environment 3.38s, prepare 1.95s)

