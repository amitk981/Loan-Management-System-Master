# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-14_155832_architecture_review/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1111ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  703ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1431ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  697ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  351ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1488ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  573ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1974ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  394ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  352ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2638ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1292ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1118ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 305ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 176ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 761ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 68ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 78ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 216ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 76ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 46ms
 ✓ src/services/authSession.test.ts (36 tests) 42ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 40ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 38ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 34ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 30ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 13ms
 ✓ src/services/portalApi.test.ts (4 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 6ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 13ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3295ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2883ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  320ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5451ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  539ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  403ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  351ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  319ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  335ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  350ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  376ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  350ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  440ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 3785ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2385ms

 Test Files  33 passed (33)
      Tests  293 passed (293)
   Start at  16:22:21
   Duration  7.50s (transform 6.11s, setup 0ms, collect 10.82s, tests 23.17s, environment 4.35s, prepare 2.05s)

