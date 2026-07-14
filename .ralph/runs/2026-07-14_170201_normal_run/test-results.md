# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-14_170201_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 974ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  301ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  362ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1242ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  837ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1848ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  778ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  650ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2511ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  686ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  458ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2935ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1274ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1365ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 396ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 188ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 123ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 190ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1221ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  407ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 62ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 6ms
 ✓ src/services/authSession.test.ts (36 tests) 48ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 43ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 95ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 57ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 56ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 45ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 20ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 41ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/services/portalApi.test.ts (4 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 19ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 11ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 14ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3200ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2627ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  353ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/services/tracerApi.test.ts (2 tests) 6ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6234ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  513ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  728ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  413ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  326ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  308ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  300ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  322ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  372ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  484ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  462ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  396ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4664ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3295ms

 Test Files  33 passed (33)
      Tests  293 passed (293)
   Start at  17:32:28
   Duration  8.74s (transform 6.32s, setup 0ms, collect 11.45s, tests 26.29s, environment 7.34s, prepare 2.47s)

