# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-16_233638_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1208ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  451ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1194ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  564ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  309ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1659ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2090ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  445ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  370ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2326ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1151ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  894ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 762ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1032ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  603ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 683ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  441ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 473ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  383ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 319ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 146ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 89ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 61ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 200ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 59ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 49ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 31ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 48ms
 ✓ src/services/authSession.test.ts (36 tests) 38ms
 ✓ src/services/portalApi.test.ts (6 tests) 18ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 35ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 37ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 11ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 13ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5061ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  458ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  327ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  375ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  367ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  324ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  597ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 21ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 15ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 9ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2516ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2133ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 3984ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2169ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  00:04:59
   Duration  7.03s (transform 4.88s, setup 0ms, collect 10.66s, tests 24.23s, environment 3.95s, prepare 2.21s)


Duration milliseconds: 7549
Exit code: 0
