# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_111454_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 928ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  347ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1327ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  764ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1536ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  723ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  437ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2005ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  397ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 670ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  423ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2778ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  622ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  496ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  346ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 543ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  465ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 282ms
 ✓ src/services/authSession.test.ts (36 tests) 78ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 430ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 70ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1572ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  612ms
 ✓ src/services/portalApi.test.ts (6 tests) 26ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 180ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2658ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1204ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1165ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 8ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 105ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 57ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 90ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 30ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 28ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 51ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 12ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 54ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 10ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 20ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6408ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  523ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  418ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  415ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  301ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  390ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  480ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  477ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  360ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  786ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4857ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2850ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  354ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  366ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1324ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1212ms

 Test Files  37 passed (37)
      Tests  327 passed (327)
   Start at  11:36:01
   Duration  8.92s (transform 5.08s, setup 0ms, collect 14.11s, tests 28.19s, environment 5.32s, prepare 2.50s)


Duration milliseconds: 9688
Exit code: 0
