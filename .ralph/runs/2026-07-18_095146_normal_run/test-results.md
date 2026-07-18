# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_095146_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1309ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  474ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1344ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  573ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  418ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2058ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  356ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  440ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2575ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1170ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1119ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2804ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  488ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  490ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  471ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 984ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  577ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 899ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  338ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 660ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  436ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 285ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 513ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  435ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 153ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 184ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 40ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 83ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 72ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 53ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 59ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 45ms
 ✓ src/services/authSession.test.ts (36 tests) 34ms
 ✓ src/services/portalApi.test.ts (6 tests) 18ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 35ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 42ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5442ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  445ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  396ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  396ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  430ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  308ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  336ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  343ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  346ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  363ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  311ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  469ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 16ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 19ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2580ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2231ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4400ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2558ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  10:11:16
   Duration  7.82s (transform 4.95s, setup 0ms, collect 11.39s, tests 26.76s, environment 4.73s, prepare 2.46s)


Duration milliseconds: 8388
Exit code: 0
