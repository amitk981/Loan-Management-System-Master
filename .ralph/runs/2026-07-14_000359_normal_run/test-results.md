# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-14_000359_normal_run/sfpcl-lms

 ✓ src/pages/Dashboard.test.tsx (13 tests) 52ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 61ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 72ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 82ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 192ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 214ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 30ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 35ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 31ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/services/authSession.test.ts (16 tests) 12ms
 ✓ src/services/navigationPermissions.test.ts (8 tests) 9ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 15ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/portalApi.test.ts (4 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/services/approvalRegistersApi.test.ts (4 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 6ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2942ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1991ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  472ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > exposes only approved staff demo controls when the flag is true  478ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 893ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  488ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1153ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  404ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1510ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  312ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2213ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1053ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  911ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 233ms
 ✓ src/pages/registers/RegistersHub.test.tsx (7 tests) 519ms
 ✓ src/pages/settings/SettingsHub.test.tsx (5 tests) 612ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  472ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (21 tests) 2351ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  390ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  375ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  332ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  538ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 2673ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1452ms

 Test Files  32 passed (32)
      Tests  245 passed (245)
   Start at  00:37:57
   Duration  6.97s (transform 4.73s, setup 0ms, collect 8.81s, tests 16.00s, environment 2.92s, prepare 1.98s)

