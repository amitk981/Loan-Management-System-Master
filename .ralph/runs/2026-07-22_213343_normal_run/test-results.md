# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_213343_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 879ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1436ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  648ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  373ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1551ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  399ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  345ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  313ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2106ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  351ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  333ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 513ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2909ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  709ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  467ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  458ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1025ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  634ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 661ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  457ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 524ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 336ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 488ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 327ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 538ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  464ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 145ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 912ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  395ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5816ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  587ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  430ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  355ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  350ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  345ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  321ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  359ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  349ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  341ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  632ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2257ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1214ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  840ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1067ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  354ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 457ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4766ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2585ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  359ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 433ms
 ✓ src/services/authSession.test.ts (39 tests) 55ms
 ✓ src/services/servicingApi.test.ts (13 tests) 31ms
 ✓ src/services/portalApi.test.ts (9 tests) 25ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 193ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 332ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 226ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 125ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 255ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 754ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  753ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 112ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 10ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 97ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 52ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 8ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 33ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 39ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 13ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 41ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1116ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1008ms

 Test Files  52 passed (52)
      Tests  413 passed (413)
   Start at  22:23:51
   Duration  10.16s (transform 4.08s, setup 0ms, collect 14.58s, tests 32.73s, environment 8.20s, prepare 3.31s)


Duration milliseconds: 11048
Exit code: 0
