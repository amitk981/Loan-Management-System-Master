# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-19_003418_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1346ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  509ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1412ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  638ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  379ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2031ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  480ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2468ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1169ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1044ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2514ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  530ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  459ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 949ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  539ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 863ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  351ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 693ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  450ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 398ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 575ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  491ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 179ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (4 tests) 277ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 165ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 153ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 86ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 74ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 59ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 29ms
 ✓ src/services/authSession.test.ts (36 tests) 39ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 46ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 41ms
 ✓ src/services/portalApi.test.ts (7 tests) 22ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 49ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5742ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  508ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  426ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  321ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  344ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  397ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  430ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  319ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  658ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 11ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2673ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2468ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4516ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2622ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  330ms

 Test Files  38 passed (38)
      Tests  334 passed (334)
   Start at  01:38:12
   Duration  8.23s (transform 5.49s, setup 0ms, collect 12.41s, tests 27.48s, environment 5.03s, prepare 2.57s)


Duration milliseconds: 8653
Exit code: 0
