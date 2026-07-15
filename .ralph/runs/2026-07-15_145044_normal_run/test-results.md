# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-15_145044_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1236ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  328ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  704ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1383ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  428ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1508ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  678ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  448ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1918ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  345ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  334ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2516ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1265ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  967ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (6 tests) 495ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  321ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 528ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  447ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 753ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 325ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 47ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 241ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 202ms
 ✓ src/services/authSession.test.ts (36 tests) 31ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 92ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 72ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 38ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 109ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 52ms
(node:89044) ExperimentalWarning: buffer.File is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
 ✓ src/services/portalApi.test.ts (6 tests) 32ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 44ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 13ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 40ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 11ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 6ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2805ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2354ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  307ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5653ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  516ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  429ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  326ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  360ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  355ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  313ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  343ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  706ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4342ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3069ms

 Test Files  35 passed (35)
      Tests  303 passed (303)
   Start at  15:07:55
   Duration  7.99s (transform 5.58s, setup 0ms, collect 10.56s, tests 24.55s, environment 5.45s, prepare 2.35s)

