# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-16_080903_repair/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1054ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  597ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1462ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  711ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  365ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1693ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  357ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  307ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2470ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1212ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  970ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (16 tests) 2470ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  568ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  487ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 688ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 571ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  364ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1309ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  479ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 293ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 427ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  371ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 232ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 196ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 100ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 75ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 66ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 43ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 39ms
 ✓ src/services/authSession.test.ts (36 tests) 35ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 27ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 29ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 36ms
(node:7764) ExperimentalWarning: buffer.File is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
 ✓ src/services/portalApi.test.ts (6 tests) 33ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 6ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5276ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  370ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  375ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  313ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  309ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  345ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  309ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  360ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  408ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  546ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 15ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 14ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2598ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2370ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4054ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2213ms

 Test Files  36 passed (36)
      Tests  321 passed (321)
   Start at  09:13:01
   Duration  7.51s (transform 5.80s, setup 0ms, collect 11.10s, tests 25.36s, environment 5.27s, prepare 2.35s)

