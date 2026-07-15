# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-15_093310_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1297ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  360ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  723ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1289ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  435ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1296ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  569ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  327ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1858ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  316ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2415ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1213ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  895ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 539ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  465ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (5 tests) 572ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  365ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 852ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 441ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 202ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 113ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 96ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 243ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 39ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 72ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 46ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 40ms
(node:71415) ExperimentalWarning: buffer.File is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
 ✓ src/services/portalApi.test.ts (6 tests) 21ms
 ✓ src/services/authSession.test.ts (36 tests) 34ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 35ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 16ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 10ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2969ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2559ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5842ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  651ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  428ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  320ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  328ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  374ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  515ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  399ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  337ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  413ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  399ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  499ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4417ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2816ms

 Test Files  35 passed (35)
      Tests  302 passed (302)
   Start at  10:14:10
   Duration  7.69s (transform 5.60s, setup 0ms, collect 10.94s, tests 24.84s, environment 4.82s, prepare 2.36s)

