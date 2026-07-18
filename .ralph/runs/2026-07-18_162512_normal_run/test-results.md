# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_162512_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 905ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  328ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1189ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  711ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1526ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  706ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  431ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1896ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  382ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 678ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  402ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2939ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  568ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  468ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 721ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  618ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 189ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (3 tests) 240ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 343ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1353ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  430ms
 ✓ src/services/portalApi.test.ts (7 tests) 21ms
 ✓ src/services/authSession.test.ts (36 tests) 33ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2637ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1417ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  974ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 12ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 14ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 122ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 142ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 189ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 78ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 42ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 49ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 28ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 33ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/tracerApi.test.ts (2 tests) 9ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 37ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6074ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  550ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  408ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  315ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  343ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  363ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  444ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  492ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  317ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  442ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  346ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  692ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 4ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 17ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 12ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4816ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2762ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  347ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  304ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1180ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1074ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 6ms

 Test Files  38 passed (38)
      Tests  331 passed (331)
   Start at  17:36:34
   Duration  8.89s (transform 4.87s, setup 0ms, collect 13.97s, tests 27.57s, environment 5.61s, prepare 2.85s)


Duration milliseconds: 9800
Exit code: 0
