# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-16_165237_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1078ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  351ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  391ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1381ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  451ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  733ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1513ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  669ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  432ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2566ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  516ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  559ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 2468ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  1909ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 1720ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  1575ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 5856ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  386ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  623ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  641ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  1984ms
   ✓ 008M2 documentation workspace contract > executes a returned security action instead of navigating away  370ms
 ✓ src/services/authSession.test.ts (36 tests) 52ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 446ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 148ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 5291ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  3269ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1633ms
 ✓ src/services/portalApi.test.ts (6 tests) 29ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1564ms
   ✓ mounted witness resource actions > retains Contact correction server facts after one 400 failure without refetch  384ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  425ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 426ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 30ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 400ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 19ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 9ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 144ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 30ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 161ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 71ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 115ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 70ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 69ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 65ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 10ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 19ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 13ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 10619ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  694ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  631ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  538ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  1344ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  1287ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  578ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  792ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  502ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  460ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  439ms
   ✓ SanctionWorkbench authenticated container > surfaces CONFLICTED_APPROVER_NOT_ALLOWED without fabricating completion or refetching  319ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  1118ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1297ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1173ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 9862ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  8096ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  432ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  303ms

 Test Files  36 passed (36)
      Tests  323 passed (323)
   Start at  17:23:52
   Duration  13.36s (transform 4.78s, setup 0ms, collect 16.64s, tests 47.57s, environment 9.28s, prepare 3.81s)


Duration milliseconds: 13955
Exit code: 0
