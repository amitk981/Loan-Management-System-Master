# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_185616_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1198ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  691ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1315ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  629ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  351ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1857ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  353ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2390ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1182ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  913ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2499ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  517ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  419ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 768ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1241ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  438ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 581ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  378ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 297ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 533ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  436ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 155ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 206ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 76ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 70ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 34ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 75ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 36ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 41ms
 ✓ src/services/authSession.test.ts (36 tests) 37ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 40ms
 ✓ src/services/portalApi.test.ts (6 tests) 21ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 30ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5339ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  517ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  351ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  312ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  309ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  304ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  361ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  337ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  337ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  564ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 9ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2762ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2383ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4333ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2352ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  19:14:19
   Duration  7.46s (transform 4.80s, setup 0ms, collect 10.80s, tests 26.01s, environment 5.13s, prepare 2.22s)


Duration milliseconds: 7991
Exit code: 0
