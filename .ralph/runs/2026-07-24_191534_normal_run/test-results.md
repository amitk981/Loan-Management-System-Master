# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_191534_normal_run/sfpcl-lms

 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 1420ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  571ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1518ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  375ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  380ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  302ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1706ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  305ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2312ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  570ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  387ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2366ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1171ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  934ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 913ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  493ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1223ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  428ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1354ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  638ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  387ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 737ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1004ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  309ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  452ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 749ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  537ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 654ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  650ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 579ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 606ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  385ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 508ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5609ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  508ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  340ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  307ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  343ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  390ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  366ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  441ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  313ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  646ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4358ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2154ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 392ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 567ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  490ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 440ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 471ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  300ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 403ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 338ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 335ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 202ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 231ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 363ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 197ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 204ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 90ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 60ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 58ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 134ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 163ms
 ✓ src/services/authSession.test.ts (39 tests) 71ms
 ✓ src/services/portalApi.test.ts (10 tests) 36ms
 ✓ src/services/servicingApi.test.ts (13 tests) 38ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 36ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 44ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 48ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 13ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 14ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 10ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 4ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/playwright.seed.test.ts (3 tests) 4ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 2373ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2204ms

 Test Files  56 passed (56)
      Tests  457 passed (457)
   Start at  20:03:40
   Duration  10.65s (transform 4.99s, setup 0ms, collect 15.46s, tests 35.02s, environment 9.06s, prepare 3.56s)


Duration milliseconds: 11160
Exit code: 0
