# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_174430_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1790ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  813ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1997ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  902ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  475ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2577ms
   ✓ default AppraisalWorkbench authenticated HTTP container > renders HTTP 400 once without retry or refresh  372ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  370ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  320ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2996ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1666ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  990ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3349ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  337ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  943ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  392ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  386ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1210ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  688ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 996ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  345ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  338ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 882ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  493ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 757ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  678ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 372ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 192ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (3 tests) 265ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 96ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 191ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 81ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 69ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 44ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 40ms
 ✓ src/services/authSession.test.ts (36 tests) 48ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 60ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 37ms
 ✓ src/services/portalApi.test.ts (7 tests) 34ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 42ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 22ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 15ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6944ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  960ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  432ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  361ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  337ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  363ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  328ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  427ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  453ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  465ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  422ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  875ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 9ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3205ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2776ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  343ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5204ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3058ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  390ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  38 passed (38)
      Tests  331 passed (331)
   Start at  18:55:11
   Duration  9.54s (transform 6.24s, setup 0ms, collect 15.17s, tests 33.58s, environment 6.93s, prepare 2.59s)


Duration milliseconds: 10079
Exit code: 0
