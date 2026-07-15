# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-15_052444_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 918ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  584ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1170ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  408ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1296ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  628ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  308ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1637ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  330ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  314ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 238ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2299ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1165ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  862ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 158ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 614ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 69ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 175ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 81ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 77ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 36ms
 ✓ src/services/authSession.test.ts (36 tests) 30ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 37ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 33ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 13ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 31ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 11ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 31ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 14ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 12ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/services/portalApi.test.ts (4 tests) 9ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 12ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 4ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2575ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2058ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 4788ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  440ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  372ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  311ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  307ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  324ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  335ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  339ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  488ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 3305ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1887ms

 Test Files  33 passed (33)
      Tests  293 passed (293)
   Start at  06:34:45
   Duration  6.43s (transform 4.66s, setup 0ms, collect 9.02s, tests 19.70s, environment 3.60s, prepare 2.09s)

