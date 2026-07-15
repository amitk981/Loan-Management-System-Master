# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-15_073659_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1020ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  593ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1206ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  454ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1263ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  581ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  333ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1714ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  328ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  307ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2439ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1178ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  985ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 685ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (5 tests) 497ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  365ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 515ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  417ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 312ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 73ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 168ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 78ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 181ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 60ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 38ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 44ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 46ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 29ms
 ✓ src/services/authSession.test.ts (36 tests) 36ms
(node:35403) ExperimentalWarning: buffer.File is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
 ✓ src/services/portalApi.test.ts (6 tests) 27ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 11ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 18ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 18ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 12ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2454ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2237ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5173ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  423ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  365ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  327ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  314ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  405ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  443ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  543ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 3562ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  1918ms

 Test Files  35 passed (35)
      Tests  302 passed (302)
   Start at  08:52:29
   Duration  6.94s (transform 5.30s, setup 0ms, collect 10.27s, tests 21.75s, environment 4.07s, prepare 2.18s)

