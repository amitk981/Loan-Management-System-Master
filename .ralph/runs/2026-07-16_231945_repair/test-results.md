# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-16_224541_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1243ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  420ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1300ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  608ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  331ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1825ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  363ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2225ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1043ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  900ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2515ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  545ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  424ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  329ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 996ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  578ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 779ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  330ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 604ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  420ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 507ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  440ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 320ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 178ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 132ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 69ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 86ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 79ms
 ✓ src/services/authSession.test.ts (36 tests) 44ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 43ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 39ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 30ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 38ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 29ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/portalApi.test.ts (6 tests) 20ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5360ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  539ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  384ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  307ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  366ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  325ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  327ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  369ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  302ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  537ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2598ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2276ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4247ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2241ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  303ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  23:25:28
   Duration  7.17s (transform 4.72s, setup 0ms, collect 10.67s, tests 25.38s, environment 4.32s, prepare 2.26s)


Duration milliseconds: 7697
Exit code: 0
