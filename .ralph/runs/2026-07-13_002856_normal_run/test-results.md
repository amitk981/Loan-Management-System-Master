# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-13_002856_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (4 tests) 140ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 254ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 164ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 147ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1072ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  357ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 77ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1334ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 62ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 69ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 41ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 36ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 33ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 1891ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  953ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  728ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 35ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 30ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 18ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/authSession.test.ts (15 tests) 14ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 11ms
 ✓ src/services/navigationPermissions.test.ts (7 tests) 13ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (2 tests) 8ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 15ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3331ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2814ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (15 tests) 7066ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback before an ordinary update readback  3073ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  1155ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  977ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  1131ms

 Test Files  29 passed (29)
      Tests  204 passed (204)
   Start at  00:43:40
   Duration  10.17s (transform 4.54s, setup 0ms, collect 7.39s, tests 15.90s, environment 2.41s, prepare 1.66s)

