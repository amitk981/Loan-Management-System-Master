# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-15_181520_architecture_review/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1018ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  597ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1240ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  443ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1321ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  616ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  372ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1698ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  355ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2358ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1122ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  965ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 730ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (7 tests) 546ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  339ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 520ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  437ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 283ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 66ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 82ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 173ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 175ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 31ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 59ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 37ms
 ✓ src/services/authSession.test.ts (36 tests) 33ms
(node:91912) ExperimentalWarning: buffer.File is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
 ✓ src/services/portalApi.test.ts (6 tests) 21ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 33ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 41ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 6ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 4ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 10ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2442ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2154ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5030ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  432ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  351ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  301ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  303ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  350ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  402ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  388ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  546ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 3674ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2167ms

 Test Files  35 passed (35)
      Tests  304 passed (304)
   Start at  18:42:57
   Duration  6.99s (transform 5.31s, setup 0ms, collect 10.42s, tests 21.72s, environment 4.63s, prepare 2.10s)

