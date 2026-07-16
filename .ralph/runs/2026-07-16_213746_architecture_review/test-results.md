# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-16_213746_architecture_review/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 793ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1357ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  333ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  811ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1534ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  694ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  444ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2180ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  363ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  370ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 601ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  392ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2792ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  668ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  425ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  334ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 543ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  478ms
 ✓ src/services/authSession.test.ts (36 tests) 36ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 174ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 359ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 69ms
 ✓ src/services/portalApi.test.ts (6 tests) 22ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 12ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 200ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1225ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  433ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 69ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2402ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1197ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  915ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 57ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 36ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 78ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 55ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 31ms
 ✓ src/services/tracerApi.test.ts (2 tests) 9ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 14ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 29ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5877ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  529ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  396ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  353ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  316ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  320ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  321ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  352ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  309ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  365ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  358ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  592ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4625ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2502ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  352ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1273ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1173ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  21:54:20
   Duration  8.12s (transform 4.56s, setup 0ms, collect 12.39s, tests 26.51s, environment 4.78s, prepare 3.01s)


Duration milliseconds: 8878
Exit code: 0
