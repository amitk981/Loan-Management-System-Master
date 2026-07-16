# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-16_224541_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1222ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  439ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1271ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  593ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  334ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1759ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  342ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  314ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2263ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1045ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  929ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2368ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  452ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  401ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 917ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  537ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 763ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 636ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  440ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 300ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 145ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 525ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  434ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 224ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 79ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 62ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 76ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 26ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 41ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 56ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/services/authSession.test.ts (36 tests) 42ms
 ✓ src/services/portalApi.test.ts (6 tests) 19ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 35ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 14ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 21ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 20ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5444ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  533ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  461ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  303ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  419ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  364ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  330ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  316ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  305ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  517ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 12ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2606ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2196ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4166ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2241ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  23:09:15
   Duration  7.15s (transform 4.36s, setup 0ms, collect 10.32s, tests 25.18s, environment 4.12s, prepare 2.30s)


Duration milliseconds: 7688
Exit code: 0
