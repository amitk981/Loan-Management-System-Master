# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-14_025903_normal_run/sfpcl-lms

 ✓ src/pages/Dashboard.test.tsx (13 tests) 47ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 65ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 84ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 70ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 199ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 193ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 29ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 37ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 30ms
 ✓ src/services/authSession.test.ts (17 tests) 39ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 18ms
 ✓ src/services/approvalRegistersApi.test.ts (4 tests) 6ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/navigationPermissions.test.ts (8 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 23ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 10ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 12ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 14ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/services/tracerApi.test.ts (2 tests) 10ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3238ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2305ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  483ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > exposes only approved staff demo controls when the flag is true  449ms
 ✓ src/pages/settings/SettingsHub.test.tsx (9 tests) 1161ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  527ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  316ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1197ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  408ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1547ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  306ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  321ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2132ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  980ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  870ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 284ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 799ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  434ms
 ✓ src/pages/registers/RegistersHub.test.tsx (7 tests) 509ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (22 tests) 2603ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  451ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  353ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  338ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  688ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 2736ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1500ms

 Test Files  33 passed (33)
      Tests  253 passed (253)
   Start at  03:17:57
   Duration  7.20s (transform 5.06s, setup 0ms, collect 9.05s, tests 17.15s, environment 3.36s, prepare 2.03s)

