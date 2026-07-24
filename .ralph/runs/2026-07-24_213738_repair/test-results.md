# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_211119_normal_run/sfpcl-lms

 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 1431ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  484ms
   ✓ Task Inbox screen > opens the linked application and completes a permitted comment action  318ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1527ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  450ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  325ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  317ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1798ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  357ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2309ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1126ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  902ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2426ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  453ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  376ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1290ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  455ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1080ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  366ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  462ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1432ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  605ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  402ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 915ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  506ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 747ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  549ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 576ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 626ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  376ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 512ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 788ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 544ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  464ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5628ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  472ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  408ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  328ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  307ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  302ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  350ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  319ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  397ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  364ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  618ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 434ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 389ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 263ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 392ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 325ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4798ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2426ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  318ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  303ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (7 tests) 540ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 226ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 221ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 284ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 225ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 306ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 136ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 140ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 66ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 62ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 65ms
 ✓ src/services/authSession.test.ts (39 tests) 37ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 142ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 32ms
 ✓ src/services/portalApi.test.ts (10 tests) 30ms
 ✓ src/services/servicingApi.test.ts (13 tests) 37ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 45ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 61ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 10ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 10ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/services/recoveryApi.test.ts (1 test) 3ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 2398ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2200ms

 Test Files  57 passed (57)
      Tests  464 passed (464)
   Start at  21:45:07
   Duration  10.93s (transform 5.48s, setup 0ms, collect 16.37s, tests 35.38s, environment 9.40s, prepare 3.60s)


Duration milliseconds: 11365
Exit code: 0
