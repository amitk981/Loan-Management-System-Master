# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_092208_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1456ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  433ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  717ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1460ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  699ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  403ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2112ms
   ✓ default AppraisalWorkbench authenticated HTTP container > PATCHes only the appraisal allowlist and refreshes the canonical resources once  332ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  359ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2698ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1466ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  931ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2688ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  384ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  528ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  401ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  307ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 774ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 521ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  418ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1237ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  429ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 501ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  304ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 339ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 154ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 81ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 145ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 67ms
 ✓ src/services/authSession.test.ts (36 tests) 29ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 62ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 33ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 40ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 44ms
 ✓ src/services/portalApi.test.ts (6 tests) 18ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 41ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 29ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 16ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 11ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 13ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5591ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  748ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  390ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  320ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  312ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  322ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  314ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  344ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  311ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  621ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 10ms
 ✓ src/services/tracerApi.test.ts (2 tests) 6ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2681ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2244ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4307ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2260ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  340ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  10:09:40
   Duration  8.00s (transform 5.62s, setup 0ms, collect 12.30s, tests 27.20s, environment 4.70s, prepare 2.32s)


Duration milliseconds: 8526
Exit code: 0
