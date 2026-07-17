# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_071512_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 900ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  333ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1267ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  327ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  712ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1377ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  607ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  410ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1983ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  382ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 553ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  314ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2654ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  605ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  462ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  317ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 551ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  448ms
 ✓ src/services/authSession.test.ts (36 tests) 52ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 167ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 307ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 68ms
 ✓ src/services/portalApi.test.ts (6 tests) 30ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1140ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  390ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 173ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 85ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 10ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 9ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2263ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1092ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  889ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 68ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 50ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 36ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 7ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 34ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 35ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 42ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5450ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  555ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  371ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  357ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  341ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  302ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  377ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  624ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4302ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2268ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1123ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1020ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  07:46:42
   Duration  7.41s (transform 3.77s, setup 0ms, collect 10.70s, tests 24.79s, environment 4.68s, prepare 2.30s)


Duration milliseconds: 8157
Exit code: 0
