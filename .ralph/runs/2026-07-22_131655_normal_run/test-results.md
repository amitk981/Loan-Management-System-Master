# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_131655_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 855ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  307ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1477ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  654ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  378ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1696ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  501ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  368ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  401ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1970ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  399ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2723ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  548ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  478ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  402ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 453ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1030ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  592ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 660ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  454ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 453ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 325ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 498ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 344ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 633ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  555ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 238ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5871ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  512ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  410ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  345ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  369ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  326ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  315ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  431ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  315ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  394ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  345ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  702ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2337ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1141ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  958ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 996ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  340ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  431ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 414ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1213ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  399ms
 ✓ src/services/authSession.test.ts (38 tests) 36ms
 ✓ src/services/servicingApi.test.ts (13 tests) 31ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5032ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2758ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  313ms
 ✓ src/services/portalApi.test.ts (9 tests) 29ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 459ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 245ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 13ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 74ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 358ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 287ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 163ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 89ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 14ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 11ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 53ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 67ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 31ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 34ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 40ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 14ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1125ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1015ms

 Test Files  51 passed (51)
      Tests  411 passed (411)
   Start at  14:06:39
   Duration  10.55s (transform 4.60s, setup 0ms, collect 16.46s, tests 32.45s, environment 8.82s, prepare 3.75s)


Duration milliseconds: 11307
Exit code: 0
