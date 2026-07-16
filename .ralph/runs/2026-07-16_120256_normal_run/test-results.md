# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-16_120256_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1142ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  700ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1394ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  666ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  350ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1829ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  353ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  311ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (17 tests) 2274ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  548ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  465ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2396ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1168ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  955ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 737ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1185ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  435ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 556ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  359ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 313ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 523ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  457ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 178ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 88ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 172ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 100ms
 ✓ src/services/authSession.test.ts (36 tests) 28ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 63ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 41ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 49ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 33ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 30ms
(node:96544) ExperimentalWarning: buffer.File is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
 ✓ src/services/portalApi.test.ts (6 tests) 27ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 39ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 9ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 10ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 11ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 9ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 11ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5230ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  434ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  361ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  301ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  369ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  309ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  301ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  312ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  376ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  560ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/services/tracerApi.test.ts (2 tests) 6ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2377ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1998ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4035ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2155ms

 Test Files  36 passed (36)
      Tests  322 passed (322)
   Start at  12:55:25
   Duration  6.96s (transform 4.85s, setup 0ms, collect 9.68s, tests 24.93s, environment 4.65s, prepare 2.22s)

