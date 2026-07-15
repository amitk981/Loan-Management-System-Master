# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-16_000538_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1040ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  604ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1193ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  432ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1240ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  607ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  334ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1583ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  330ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2284ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1095ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  926ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 828ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 650ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  397ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (6 tests) 742ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 552ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  490ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 260ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 75ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 182ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 177ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 83ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 51ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 74ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 41ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/services/authSession.test.ts (36 tests) 33ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 37ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
(node:69077) ExperimentalWarning: buffer.File is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
 ✓ src/services/portalApi.test.ts (6 tests) 20ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 15ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 11ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 6ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2349ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2069ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5227ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  377ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  329ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  352ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  320ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  335ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  388ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  380ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  376ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  562ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 3870ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2221ms

 Test Files  36 passed (36)
      Tests  311 passed (311)
   Start at  02:23:48
   Duration  6.96s (transform 4.94s, setup 0ms, collect 9.62s, tests 22.73s, environment 4.02s, prepare 2.19s)

