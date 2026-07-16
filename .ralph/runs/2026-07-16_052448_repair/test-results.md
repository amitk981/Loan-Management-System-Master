# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-16_052448_repair/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1020ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  675ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1279ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  613ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  353ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1690ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  320ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (14 tests) 1935ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  573ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  492ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2439ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1211ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  951ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 740ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 530ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  341ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 510ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  427ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1265ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  448ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 276ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 160ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 77ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 64ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 150ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 37ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 69ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 44ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 33ms
(node:57605) ExperimentalWarning: buffer.File is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
 ✓ src/services/portalApi.test.ts (6 tests) 26ms
 ✓ src/services/authSession.test.ts (36 tests) 30ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 41ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 10ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 31ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5381ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  473ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  415ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  317ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  313ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  310ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  329ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  368ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  663ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2573ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2190ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 3866ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2039ms

 Test Files  36 passed (36)
      Tests  319 passed (319)
   Start at  06:16:03
   Duration  7.05s (transform 5.19s, setup 0ms, collect 10.11s, tests 24.35s, environment 4.05s, prepare 2.24s)

