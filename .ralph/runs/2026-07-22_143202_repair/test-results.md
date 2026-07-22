# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_131655_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1267ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  629ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  333ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1567ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  481ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  325ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  340ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1859ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  342ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  329ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2778ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1248ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1190ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2857ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  553ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  483ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  428ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1444ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  482ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1365ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  303ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  719ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1261ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  511ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  496ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 690ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  430ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 869ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 553ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  461ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 529ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 521ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  302ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 490ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 477ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6176ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  560ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  439ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  349ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  355ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  405ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  353ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  419ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  343ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  471ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  437ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  686ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 569ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 504ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 359ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 292ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 213ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 200ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 178ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5553ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3008ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  333ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  308ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 78ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 81ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 175ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 75ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 43ms
 ✓ src/services/authSession.test.ts (38 tests) 46ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 35ms
 ✓ src/services/servicingApi.test.ts (13 tests) 32ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 37ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 34ms
 ✓ src/services/portalApi.test.ts (9 tests) 27ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 14ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 10ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 12ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 10ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2382ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2258ms

 Test Files  51 passed (51)
      Tests  411 passed (411)
   Start at  14:46:19
   Duration  10.69s (transform 5.34s, setup 0ms, collect 15.84s, tests 35.71s, environment 8.98s, prepare 3.23s)


Duration milliseconds: 11225
Exit code: 0
