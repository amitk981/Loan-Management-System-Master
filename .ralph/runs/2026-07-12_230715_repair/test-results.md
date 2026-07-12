# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_224547_normal_run/sfpcl-lms

 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 165ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 252ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 71ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 155ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1014ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  344ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 75ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 65ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1280ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 32ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 42ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 37ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 1825ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  922ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  691ms
 ✓ src/services/portalApi.test.ts (4 tests) 10ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 29ms
 ✓ src/services/authSession.test.ts (15 tests) 13ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 16ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 15ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 19ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 3ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3108ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2649ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (15 tests) 6888ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback before an ordinary update readback  2988ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  1145ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  932ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  1092ms

 Test Files  29 passed (29)
      Tests  202 passed (202)
   Start at  23:14:13
   Duration  9.88s (transform 4.58s, setup 0ms, collect 7.36s, tests 15.19s, environment 1.66s, prepare 1.64s)

