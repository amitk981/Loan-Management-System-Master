# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-15_085859_architecture_review/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1163ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  435ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1288ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  329ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  734ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1210ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  560ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  344ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1964ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  343ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2311ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1144ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  875ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (5 tests) 481ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  338ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 501ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  430ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 703ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 375ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 78ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 238ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 174ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 90ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 46ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 88ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 51ms
 ✓ src/services/authSession.test.ts (36 tests) 34ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 37ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 42ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 39ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 13ms
(node:51060) ExperimentalWarning: buffer.File is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
 ✓ src/services/portalApi.test.ts (6 tests) 20ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 13ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 4ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 10ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2623ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2126ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5521ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  549ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  433ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  318ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  326ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  328ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  318ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  317ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  382ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  347ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  535ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4200ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2615ms

 Test Files  35 passed (35)
      Tests  302 passed (302)
   Start at  09:26:35
   Duration  7.25s (transform 4.83s, setup 0ms, collect 9.69s, tests 23.36s, environment 4.60s, prepare 2.14s)

