# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_211948_normal_run/sfpcl-lms

 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 233ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 272ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 200ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 95ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1173ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  420ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 76ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 38ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1610ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  309ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 29ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 71ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 38ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (4 tests) 2080ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1103ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  848ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 30ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3079ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2601ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 16ms
 ✓ src/services/authSession.test.ts (15 tests) 23ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 11ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 10ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 11ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 2ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 19ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (13 tests) 5030ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  2049ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  1334ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  1139ms

 Test Files  29 passed (29)
      Tests  199 passed (199)
   Start at  21:44:23
   Duration  6.15s (transform 2.92s, setup 0ms, collect 5.37s, tests 14.21s, environment 2.36s, prepare 1.87s)

