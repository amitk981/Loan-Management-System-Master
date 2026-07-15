# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-14_023135_normal_run/sfpcl-lms

 ✓ src/pages/Dashboard.test.tsx (13 tests) 44ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 61ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 70ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 65ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 212ms
 ✓ src/services/authSession.test.ts (17 tests) 24ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 225ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 44ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 36ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 40ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 12ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/services/navigationPermissions.test.ts (8 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 16ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 4ms
 ✓ src/services/approvalRegistersApi.test.ts (4 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3139ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2076ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  462ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > exposes only approved staff demo controls when the flag is true  601ms
 ✓ src/pages/settings/SettingsHub.test.tsx (9 tests) 1053ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  501ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  301ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1093ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  381ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1548ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  324ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  344ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2240ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1030ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  904ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 326ms
 ✓ src/pages/registers/RegistersHub.test.tsx (7 tests) 602ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 802ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  464ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (22 tests) 2549ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  380ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  338ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  327ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  679ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 2759ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1491ms

 Test Files  33 passed (33)
      Tests  253 passed (253)
   Start at  02:55:43
   Duration  7.24s (transform 4.64s, setup 0ms, collect 9.13s, tests 17.06s, environment 3.14s, prepare 2.05s)

