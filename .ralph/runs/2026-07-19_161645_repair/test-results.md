# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-19_154507_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 2034ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  603ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  1064ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 2215ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  1131ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  473ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2940ms
   ✓ default AppraisalWorkbench authenticated HTTP container > runs eligibility with the exact request and performs one canonical four-read refresh  360ms
   ✓ default AppraisalWorkbench authenticated HTTP container > PATCHes only the appraisal allowlist and refreshes the canonical resources once  382ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  496ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  354ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 3405ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1874ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1152ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 4478ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  571ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  942ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  681ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  605ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1281ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  610ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  349ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1838ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  562ms
   ✓ mounted witness resource actions > corrects protected identity with an identity-only body  316ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (4 tests) 1183ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  521ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  630ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 951ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  639ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 647ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  565ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 586ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  392ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 571ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 558ms
   ✓ MemberProfile container > preserves approval 400 VALIDATION_ERROR after one POST and no canonical refetch  320ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 347ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 341ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 176ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 65ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 164ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 8155ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  913ms
   ✓ SanctionWorkbench authenticated container > clears prior rows and totals when a later collection fails with 'OBJECT_ACCESS_DENIED'  314ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  562ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  405ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  537ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  536ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  465ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  424ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  423ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  492ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  486ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  921ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 112ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 98ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 135ms
 ✓ src/services/authSession.test.ts (36 tests) 50ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 54ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 62ms
 ✓ src/services/portalApi.test.ts (7 tests) 40ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 45ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 10ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 13ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 16ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 14ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 6852ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3931ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  408ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  312ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  315ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  314ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  325ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3269ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2931ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  42 passed (42)
      Tests  351 passed (351)
   Start at  16:23:02
   Duration  11.84s (transform 6.53s, setup 0ms, collect 16.64s, tests 42.76s, environment 8.69s, prepare 3.10s)


Duration milliseconds: 12464
Exit code: 0
