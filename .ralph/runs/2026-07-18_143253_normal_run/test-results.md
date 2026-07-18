# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_143253_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1503ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  548ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1567ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  603ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  472ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1921ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  446ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2555ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1265ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  989ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2637ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  510ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  537ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  303ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 823ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 608ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  357ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1063ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  615ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 311ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 546ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  441ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 183ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (3 tests) 212ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 88ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 180ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 65ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 75ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 33ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 35ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 36ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 28ms
 ✓ src/services/authSession.test.ts (36 tests) 38ms
 ✓ src/services/portalApi.test.ts (7 tests) 21ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 10ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 31ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 11ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5705ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  494ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  467ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  371ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  370ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  325ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  359ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  337ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  579ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 23ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 9ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 14ms
 ✓ src/services/tracerApi.test.ts (2 tests) 10ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2568ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2129ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4293ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2250ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  38 passed (38)
      Tests  331 passed (331)
   Start at  15:21:19
   Duration  7.61s (transform 4.58s, setup 0ms, collect 11.20s, tests 27.24s, environment 4.29s, prepare 2.34s)


Duration milliseconds: 8125
Exit code: 0
