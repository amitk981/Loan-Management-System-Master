# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-14_084216_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1239ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  432ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  624ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1350ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  464ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1368ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  716ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  323ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1838ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  336ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 257ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2427ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1257ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  884ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 225ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 777ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  368ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 89ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 214ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 75ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 37ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 103ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (33 tests) 3320ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  374ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  374ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  307ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  687ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 63ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 52ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 55ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 40ms
 ✓ src/services/authSession.test.ts (36 tests) 43ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 19ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 12ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 23ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 12ms
 ✓ src/services/portalApi.test.ts (4 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 14ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2864ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2378ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 3927ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2685ms

 Test Files  33 passed (33)
      Tests  287 passed (287)
   Start at  09:26:44
   Duration  7.28s (transform 5.50s, setup 0ms, collect 9.89s, tests 20.49s, environment 3.90s, prepare 2.18s)

