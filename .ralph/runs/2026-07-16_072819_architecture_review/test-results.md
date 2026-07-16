# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-16_072819_architecture_review/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1301ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  420ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1265ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  583ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  327ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1770ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  403ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (14 tests) 1813ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  478ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  401ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2439ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1168ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  960ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 774ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1049ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  593ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 608ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  440ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 587ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  490ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 344ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 94ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 208ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 196ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 109ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 40ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 87ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 91ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 46ms
 ✓ src/services/authSession.test.ts (36 tests) 38ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 36ms
(node:87808) ExperimentalWarning: buffer.File is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
 ✓ src/services/portalApi.test.ts (6 tests) 21ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 32ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 12ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 6ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5746ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  441ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  353ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  339ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  410ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  362ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  443ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  333ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  409ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  359ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  712ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2619ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2240ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4333ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2648ms

 Test Files  36 passed (36)
      Tests  319 passed (319)
   Start at  08:01:26
   Duration  7.70s (transform 5.32s, setup 0ms, collect 10.73s, tests 25.72s, environment 5.28s, prepare 2.58s)

