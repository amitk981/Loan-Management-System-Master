# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_114316_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1371ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  328ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  770ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1537ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  823ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  373ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2060ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  358ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2532ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1340ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  928ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2703ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  360ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  659ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  373ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  330ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 755ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1237ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  435ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 598ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  371ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 357ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 526ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  447ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 183ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 174ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 67ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 65ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 41ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 80ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 43ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 28ms
 ✓ src/services/portalApi.test.ts (6 tests) 20ms
 ✓ src/services/authSession.test.ts (36 tests) 33ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 29ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 36ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 18ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 10ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5815ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  711ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  368ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  314ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  313ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  339ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  308ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  394ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  372ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  638ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 12ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2714ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2328ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4224ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2182ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  12:50:35
   Duration  7.64s (transform 5.07s, setup 0ms, collect 11.45s, tests 27.32s, environment 4.52s, prepare 2.31s)


Duration milliseconds: 8168
Exit code: 0
