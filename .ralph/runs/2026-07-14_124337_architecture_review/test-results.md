# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-14_124337_architecture_review/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 796ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  333ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1057ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  601ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1756ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  654ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  423ms
   ✓ SettingsHub remaining panels > keeps server errors visible inside the successor modal and does not label a draft current  346ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2214ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  524ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the returned Credit Manager decision once  307ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  374ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 282ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2854ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1258ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1364ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 194ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1099ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  375ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 159ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 76ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 86ms
 ✓ src/services/authSession.test.ts (36 tests) 41ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 39ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 34ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 35ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 47ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 76ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 12ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 10ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 11ms
 ✓ src/services/portalApi.test.ts (4 tests) 6ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 4ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2890ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2385ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5560ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  399ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  766ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  394ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  325ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  325ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  337ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  304ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  567ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 3702ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2268ms

 Test Files  33 passed (33)
      Tests  293 passed (293)
   Start at  13:05:15
   Duration  7.78s (transform 6.07s, setup 0ms, collect 10.80s, tests 23.12s, environment 5.35s, prepare 2.20s)

