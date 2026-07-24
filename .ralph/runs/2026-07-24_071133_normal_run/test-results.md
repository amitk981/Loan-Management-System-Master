# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_071133_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 952ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  420ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1448ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  702ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  391ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1701ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  350ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1677ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  533ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  374ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  338ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 419ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1059ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  562ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2894ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  302ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  575ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  447ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  461ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 449ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 564ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  324ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 234ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 355ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 512ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 402ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 532ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  456ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 520ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 646ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  492ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5672ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  605ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  380ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  355ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  348ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  343ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  315ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  392ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  368ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  360ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  622ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1052ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  365ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2208ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1107ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  860ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4643ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2448ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 417ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 212ms
 ✓ src/services/authSession.test.ts (39 tests) 46ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 294ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1055ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  395ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  404ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 182ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 225ms
 ✓ src/services/servicingApi.test.ts (13 tests) 27ms
 ✓ src/services/portalApi.test.ts (10 tests) 24ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 11ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 640ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  640ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 72ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 70ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 18ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 178ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 23ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 37ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 58ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 9ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 35ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 55ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 16ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 37ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/playwright.seed.test.ts (3 tests) 3ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1072ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  962ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 5ms

 Test Files  54 passed (54)
      Tests  424 passed (424)
   Start at  07:42:14
   Duration  11.17s (transform 4.21s, setup 0ms, collect 16.16s, tests 32.81s, environment 8.52s, prepare 3.58s)


Duration milliseconds: 11923
Exit code: 0
