# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_162231_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1452ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  450ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1604ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  751ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  468ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2431ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  445ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  446ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2858ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1346ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1246ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3317ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  633ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  662ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  360ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1200ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  659ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1194ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  372ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  531ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1038ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  396ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 757ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  535ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1863ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  536ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  525ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  324ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 466ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 535ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  455ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 372ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 281ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (3 tests) 269ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6529ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  529ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  475ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  433ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  444ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  325ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  362ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  323ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  460ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  512ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  749ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 397ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 361ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 63ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 183ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 78ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 237ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 187ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5685ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3272ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  344ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  316ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 47ms
 ✓ src/services/authSession.test.ts (36 tests) 142ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 243ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 104ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 69ms
 ✓ src/services/portalApi.test.ts (9 tests) 31ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 15ms
 ✓ src/services/servicingApi.test.ts (7 tests) 9ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 43ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 21ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 13ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 13ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/playwright.seed.test.ts (3 tests) 5ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2559ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2452ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  48 passed (48)
      Tests  385 passed (385)
   Start at  17:20:49
   Duration  10.66s (transform 5.06s, setup 0ms, collect 14.97s, tests 36.73s, environment 8.65s, prepare 3.31s)


Duration milliseconds: 11190
Exit code: 0
