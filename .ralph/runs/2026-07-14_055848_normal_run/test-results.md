# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-14_055848_normal_run/sfpcl-lms

 ✓ src/pages/Dashboard.test.tsx (13 tests) 40ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 62ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 73ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 70ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 170ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 221ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 39ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 47ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 29ms
 ✓ src/services/authSession.test.ts (27 tests) 29ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 15ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/portalApi.test.ts (4 tests) 14ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 14ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 12ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3055ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2135ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  479ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > exposes only approved staff demo controls when the flag is true  440ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1263ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  893ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1510ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  647ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  458ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1964ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  418ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  347ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2512ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1209ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1045ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 287ms
 ✓ src/pages/registers/RegistersHub.test.tsx (7 tests) 539ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1100ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  398ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (25 tests) 3038ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  455ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  486ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  443ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  528ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 2885ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1619ms

 Test Files  33 passed (33)
      Tests  269 passed (269)
   Start at  06:21:51
   Duration  7.67s (transform 5.12s, setup 0ms, collect 9.34s, tests 19.07s, environment 3.43s, prepare 2.00s)

