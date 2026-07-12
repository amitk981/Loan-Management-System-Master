# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-13_011233_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (4 tests) 115ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 256ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 168ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 164ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 985ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  325ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 61ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1295ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 75ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 78ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 37ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 31ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 44ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 1844ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  935ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  695ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 29ms
 ✓ src/services/authSession.test.ts (15 tests) 14ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 30ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 11ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 11ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3199ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2721ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (15 tests) 7125ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback before an ordinary update readback  3132ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  1163ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  977ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  1126ms

 Test Files  29 passed (29)
      Tests  204 passed (204)
   Start at  01:20:42
   Duration  10.22s (transform 4.38s, setup 0ms, collect 7.17s, tests 15.63s, environment 2.27s, prepare 1.65s)

