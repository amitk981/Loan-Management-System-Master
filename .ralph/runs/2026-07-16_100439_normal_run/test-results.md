# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-16_100439_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1358ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  654ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  356ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1407ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  549ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1937ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  360ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  343ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (17 tests) 2444ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  507ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  454ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2658ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1337ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1004ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1012ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 936ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  701ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1535ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  1090ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 326ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 565ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  376ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 79ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 243ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 83ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 93ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 214ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 46ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 48ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 33ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
(node:50669) ExperimentalWarning: buffer.File is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
 ✓ src/services/portalApi.test.ts (6 tests) 28ms
 ✓ src/services/authSession.test.ts (36 tests) 37ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 11ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 11ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6156ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  514ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  388ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  371ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  307ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  389ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  421ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  646ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  322ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  384ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  401ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  645ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 4ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2759ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2407ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4820ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2995ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  318ms

 Test Files  36 passed (36)
      Tests  322 passed (322)
   Start at  11:01:58
   Duration  8.52s (transform 5.62s, setup 0ms, collect 11.41s, tests 28.96s, environment 6.18s, prepare 2.35s)

