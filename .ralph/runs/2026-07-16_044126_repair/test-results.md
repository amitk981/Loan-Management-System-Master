# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-16_033311_repair/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1236ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  416ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1185ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  570ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  302ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1694ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  354ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  307ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (14 tests) 1827ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  518ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  417ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2426ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1156ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  944ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 783ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 966ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  556ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 624ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  360ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 526ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  448ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 262ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 71ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 177ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 174ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 64ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 85ms
 ✓ src/services/authSession.test.ts (36 tests) 38ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 48ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 39ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 37ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 35ms
(node:33783) ExperimentalWarning: buffer.File is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
 ✓ src/services/portalApi.test.ts (6 tests) 23ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 29ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 16ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5223ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  436ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  333ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  335ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  322ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  362ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  365ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  347ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  332ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  598ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 4ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2365ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2085ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 3812ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2020ms

 Test Files  36 passed (36)
      Tests  319 passed (319)
   Start at  05:03:12
   Duration  6.86s (transform 5.03s, setup 0ms, collect 9.96s, tests 23.83s, environment 4.31s, prepare 2.20s)

