# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-19_024941_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1292ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  435ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1424ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  624ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  446ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2050ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  352ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  363ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2486ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1105ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1073ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2785ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  617ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  491ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  357ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1034ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  551ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 891ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  306ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  331ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 624ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  397ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 565ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  480ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 371ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 203ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (4 tests) 268ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 153ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 150ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 54ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 72ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 195ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 67ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 33ms
 ✓ src/services/authSession.test.ts (36 tests) 41ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 67ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5651ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  440ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  447ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  359ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  301ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  347ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  341ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  368ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  303ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  365ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  360ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  628ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 33ms
 ✓ src/services/portalApi.test.ts (7 tests) 21ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 27ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 13ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 12ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 12ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4544ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2455ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2367ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2100ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  39 passed (39)
      Tests  338 passed (338)
   Start at  03:31:54
   Duration  7.98s (transform 4.46s, setup 0ms, collect 11.47s, tests 27.56s, environment 5.38s, prepare 2.42s)


Duration milliseconds: 8500
Exit code: 0
