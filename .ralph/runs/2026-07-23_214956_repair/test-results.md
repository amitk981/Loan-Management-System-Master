# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_210407_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1346ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  627ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  334ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1517ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  491ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  335ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  338ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1708ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  304ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2211ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1120ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  823ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2289ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  492ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  370ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1089ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  393ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  455ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1008ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  507ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1268ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  446ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 704ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  540ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 767ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 565ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 585ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  348ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 683ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  682ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 415ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 510ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  433ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5265ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  494ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  354ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  312ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  357ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  380ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  414ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  610ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 292ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 392ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 462ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 276ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 491ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  363ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 346ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4691ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2349ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 202ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 75ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 188ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 242ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 203ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 192ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 73ms
 ✓ src/services/authSession.test.ts (39 tests) 39ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 29ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 47ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 89ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 35ms
 ✓ src/services/portalApi.test.ts (10 tests) 27ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 28ms
 ✓ src/services/servicingApi.test.ts (13 tests) 20ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 10ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 23ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 11ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 9ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2235ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2112ms

 Test Files  54 passed (54)
      Tests  424 passed (424)
   Start at  22:00:12
   Duration  9.80s (transform 5.09s, setup 0ms, collect 14.83s, tests 32.72s, environment 8.40s, prepare 3.22s)


Duration milliseconds: 10441
Exit code: 0
