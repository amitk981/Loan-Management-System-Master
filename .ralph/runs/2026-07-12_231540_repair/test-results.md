# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_224547_normal_run/sfpcl-lms

 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 170ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 262ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 68ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 156ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1036ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  324ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 78ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 70ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1290ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 44ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 37ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 29ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 37ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 1862ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  920ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  712ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/services/authSession.test.ts (15 tests) 16ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 14ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3262ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2862ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (15 tests) 6948ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback before an ordinary update readback  2954ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  1153ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  975ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  1118ms

 Test Files  29 passed (29)
      Tests  202 passed (202)
   Start at  23:23:29
   Duration  10.30s (transform 4.88s, setup 0ms, collect 7.98s, tests 15.48s, environment 1.74s, prepare 1.64s)

