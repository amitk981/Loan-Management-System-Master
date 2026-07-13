# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_224547_normal_run/sfpcl-lms

 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 172ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 253ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 60ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 162ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1000ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  305ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 74ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1354ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 68ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 34ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (4 tests) 1797ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  988ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  694ms
 ✓ src/services/authSession.test.ts (15 tests) 13ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 30ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 36ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 62ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 6ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 12ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 11ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 17ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 8ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3202ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2807ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (14 tests) 6846ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback before an ordinary update readback  2977ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  1142ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  970ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  1118ms

 Test Files  29 passed (29)
      Tests  200 passed (200)
   Start at  22:54:40
   Duration  10.01s (transform 4.86s, setup 0ms, collect 7.69s, tests 15.28s, environment 1.63s, prepare 1.68s)

