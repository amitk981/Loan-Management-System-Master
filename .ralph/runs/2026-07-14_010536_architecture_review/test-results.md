# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-14_010536_architecture_review/sfpcl-lms

 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 32ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 61ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 82ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 74ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 184ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 193ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 32ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 37ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 37ms
 ✓ src/services/authSession.test.ts (16 tests) 11ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 42ms
 ✓ src/services/navigationPermissions.test.ts (8 tests) 13ms
 ✓ src/services/approvalRegistersApi.test.ts (4 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 16ms
 ✓ src/services/portalApi.test.ts (4 tests) 8ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2902ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2075ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  448ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > exposes only approved staff demo controls when the flag is true  378ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1071ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  362ms
 ✓ src/pages/settings/SettingsHub.test.tsx (9 tests) 1084ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  513ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  311ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1449ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  304ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 280ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2228ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  986ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  963ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 775ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  442ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (21 tests) 2361ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  403ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  340ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  310ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  584ms
 ✓ src/pages/registers/RegistersHub.test.tsx (7 tests) 518ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 2773ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1487ms

 Test Files  33 passed (33)
      Tests  251 passed (251)
   Start at  01:32:08
   Duration  7.02s (transform 4.41s, setup 0ms, collect 8.48s, tests 16.32s, environment 3.20s, prepare 1.97s)

