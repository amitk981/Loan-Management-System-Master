# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-13_010017_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (4 tests) 147ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 248ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 165ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 141ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1038ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  321ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 74ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1312ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 74ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 69ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 31ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 38ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 1802ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  918ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  683ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 40ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 38ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 32ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 10ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 13ms
 ✓ src/services/authSession.test.ts (15 tests) 10ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 19ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 6ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 10ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3232ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2731ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 4ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (15 tests) 6996ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback before an ordinary update readback  3017ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  1159ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  963ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  1107ms

 Test Files  29 passed (29)
      Tests  204 passed (204)
   Start at  01:11:14
   Duration  10.05s (transform 4.39s, setup 0ms, collect 7.21s, tests 15.58s, environment 2.41s, prepare 1.69s)

