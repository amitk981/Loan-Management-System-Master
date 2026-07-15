# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-15_073659_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1184ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  427ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1222ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  573ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  328ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1329ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  368ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  793ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1990ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  407ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 310ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2501ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1191ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  990ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (5 tests) 516ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  395ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 733ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 179ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 66ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 473ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  383ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 202ms
 ✓ src/services/authSession.test.ts (36 tests) 38ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 86ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 89ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 35ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 56ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 49ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 41ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 36ms
(node:27467) ExperimentalWarning: buffer.File is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
 ✓ src/services/portalApi.test.ts (6 tests) 30ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 11ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 10ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 15ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 12ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 15ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 14ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 13ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 4ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2580ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2228ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5476ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  502ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  445ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  334ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  315ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  306ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  304ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  312ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  374ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  321ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  561ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4043ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2334ms

 Test Files  35 passed (35)
      Tests  302 passed (302)
   Start at  08:25:06
   Duration  7.10s (transform 5.14s, setup 0ms, collect 10.05s, tests 23.38s, environment 4.29s, prepare 2.15s)

