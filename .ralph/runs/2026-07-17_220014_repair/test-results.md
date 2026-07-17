# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_215313_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 855ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1175ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  778ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1466ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  602ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  369ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1859ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  343ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  324ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2485ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  572ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  445ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 580ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  379ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 513ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  430ms
 ✓ src/services/authSession.test.ts (36 tests) 42ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 184ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 331ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 61ms
 ✓ src/services/portalApi.test.ts (6 tests) 29ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 161ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 10ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1260ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  405ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2243ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1099ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  878ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 9ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 13ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 88ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 66ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 55ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 44ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 38ms
 ✓ src/services/tracerApi.test.ts (2 tests) 9ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 18ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 35ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 17ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5658ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  626ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  411ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  323ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  339ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  324ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  356ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  380ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  712ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4421ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2510ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1377ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1239ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  22:06:21
   Duration  7.72s (transform 4.40s, setup 0ms, collect 11.57s, tests 25.17s, environment 4.74s, prepare 2.30s)


Duration milliseconds: 8557
Exit code: 0
