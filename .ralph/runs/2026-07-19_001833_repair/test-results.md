# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_232234_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1511ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  546ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1625ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  833ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  367ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2105ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  356ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2549ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1387ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  878ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2743ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  659ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  414ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 829ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1087ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  613ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 627ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  415ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 574ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  500ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 362ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 179ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (3 tests) 198ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 36ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 231ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 35ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 76ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 66ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 44ms
 ✓ src/services/authSession.test.ts (36 tests) 37ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 88ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 26ms
 ✓ src/services/portalApi.test.ts (7 tests) 23ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 49ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5870ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  639ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  434ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  339ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  304ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  329ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  331ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  352ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  399ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  353ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  372ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  669ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 17ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 14ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 18ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2883ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2386ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  312ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4448ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2572ms

 Test Files  38 passed (38)
      Tests  331 passed (331)
   Start at  00:25:43
   Duration  8.03s (transform 4.99s, setup 0ms, collect 12.10s, tests 28.40s, environment 5.14s, prepare 2.26s)


Duration milliseconds: 8550
Exit code: 0
