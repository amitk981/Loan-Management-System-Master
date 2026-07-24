# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-25_032730_normal_run/sfpcl-lms

 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1538ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  470ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  346ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  301ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1741ms
 ✓ src/pages/closure/LoanClosureHub.test.tsx (6 tests) 1857ms
   ✓ 011PC closure readiness and downstream owner wiring > validates notes, closes from server readiness, and refetches canonical downstream reads  498ms
   ✓ 011PC closure readiness and downstream owner wiring > issues NOC then renders the canonical refetch projection  531ms
   ✓ 011PC closure readiness and downstream owner wiring > records server-owned security state and archives only after downstream prerequisites  574ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2416ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1239ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  895ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2425ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  511ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  389ms
 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 1400ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  480ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1338ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  584ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  374ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1261ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  403ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1100ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  363ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  491ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (11 tests) 1347ms
   ✓ 011PA default case and frozen-note read surface > enforces a reason, posts the server-fixed action, and refetches canonical terminal state  520ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5602ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  471ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  368ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  311ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  307ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  341ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  424ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  347ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  781ms
 ✓ src/pages/compliance/ComplianceDashboard.test.tsx (5 tests) 1056ms
   ✓ 011PD compliance dashboard owner wiring > validates projected reviews, refetches canonical state, and keeps auditors read-only  619ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 921ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  535ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 879ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  322ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 707ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  542ms
 ✓ src/pages/compliance/GrievancesHub.test.tsx (3 tests) 772ms
   ✓ 011PE grievance register owner wiring > requires a projected status and reason, resolves, then refetches canonical state  585ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 338ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 595ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  375ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 558ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 518ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  443ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5098ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2493ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  324ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  416ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 451ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 622ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 518ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 371ms
 ✓ src/pages/compliance/AuditArchiveHub.test.tsx (3 tests) 446ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 376ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 446ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 442ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 301ms
   ✓ 010N Header search path > navigates the transient query to S02 without building a local result index  300ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 138ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 147ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 173ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 243ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 222ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 90ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 137ms
 ✓ src/services/authSession.test.ts (40 tests) 43ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 49ms
 ✓ src/services/servicingApi.test.ts (13 tests) 21ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 72ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 28ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/portalApi.test.ts (10 tests) 27ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 31ms
 ✓ src/services/recoveryApi.test.ts (8 tests) 19ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 11ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 9ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 2515ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2324ms

 Test Files  61 passed (61)
      Tests  493 passed (493)
   Start at  04:04:47
   Duration  12.70s (transform 5.49s, setup 0ms, collect 18.07s, tests 41.49s, environment 11.22s, prepare 3.98s)


Duration milliseconds: 13235
Exit code: 0
