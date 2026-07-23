# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_164006_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1310ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  626ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1525ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  503ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  334ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  300ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1859ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  341ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2288ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1117ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  896ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2438ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  536ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  469ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1070ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  325ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  458ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1254ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  418ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 944ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  531ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 734ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 709ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  708ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 595ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 632ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  392ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 494ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 527ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  439ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 425ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5775ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  595ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  374ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  369ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  319ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  343ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  340ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  408ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  382ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  710ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 388ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 315ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 406ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 345ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4692ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2244ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  376ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  308ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 309ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 74ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 153ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 194ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 194ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 64ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 160ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 35ms
 ✓ src/services/authSession.test.ts (39 tests) 26ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 44ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 38ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 68ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 39ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 6ms
 ✓ src/services/portalApi.test.ts (10 tests) 22ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 9ms
 ✓ src/services/servicingApi.test.ts (13 tests) 31ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 17ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 10ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 16ms
 ✓ src/playwright.seed.test.ts (3 tests) 5ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 11ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 8ms
 ✓ src/utils/formatMoney.test.ts (1 test) 5ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2200ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2058ms

 Test Files  52 passed (52)
      Tests  415 passed (415)
   Start at  18:45:42
   Duration  9.60s (transform 4.63s, setup 0ms, collect 14.03s, tests 32.51s, environment 8.07s, prepare 3.21s)


Duration milliseconds: 10319
Exit code: 0
