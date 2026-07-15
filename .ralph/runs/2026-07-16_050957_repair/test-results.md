# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-16_033311_repair/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1124ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  386ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1275ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  602ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  361ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1654ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  326ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (14 tests) 1968ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  593ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  472ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2463ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1154ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  974ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 974ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  583ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 761ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  300ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 575ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  389ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 501ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  418ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 262ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 181ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 84ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 160ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 73ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 44ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 62ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 38ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 50ms
 ✓ src/services/authSession.test.ts (36 tests) 42ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
(node:40480) ExperimentalWarning: buffer.File is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
 ✓ src/services/portalApi.test.ts (6 tests) 24ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 31ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 4ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5440ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  419ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  351ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  334ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  374ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  340ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  352ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  313ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  368ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  332ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  640ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2414ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2104ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 3947ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2071ms

 Test Files  36 passed (36)
      Tests  319 passed (319)
   Start at  05:17:38
   Duration  6.99s (transform 4.74s, setup 0ms, collect 9.87s, tests 24.25s, environment 4.04s, prepare 2.21s)

