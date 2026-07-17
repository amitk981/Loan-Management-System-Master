# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_085441_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1269ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  432ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1383ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  699ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  374ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1922ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  366ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  302ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2486ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1214ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  979ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2629ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  608ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  418ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1023ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  574ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 790ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 644ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  410ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 495ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  422ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 347ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 161ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 148ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 80ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 75ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 68ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 43ms
 ✓ src/services/authSession.test.ts (36 tests) 36ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 36ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 27ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 41ms
 ✓ src/services/portalApi.test.ts (6 tests) 20ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 10ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 12ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5425ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  433ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  326ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  329ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  317ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  325ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  396ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  336ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  447ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  396ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  529ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 12ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 11ms
 ✓ src/services/tracerApi.test.ts (2 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2552ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2131ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4310ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2485ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  09:10:38
   Duration  7.69s (transform 5.00s, setup 0ms, collect 12.05s, tests 26.13s, environment 4.66s, prepare 2.26s)


Duration milliseconds: 8215
Exit code: 0
