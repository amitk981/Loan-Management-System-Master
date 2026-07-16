# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-16_111411_repair/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1202ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  759ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1378ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  650ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  367ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1785ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  347ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2496ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1241ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  997ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (17 tests) 2574ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  527ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  465ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  328ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 704ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 480ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  399ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1255ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  425ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 571ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  320ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 181ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 342ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 254ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 56ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 46ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 93ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 47ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 79ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 31ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 69ms
 ✓ src/services/authSession.test.ts (36 tests) 37ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
(node:66410) ExperimentalWarning: buffer.File is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
 ✓ src/services/portalApi.test.ts (6 tests) 22ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 41ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5265ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  443ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  376ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  348ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  334ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  316ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  393ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  304ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  534ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 26ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 14ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 4ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2831ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2362ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4149ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2180ms

 Test Files  36 passed (36)
      Tests  322 passed (322)
   Start at  11:53:17
   Duration  7.35s (transform 5.11s, setup 0ms, collect 10.43s, tests 26.09s, environment 4.98s, prepare 2.24s)

