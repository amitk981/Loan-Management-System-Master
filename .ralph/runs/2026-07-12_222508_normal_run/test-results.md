# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-12_222508_normal_run/sfpcl-lms

 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 141ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 274ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 188ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 76ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 65ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1099ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  376ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 66ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1383ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 37ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 39ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 29ms
 ✓ src/services/authSession.test.ts (15 tests) 10ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 31ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 30ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 9ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2585ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2147ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (4 tests) 2004ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1006ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  827ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 13ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 22ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 11ms
 ✓ src/services/portalApi.test.ts (4 tests) 10ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (2 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (13 tests) 4759ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  1894ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  1165ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  1098ms

 Test Files  29 passed (29)
      Tests  199 passed (199)
   Start at  22:34:12
   Duration  5.87s (transform 2.69s, setup 0ms, collect 4.73s, tests 12.92s, environment 1.94s, prepare 1.75s)

