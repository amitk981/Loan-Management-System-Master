# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_215313_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1234ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  436ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1246ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  567ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  318ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1742ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  311ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2235ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1053ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  901ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2386ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  454ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  402ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1061ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  421ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1434ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  332ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  878ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 742ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  511ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 350ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 542ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  480ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 155ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 315ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 214ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 115ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 85ms
 ✓ src/services/authSession.test.ts (36 tests) 50ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 79ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 49ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 28ms
 ✓ src/services/portalApi.test.ts (6 tests) 18ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 35ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 26ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 19ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 10ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6040ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  480ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  353ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  306ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  308ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  395ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  580ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  328ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  337ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  751ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 10ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 22ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3055ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2455ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  442ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5098ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3028ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  348ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  22:49:34
   Duration  8.44s (transform 4.84s, setup 0ms, collect 11.99s, tests 28.44s, environment 5.46s, prepare 2.80s)


Duration milliseconds: 9160
Exit code: 0
