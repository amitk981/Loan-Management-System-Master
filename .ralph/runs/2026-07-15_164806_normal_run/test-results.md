# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-15_164806_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1236ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  671ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1288ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  478ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1492ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  628ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  429ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2425ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  441ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  709ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 3454ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1430ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1476ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (7 tests) 1137ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  833ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 1120ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  1012ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1655ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  597ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  541ms
   ✓ RegistersHub owned approval register panels > loads S25 independently with immutable comments and evidence but no inferred download  320ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 499ms
   ✓ MemberProfile container > preserves approval 400 VALIDATION_ERROR after one POST and no canonical refetch  302ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 79ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 342ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 378ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 136ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 238ms
(node:59948) ExperimentalWarning: buffer.File is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
 ✓ src/services/portalApi.test.ts (6 tests) 82ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 115ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 76ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 70ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 37ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 38ms
 ✓ src/services/authSession.test.ts (36 tests) 50ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 19ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 11ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 11ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 13ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 12ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 9ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3689ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  3045ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  309ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > exposes only approved staff demo controls when the flag is true  334ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 8016ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  456ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  510ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  653ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  459ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  634ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  559ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  674ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  327ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  588ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  610ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  890ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 6452ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  4860ms

 Test Files  35 passed (35)
      Tests  304 passed (304)
   Start at  17:06:01
   Duration  10.70s (transform 6.82s, setup 0ms, collect 13.69s, tests 34.21s, environment 7.08s, prepare 3.20s)

