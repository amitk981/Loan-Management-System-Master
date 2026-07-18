# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_232234_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 889ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  312ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1109ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  645ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1387ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  644ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  386ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1856ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  364ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  302ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 631ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  406ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 597ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  444ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3036ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  620ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  474ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  412ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (3 tests) 369ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 394ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 517ms
   ✓ MemberProfile container > preserves approval 400 VALIDATION_ERROR after one POST and no canonical refetch  303ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1610ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  567ms
 ✓ src/services/portalApi.test.ts (7 tests) 22ms
 ✓ src/services/authSession.test.ts (36 tests) 56ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2935ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1305ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1174ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 11ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 71ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 94ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 177ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 13ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 90ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 54ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 98ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 124ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (4 tests) 78ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 8ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 64ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 15ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 11ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6909ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  446ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  399ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  309ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  305ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  360ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  471ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  382ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  653ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  584ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  1124ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5728ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3457ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  343ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  414ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  327ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1209ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1094ms

 Test Files  38 passed (38)
      Tests  331 passed (331)
   Start at  00:10:32
   Duration  9.05s (transform 4.76s, setup 0ms, collect 13.83s, tests 30.21s, environment 5.46s, prepare 3.12s)


Duration milliseconds: 9958
Exit code: 0
