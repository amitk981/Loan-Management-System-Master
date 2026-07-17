# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_124432_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 862ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  322ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1137ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  717ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1764ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  634ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  595ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2503ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  572ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  428ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 652ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  401ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 522ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  451ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3479ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  587ms
   ✓ 008M2 documentation workspace contract > posts the exact server-selected generation option and refetches once  311ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  885ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  413ms
 ✓ src/services/authSession.test.ts (36 tests) 34ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 294ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 164ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 73ms
 ✓ src/services/portalApi.test.ts (6 tests) 21ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1251ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  461ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 182ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 10ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2342ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1185ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  905ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 84ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 11ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 17ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 64ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 37ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 32ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 43ms
 ✓ src/services/tracerApi.test.ts (2 tests) 7ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 39ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 10ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 35ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6091ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  549ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  764ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  505ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  318ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  339ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  347ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  366ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  343ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  679ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 10ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4286ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2181ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1231ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1102ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  13:10:25
   Duration  8.67s (transform 4.47s, setup 0ms, collect 13.97s, tests 27.33s, environment 5.84s, prepare 2.64s)


Duration milliseconds: 9728
Exit code: 0
