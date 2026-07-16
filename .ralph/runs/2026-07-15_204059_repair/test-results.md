# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-15_193120_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1115ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  664ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1302ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  473ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1295ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  576ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  366ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1827ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  324ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2424ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1164ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  931ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 550ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  466ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (7 tests) 651ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  447ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 814ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 306ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 87ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 170ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 160ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 150ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 70ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 41ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 62ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 37ms
 ✓ src/services/authSession.test.ts (36 tests) 39ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 41ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 31ms
(node:34660) ExperimentalWarning: buffer.File is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
 ✓ src/services/portalApi.test.ts (6 tests) 35ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 18ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 10ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 20ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 6ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 11ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2894ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2620ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5765ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  452ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  379ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  352ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  338ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  396ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  328ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  319ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  328ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  432ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  363ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  688ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4238ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2463ms

 Test Files  35 passed (35)
      Tests  304 passed (304)
   Start at  21:00:48
   Duration  7.59s (transform 5.14s, setup 0ms, collect 11.08s, tests 24.21s, environment 4.53s, prepare 2.26s)
