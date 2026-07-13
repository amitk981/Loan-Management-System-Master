# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-13_014006_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (4 tests) 164ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 226ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 173ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 163ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1001ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  333ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 73ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1295ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 64ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 63ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 37ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 41ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 1817ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  915ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  701ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 29ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 29ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/services/portalApi.test.ts (4 tests) 8ms
 ✓ src/services/authSession.test.ts (15 tests) 17ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 16ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 10ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 11ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3215ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2727ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (15 tests) 7003ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback before an ordinary update readback  3030ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  1142ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  961ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  1113ms

 Test Files  29 passed (29)
      Tests  204 passed (204)
   Start at  02:31:44
   Duration  9.98s (transform 4.40s, setup 0ms, collect 7.13s, tests 15.53s, environment 2.30s, prepare 1.71s)

