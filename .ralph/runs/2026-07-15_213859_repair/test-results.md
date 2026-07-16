# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-15_213859_repair/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1173ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  332ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  620ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1233ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  467ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1332ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  625ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  329ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1863ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  344ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  325ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2398ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1151ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  948ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 655ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  362ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 743ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  676ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 935ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  336ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 303ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 31ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 197ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 837ms
   ✓ Borrower360View > renders API-backed borrower, KYC, shareholding, land, crop, nominee, and bank metadata without mock remnants  763ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 1424ms
   ✓ Appraisal Workbench server-state rendering > gates server state review_pending  338ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 109ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 99ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 55ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 58ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 61ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 36ms
 ✓ src/services/authSession.test.ts (36 tests) 41ms
(node:70604) ExperimentalWarning: buffer.File is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
 ✓ src/services/portalApi.test.ts (6 tests) 35ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 34ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 12ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 20ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 4166ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  3600ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  323ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 7168ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  496ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  371ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  301ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  372ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  431ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  1660ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  596ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  739ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5873ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  4113ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  318ms

 Test Files  35 passed (35)
      Tests  305 passed (305)
   Start at  21:58:17
   Duration  9.03s (transform 6.09s, setup 0ms, collect 11.93s, tests 30.94s, environment 4.50s, prepare 3.17s)

