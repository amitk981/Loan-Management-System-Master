# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_151342_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1264ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  593ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  327ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1522ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  525ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  306ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1722ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  301ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2195ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1059ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  874ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2381ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  573ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  423ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 932ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  540ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 741ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 445ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  365ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1266ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  444ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 980ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  345ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  414ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 527ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 626ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  361ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 456ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 555ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 386ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 439ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 290ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5784ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  518ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  402ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  311ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  341ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  338ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  341ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  311ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  367ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  455ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  760ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 314ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4753ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2344ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  389ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 346ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 210ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 168ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 194ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 57ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 70ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 75ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 167ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 33ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 33ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 28ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 50ms
 ✓ src/services/portalApi.test.ts (9 tests) 30ms
 ✓ src/services/authSession.test.ts (38 tests) 37ms
 ✓ src/services/servicingApi.test.ts (13 tests) 22ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 18ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 10ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 15ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 10ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 9ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 12ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2324ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2147ms

 Test Files  51 passed (51)
      Tests  411 passed (411)
   Start at  17:08:49
   Duration  9.44s (transform 4.68s, setup 0ms, collect 13.99s, tests 31.54s, environment 7.79s, prepare 3.18s)


Duration milliseconds: 9973
Exit code: 0
