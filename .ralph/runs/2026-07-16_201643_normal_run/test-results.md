# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-16_201643_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 839ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1257ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  371ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  684ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1413ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  617ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  404ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1933ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  377ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  307ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 534ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  336ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2541ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  546ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  473ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  310ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 511ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  434ms
 ✓ src/services/authSession.test.ts (36 tests) 34ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 154ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 255ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 59ms
 ✓ src/services/portalApi.test.ts (6 tests) 18ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1132ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  392ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 150ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 83ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 8ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2205ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1063ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  886ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 16ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 99ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 39ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 41ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 54ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 32ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 27ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 13ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5506ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  552ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  408ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  310ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  343ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  313ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  302ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  357ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  359ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  343ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  573ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 4ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4209ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2176ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1180ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1079ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  20:35:11
   Duration  7.54s (transform 4.33s, setup 0ms, collect 11.83s, tests 24.40s, environment 4.50s, prepare 2.37s)


Duration milliseconds: 8345
Exit code: 0
