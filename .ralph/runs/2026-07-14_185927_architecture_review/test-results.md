# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-14_185927_architecture_review/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 854ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  304ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1165ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  314ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  661ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1423ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  582ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  414ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1872ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  402ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  383ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2396ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1119ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1050ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 272ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 274ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 83ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 162ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1177ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  414ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 161ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 107ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 49ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 54ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 14ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 55ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 34ms
 ✓ src/services/authSession.test.ts (36 tests) 41ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 71ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/services/portalApi.test.ts (4 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 12ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 6ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 9ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 4ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3165ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2599ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5501ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  434ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  439ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  370ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  339ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  392ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  401ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  401ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  521ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4100ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2764ms

 Test Files  33 passed (33)
      Tests  293 passed (293)
   Start at  19:26:05
   Duration  7.97s (transform 5.81s, setup 0ms, collect 10.72s, tests 23.11s, environment 4.61s, prepare 2.70s)

