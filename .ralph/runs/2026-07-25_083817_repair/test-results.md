# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-25_074057_normal_run/sfpcl-lms

 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1987ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  328ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  322ms
 ✓ src/pages/closure/LoanClosureHub.test.tsx (6 tests) 2073ms
   ✓ 011PC closure readiness and downstream owner wiring > validates notes, closes from server readiness, and refetches canonical downstream reads  528ms
   ✓ 011PC closure readiness and downstream owner wiring > issues NOC then renders the canonical refetch projection  717ms
   ✓ 011PC closure readiness and downstream owner wiring > records server-owned security state and archives only after downstream prerequisites  572ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2357ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1173ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  938ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2623ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  481ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  422ms
 ✓ src/pages/compliance/AuditArchiveHub.test.tsx (11 tests) 3505ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > filters and paginates the S74 explorer through backend query parameters  964ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > records and revisits a separate immutable M14-FR-012 auditor observation  714ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > surfaces backend observation validation without exposing details or lifecycle controls  461ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > surfaces a foreign or stale sample denial without leaking backend details  432ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (11 tests) 1742ms
   ✓ 011PA default case and frozen-note read surface > shows exact pending, rejected, conflicted, and foreign approval blockers without decision controls  538ms
   ✓ 011PA default case and frozen-note read surface > enforces a reason, posts the server-fixed action, and refetches canonical terminal state  548ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 2014ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  647ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  417ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  359ms
 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 2004ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  819ms
   ✓ Task Inbox screen > opens the linked application and completes a permitted comment action  369ms
   ✓ Task Inbox screen > surfaces the backend rejection when task authority changes before an action  353ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1790ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  758ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  471ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1456ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  529ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6689ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  535ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  385ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  323ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  303ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  452ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  378ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  522ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  453ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  596ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  381ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  784ms
 ✓ src/pages/compliance/ComplianceDashboard.test.tsx (5 tests) 1213ms
   ✓ 011PD compliance dashboard owner wiring > validates projected reviews, refetches canonical state, and keeps auditors read-only  729ms
   ✓ 011PD compliance dashboard owner wiring > blocks accepted statutory reviews until required Board evidence is named  348ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1305ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  323ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  752ms
 ✓ src/pages/reports/ReportsMIS.test.tsx (5 tests) 1013ms
   ✓ ReportsMIS report wiring > preserves active filters while backend sorting and pagination change  398ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1216ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  471ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  468ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 856ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  318ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 6209ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3511ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  349ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  346ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  303ms
 ✓ src/pages/compliance/GrievancesHub.test.tsx (3 tests) 724ms
   ✓ 011PE grievance register owner wiring > requires a projected status and reason, resolves, then refetches canonical state  564ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 579ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 771ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  558ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 668ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  448ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 534ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  451ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 497ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 560ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 590ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 414ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 386ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 407ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 550ms
 ✓ src/services/reportApi.test.ts (5 tests) 7ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 331ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 258ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 295ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 212ms
 ✓ src/services/auditExplorerApi.test.ts (2 tests) 6ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 145ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 166ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 64ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 80ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 154ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 28ms
 ✓ src/services/portalApi.test.ts (10 tests) 34ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 73ms
 ✓ src/services/authSession.test.ts (40 tests) 44ms
 ✓ src/services/servicingApi.test.ts (13 tests) 26ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 45ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 57ms
 ✓ src/services/recoveryApi.test.ts (8 tests) 14ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 12ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 40ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 10ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 12ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/utils/formatMoney.test.ts (1 test) 3ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/playwright.seed.test.ts (5 tests) 3ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 2547ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2295ms

 Test Files  64 passed (64)
      Tests  515 passed (515)
   Start at  08:49:01
   Duration  15.18s (transform 6.26s, setup 0ms, collect 20.69s, tests 51.45s, environment 14.15s, prepare 4.35s)


Duration milliseconds: 15622
Exit code: 0
