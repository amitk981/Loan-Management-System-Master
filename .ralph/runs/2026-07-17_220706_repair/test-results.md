# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_215313_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1351ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  439ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1288ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  617ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  346ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1688ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  341ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2455ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1256ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  920ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2435ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  494ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  444ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 857ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  316ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1064ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  606ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 735ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  509ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 355ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 485ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  416ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 160ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 190ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 71ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 54ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 44ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 72ms
 ✓ src/services/authSession.test.ts (36 tests) 40ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 37ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 29ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 36ms
 ✓ src/services/portalApi.test.ts (6 tests) 20ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 37ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5243ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  382ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  371ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  315ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  383ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  355ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  433ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  324ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  612ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 23ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 15ms
 ✓ src/services/tracerApi.test.ts (2 tests) 6ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 11ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2651ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2324ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4227ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2467ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  306ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  22:18:39
   Duration  7.91s (transform 5.20s, setup 0ms, collect 11.77s, tests 25.73s, environment 4.62s, prepare 2.34s)


Duration milliseconds: 8425
Exit code: 0
