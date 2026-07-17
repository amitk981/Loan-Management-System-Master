# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_083059_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1415ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  504ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  692ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1553ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  817ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  333ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1996ms
   ✓ default AppraisalWorkbench authenticated HTTP container > renders a stale 409 without retry, synthesis, or refresh  333ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  335ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2589ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1368ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  971ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2651ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  470ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  550ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  410ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  340ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 810ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 537ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  349ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1326ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  455ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 305ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 472ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  405ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 167ms
 ✓ src/services/authSession.test.ts (36 tests) 41ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 66ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 82ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 153ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 54ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 41ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 43ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 32ms
 ✓ src/services/portalApi.test.ts (6 tests) 18ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 29ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 38ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5404ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  733ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  387ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  322ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  315ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  304ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  334ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  516ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 11ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 12ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 11ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2653ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2189ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4123ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2148ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  08:43:19
   Duration  7.66s (transform 5.10s, setup 0ms, collect 12.02s, tests 26.68s, environment 4.38s, prepare 2.38s)


Duration milliseconds: 8190
Exit code: 0
