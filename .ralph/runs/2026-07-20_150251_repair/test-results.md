# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_134450_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1363ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  508ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  454ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1910ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  402ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  1146ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 2014ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  980ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  494ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2836ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  498ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  421ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 785ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  542ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 500ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3992ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  320ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  822ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  661ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  541ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 688ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  565ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 222ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2855ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1380ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1153ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1581ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  552ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1367ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  487ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  571ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 607ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  421ms
 ✓ src/services/authSession.test.ts (36 tests) 59ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 318ms
 ✓ src/services/portalApi.test.ts (7 tests) 35ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 157ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 9ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 336ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 66ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 171ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 16ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 76ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 7498ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  796ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  538ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  521ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  438ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  445ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  433ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  442ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  413ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  477ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  426ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  661ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 98ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 10ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 56ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 35ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 49ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 49ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 14ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 10ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 6244ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3845ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  439ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1187ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1082ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  15:10:59
   Duration  11.27s (transform 5.59s, setup 0ms, collect 16.97s, tests 37.27s, environment 9.40s, prepare 3.07s)


Duration milliseconds: 12066
Exit code: 0
