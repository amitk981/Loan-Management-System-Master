# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_201120_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1388ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  460ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1598ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  655ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  448ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2338ms
   ✓ default AppraisalWorkbench authenticated HTTP container > runs eligibility with the exact request and performs one canonical four-read refresh  456ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  472ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  330ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2433ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1228ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  912ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3197ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  648ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  564ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  487ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 919ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  335ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1365ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  772ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 600ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  497ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 743ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  456ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 359ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 242ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 160ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 75ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 77ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 107ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 53ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 45ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 57ms
 ✓ src/services/authSession.test.ts (36 tests) 30ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 29ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 9ms
 ✓ src/services/portalApi.test.ts (6 tests) 47ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 47ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 14ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 15ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6378ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  691ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  494ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  367ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  327ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  419ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  345ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  425ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  349ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  406ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  396ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  645ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 23ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 14ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 16ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3171ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2712ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  317ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5520ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3336ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  306ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  392ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  21:01:43
   Duration  9.23s (transform 5.38s, setup 0ms, collect 13.48s, tests 31.10s, environment 6.48s, prepare 2.93s)


Duration milliseconds: 10169
Exit code: 0
