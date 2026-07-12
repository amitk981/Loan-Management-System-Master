# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-13_014006_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (4 tests) 155ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 274ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 159ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 176ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 995ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  327ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 71ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1297ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 68ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 58ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 36ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 39ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 1868ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  937ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  712ms
 ✓ src/services/authSession.test.ts (15 tests) 19ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 14ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 37ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 16ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 22ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 14ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 6ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3138ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2688ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 4ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (15 tests) 7006ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback before an ordinary update readback  3022ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  1154ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  969ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  1106ms

 Test Files  29 passed (29)
      Tests  204 passed (204)
   Start at  01:54:11
   Duration  9.98s (transform 4.33s, setup 0ms, collect 6.89s, tests 15.56s, environment 2.30s, prepare 1.66s)

