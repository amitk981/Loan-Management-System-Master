# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_224547_normal_run/sfpcl-lms

 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 190ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 245ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 146ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 75ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 989ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  308ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 77ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1229ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 65ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 37ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 45ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 31ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 37ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 29ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 1917ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  985ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  721ms
 ✓ src/services/authSession.test.ts (15 tests) 12ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 13ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 6ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3207ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2782ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (14 tests) 6851ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback before an ordinary update readback  2969ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  1166ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  953ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  1121ms

 Test Files  29 passed (29)
      Tests  201 passed (201)
   Start at  23:05:49
   Duration  10.14s (transform 4.65s, setup 0ms, collect 7.83s, tests 15.27s, environment 1.69s, prepare 1.66s)

