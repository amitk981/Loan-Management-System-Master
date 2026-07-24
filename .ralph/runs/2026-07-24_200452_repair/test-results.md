# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_191534_normal_run/sfpcl-lms

 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1532ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  495ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  343ms
 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 1505ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  573ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1731ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  332ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2301ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  482ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  364ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2396ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1208ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  898ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1101ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  458ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  411ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1295ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  587ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  360ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1349ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  401ms
   ✓ mounted witness resource actions > corrects protected identity with an identity-only body  323ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 767ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  582ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 921ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  497ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 582ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  374ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 691ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  691ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 761ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 519ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 472ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  412ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5506ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  479ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  356ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  360ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  319ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  432ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  424ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  658ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 290ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 434ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 372ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 382ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 397ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4637ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2356ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  311ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 535ms
   ✓ MemberProfile container > preserves approval 400 VALIDATION_ERROR after one POST and no canonical refetch  372ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 215ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 203ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 296ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 184ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 272ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 237ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 140ms
 ✓ src/services/authSession.test.ts (39 tests) 35ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 64ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 84ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 62ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 180ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 35ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 34ms
 ✓ src/services/portalApi.test.ts (10 tests) 25ms
 ✓ src/services/servicingApi.test.ts (13 tests) 26ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 13ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 10ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 32ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 14ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 14ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 14ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 10ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 11ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 6ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 3ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 2607ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2382ms

 Test Files  56 passed (56)
      Tests  457 passed (457)
   Start at  20:16:36
   Duration  10.72s (transform 5.13s, setup 0ms, collect 15.40s, tests 35.33s, environment 9.91s, prepare 3.27s)


Duration milliseconds: 11246
Exit code: 0
