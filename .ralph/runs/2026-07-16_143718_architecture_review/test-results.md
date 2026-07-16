# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-16_143718_architecture_review/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1288ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  492ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1390ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  659ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  385ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1894ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  328ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  359ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2557ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1297ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  968ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (17 tests) 2582ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  606ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  417ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 930ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  344ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1256ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  697ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 638ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  402ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 379ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 517ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  443ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 241ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 71ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 227ms
 ✓ src/services/authSession.test.ts (36 tests) 57ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 86ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 32ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 63ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 106ms
(node:32930) ExperimentalWarning: buffer.File is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
 ✓ src/services/portalApi.test.ts (6 tests) 21ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 38ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 33ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5956ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  432ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  338ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  367ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  328ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  320ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  348ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  450ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  369ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  365ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  370ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  819ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 6ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2628ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2298ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4616ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2768ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  330ms

 Test Files  36 passed (36)
      Tests  322 passed (322)
   Start at  15:10:50
   Duration  8.23s (transform 5.28s, setup 0ms, collect 11.20s, tests 27.71s, environment 5.99s, prepare 2.46s)

