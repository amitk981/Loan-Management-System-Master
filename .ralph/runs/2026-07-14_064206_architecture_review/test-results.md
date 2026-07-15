# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-14_064206_architecture_review/sfpcl-lms

 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 39ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 86ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 81ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 96ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 203ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 234ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 30ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 39ms
 ✓ src/services/authSession.test.ts (27 tests) 26ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 39ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 36ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 15ms
 ✓ src/services/portalApi.test.ts (4 tests) 10ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 6ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 11ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 12ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2960ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2069ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  445ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > exposes only approved staff demo controls when the flag is true  445ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 974ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  519ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1232ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  566ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  348ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1686ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  337ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  301ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2258ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1127ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  895ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 277ms
 ✓ src/pages/registers/RegistersHub.test.tsx (7 tests) 526ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1062ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  382ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (25 tests) 2684ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  366ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  422ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  355ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  578ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 2781ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1565ms

 Test Files  33 passed (33)
      Tests  269 passed (269)
   Start at  07:04:44
   Duration  7.60s (transform 5.05s, setup 0ms, collect 9.63s, tests 17.45s, environment 3.56s, prepare 2.11s)

