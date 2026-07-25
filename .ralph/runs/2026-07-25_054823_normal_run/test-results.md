# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-25_054823_normal_run/sfpcl-lms

 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1499ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  484ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  333ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  311ms
 ✓ src/pages/closure/LoanClosureHub.test.tsx (6 tests) 1983ms
   ✓ 011PC closure readiness and downstream owner wiring > validates notes, closes from server readiness, and refetches canonical downstream reads  580ms
   ✓ 011PC closure readiness and downstream owner wiring > issues NOC then renders the canonical refetch projection  641ms
   ✓ 011PC closure readiness and downstream owner wiring > records server-owned security state and archives only after downstream prerequisites  516ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2027ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2510ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1186ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  992ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2807ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  571ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  554ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  351ms
 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 1433ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  474ms
   ✓ Task Inbox screen > opens the linked application and completes a permitted comment action  311ms
   ✓ Task Inbox screen > surfaces the backend rejection when task authority changes before an action  320ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1289ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  467ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1367ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  551ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  397ms
 ✓ src/pages/compliance/ComplianceDashboard.test.tsx (5 tests) 1089ms
   ✓ 011PD compliance dashboard owner wiring > validates projected reviews, refetches canonical state, and keeps auditors read-only  646ms
   ✓ 011PD compliance dashboard owner wiring > blocks accepted statutory reviews until required Board evidence is named  300ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (11 tests) 1355ms
   ✓ 011PA default case and frozen-note read surface > shows exact pending, rejected, conflicted, and foreign approval blockers without decision controls  318ms
   ✓ 011PA default case and frozen-note read surface > enforces a reason, posts the server-fixed action, and refetches canonical terminal state  511ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1075ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  412ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  425ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5914ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  581ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  418ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  352ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  303ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  343ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  347ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  336ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  340ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  437ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  386ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  752ms
 ✓ src/pages/reports/ReportsMIS.test.tsx (5 tests) 905ms
   ✓ ReportsMIS report wiring > preserves active filters while backend sorting and pagination change  379ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1086ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  614ms
 ✓ src/pages/compliance/GrievancesHub.test.tsx (3 tests) 784ms
   ✓ 011PE grievance register owner wiring > requires a projected status and reason, resolves, then refetches canonical state  562ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5056ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2690ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  325ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  316ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 917ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  335ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  317ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 595ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  387ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 493ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  397ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 763ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  540ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 564ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 419ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 466ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 509ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 370ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 278ms
 ✓ src/pages/compliance/AuditArchiveHub.test.tsx (3 tests) 350ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 455ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 199ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 272ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 321ms
 ✓ src/services/reportApi.test.ts (5 tests) 13ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 77ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 198ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 166ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 227ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 151ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 284ms
 ✓ src/services/authSession.test.ts (40 tests) 58ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 93ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 32ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 38ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 35ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 68ms
 ✓ src/services/portalApi.test.ts (10 tests) 21ms
 ✓ src/services/servicingApi.test.ts (13 tests) 27ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 14ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/recoveryApi.test.ts (8 tests) 8ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 11ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 9ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 2367ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2193ms

 Test Files  63 passed (63)
      Tests  503 passed (503)
   Start at  06:14:07
   Duration  12.90s (transform 5.01s, setup 0ms, collect 18.05s, tests 43.11s, environment 11.88s, prepare 4.07s)


Duration milliseconds: 13406
Exit code: 0
