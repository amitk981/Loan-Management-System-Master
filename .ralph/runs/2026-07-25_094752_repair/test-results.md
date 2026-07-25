# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-25_074057_normal_run/sfpcl-lms

 ✓ src/pages/closure/LoanClosureHub.test.tsx (6 tests) 2083ms
   ✓ 011PC closure readiness and downstream owner wiring > validates notes, closes from server readiness, and refetches canonical downstream reads  458ms
   ✓ 011PC closure readiness and downstream owner wiring > issues NOC then renders the canonical refetch projection  599ms
   ✓ 011PC closure readiness and downstream owner wiring > records server-owned security state and archives only after downstream prerequisites  805ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2144ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  445ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  350ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2576ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1096ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1069ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3062ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  595ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  572ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  581ms
 ✓ src/pages/compliance/AuditArchiveHub.test.tsx (11 tests) 3555ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > filters and paginates the S74 explorer through backend query parameters  923ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > records and revisits a separate immutable M14-FR-012 auditor observation  950ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > surfaces backend observation validation without exposing details or lifecycle controls  462ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > surfaces a foreign or stale sample denial without leaking backend details  369ms
 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 1612ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  605ms
   ✓ Task Inbox screen > opens the linked application and completes a permitted comment action  302ms
   ✓ Task Inbox screen > surfaces the backend rejection when task authority changes before an action  331ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1579ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  498ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  350ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  328ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1216ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  587ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1220ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  388ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (11 tests) 1313ms
   ✓ 011PA default case and frozen-note read surface > enforces a reason, posts the server-fixed action, and refetches canonical terminal state  490ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6225ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  503ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  524ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  469ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  344ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  372ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  341ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  336ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  383ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  362ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  666ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1114ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  633ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1122ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  443ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  422ms
 ✓ src/pages/compliance/ComplianceDashboard.test.tsx (5 tests) 1104ms
   ✓ 011PD compliance dashboard owner wiring > validates projected reviews, refetches canonical state, and keeps auditors read-only  631ms
   ✓ 011PD compliance dashboard owner wiring > blocks accepted statutory reviews until required Board evidence is named  306ms
 ✓ src/pages/reports/ReportsMIS.test.tsx (5 tests) 837ms
   ✓ ReportsMIS report wiring > preserves active filters while backend sorting and pagination change  326ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5255ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2837ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  402ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  314ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 840ms
 ✓ src/pages/compliance/GrievancesHub.test.tsx (3 tests) 685ms
   ✓ 011PE grievance register owner wiring > requires a projected status and reason, resolves, then refetches canonical state  508ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 691ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 580ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 659ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  428ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 803ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  590ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 567ms
   ✓ interest and monitoring workspaces > makes loan and invoice 101 reachable and accrues the disclosed complete selection  305ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 603ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  525ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 485ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 434ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 349ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 471ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 349ms
 ✓ src/services/auditExplorerApi.test.ts (2 tests) 6ms
 ✓ src/services/reportApi.test.ts (5 tests) 13ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 250ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 379ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 223ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 182ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 123ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 89ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 80ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 162ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 162ms
 ✓ src/services/servicingApi.test.ts (13 tests) 27ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 113ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 37ms
 ✓ src/services/portalApi.test.ts (10 tests) 23ms
 ✓ src/services/authSession.test.ts (40 tests) 29ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 35ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 30ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 11ms
 ✓ src/services/recoveryApi.test.ts (8 tests) 11ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 12ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 10ms
 ✓ src/playwright.seed.test.ts (5 tests) 6ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 2704ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2526ms

 Test Files  64 passed (64)
      Tests  515 passed (515)
   Start at  09:58:26
   Duration  14.35s (transform 6.43s, setup 0ms, collect 20.22s, tests 48.32s, environment 13.08s, prepare 4.50s)


Duration milliseconds: 14906
Exit code: 0
