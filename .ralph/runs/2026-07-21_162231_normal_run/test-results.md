# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_162231_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 829ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  315ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1336ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  656ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  338ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1567ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  512ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  360ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1893ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  333ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  351ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2570ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  550ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  412ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  326ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 966ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  578ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 448ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 585ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  347ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 362ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 345ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 478ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  396ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 140ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 949ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  346ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  363ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1145ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  402ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (3 tests) 229ms
 ✓ src/services/authSession.test.ts (36 tests) 37ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2162ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1067ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  861ms
 ✓ src/services/portalApi.test.ts (9 tests) 21ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 162ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5719ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  456ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  398ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  372ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  366ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  384ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  315ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  360ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  339ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  354ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  314ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  690ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 313ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 242ms
 ✓ src/services/servicingApi.test.ts (7 tests) 13ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4363ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2197ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 11ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 67ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 8ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 192ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 88ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 10ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 9ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 9ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 38ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 59ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 65ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 33ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 13ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 51ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/playwright.seed.test.ts (3 tests) 3ms
 ✓ src/utils/formatMoney.test.ts (1 test) 3ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1019ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  920ms

 Test Files  48 passed (48)
      Tests  385 passed (385)
   Start at  17:10:15
   Duration  9.17s (transform 4.36s, setup 0ms, collect 13.52s, tests 28.59s, environment 6.61s, prepare 3.19s)


Duration milliseconds: 9686
Exit code: 0
