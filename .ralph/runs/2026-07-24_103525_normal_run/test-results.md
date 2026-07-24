# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_103525_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1119ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  414ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  453ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1660ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  767ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  423ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1908ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  530ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  333ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  385ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2063ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  397ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  300ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2990ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  670ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  474ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  380ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 559ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1186ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  652ms
 ✓ src/pages/Dashboard.test.tsx (23 tests) 342ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 670ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  448ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 290ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 475ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 342ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 493ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 349ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 491ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  426ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 637ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6600ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  684ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  463ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  352ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  359ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  428ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  324ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  387ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  531ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  420ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  416ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  675ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1366ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  481ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2741ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1349ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1091ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 764ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  542ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 285ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 425ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  319ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5634ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3039ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  364ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  315ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  394ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1125ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  373ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  466ms
 ✓ src/services/authSession.test.ts (39 tests) 49ms
 ✓ src/services/servicingApi.test.ts (13 tests) 29ms
 ✓ src/services/portalApi.test.ts (10 tests) 28ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 188ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 425ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 220ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 64ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 820ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  819ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 11ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 83ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 9ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 157ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 9ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 74ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 31ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 95ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 29ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 11ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 12ms
 ✓ src/utils/formatMoney.test.ts (1 test) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1308ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1198ms

 Test Files  54 passed (54)
      Tests  435 passed (435)
   Start at  11:29:37
   Duration  12.54s (transform 5.66s, setup 0ms, collect 19.32s, tests 38.23s, environment 10.57s, prepare 3.67s)


Duration milliseconds: 13083
Exit code: 0
