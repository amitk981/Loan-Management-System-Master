# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-16_220501_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1062ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  622ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1416ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  680ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  403ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1828ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  341ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2436ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1185ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  970ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2654ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  313ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  476ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  467ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  355ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 758ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 544ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  351ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1436ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  488ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 465ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  400ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 326ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 174ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 165ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 72ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 86ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 105ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 41ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 52ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 65ms
 ✓ src/services/authSession.test.ts (36 tests) 42ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 33ms
 ✓ src/services/portalApi.test.ts (6 tests) 18ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 10ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 10ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5280ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  435ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  435ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  320ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  345ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  355ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  333ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  601ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 11ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 12ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 13ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 13ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 13ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 9ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2603ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2156ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4308ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2169ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  22:33:47
   Duration  7.55s (transform 4.89s, setup 0ms, collect 11.09s, tests 26.10s, environment 4.84s, prepare 2.23s)


Duration milliseconds: 8083
Exit code: 0
