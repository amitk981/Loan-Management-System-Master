# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-25_074057_normal_run/sfpcl-lms

 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1736ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  318ms
 ✓ src/pages/closure/LoanClosureHub.test.tsx (6 tests) 1804ms
   ✓ 011PC closure readiness and downstream owner wiring > validates notes, closes from server readiness, and refetches canonical downstream reads  466ms
   ✓ 011PC closure readiness and downstream owner wiring > issues NOC then renders the canonical refetch projection  550ms
   ✓ 011PC closure readiness and downstream owner wiring > records server-owned security state and archives only after downstream prerequisites  519ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2273ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1081ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  890ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2423ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  484ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  386ms
 ✓ src/pages/compliance/AuditArchiveHub.test.tsx (11 tests) 3016ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > filters and paginates the S74 explorer through backend query parameters  889ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > records and revisits a separate immutable M14-FR-012 auditor observation  735ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > surfaces a foreign or stale sample denial without leaking backend details  357ms
 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 1459ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  483ms
   ✓ Task Inbox screen > opens the linked application and completes a permitted comment action  321ms
   ✓ Task Inbox screen > surfaces the backend rejection when task authority changes before an action  321ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1552ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  422ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  353ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  333ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (11 tests) 1344ms
   ✓ 011PA default case and frozen-note read surface > renders list/detail, grace, extension, and frozen note from backend projections  329ms
   ✓ 011PA default case and frozen-note read surface > enforces a reason, posts the server-fixed action, and refetches canonical terminal state  462ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1303ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  407ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1368ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  586ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  384ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5393ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  407ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  359ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  331ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  353ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  402ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  381ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  662ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1001ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  371ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  408ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1015ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  569ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 848ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  308ms
 ✓ src/pages/compliance/ComplianceDashboard.test.tsx (5 tests) 1085ms
   ✓ 011PD compliance dashboard owner wiring > validates projected reviews, refetches canonical state, and keeps auditors read-only  672ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4940ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2657ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  311ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  306ms
 ✓ src/pages/reports/ReportsMIS.test.tsx (5 tests) 855ms
   ✓ ReportsMIS report wiring > preserves active filters while backend sorting and pagination change  355ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 794ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  584ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 635ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 530ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  454ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 573ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  349ms
 ✓ src/pages/compliance/GrievancesHub.test.tsx (3 tests) 793ms
   ✓ 011PE grievance register owner wiring > requires a projected status and reason, resolves, then refetches canonical state  593ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 608ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 511ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 455ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 460ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  327ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 375ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 337ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 371ms
 ✓ src/services/reportApi.test.ts (5 tests) 19ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 374ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 159ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 233ms
 ✓ src/services/auditExplorerApi.test.ts (2 tests) 6ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 217ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 135ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 59ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 71ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 172ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 81ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 209ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 31ms
 ✓ src/services/servicingApi.test.ts (13 tests) 27ms
 ✓ src/services/portalApi.test.ts (10 tests) 28ms
 ✓ src/services/authSession.test.ts (40 tests) 40ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 31ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 36ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/recoveryApi.test.ts (8 tests) 12ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 9ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 14ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/playwright.seed.test.ts (5 tests) 3ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 22ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 2437ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2251ms

 Test Files  64 passed (64)
      Tests  515 passed (515)
   Start at  10:30:24
   Duration  13.14s (transform 5.49s, setup 0ms, collect 18.25s, tests 44.34s, environment 11.80s, prepare 3.93s)


Duration milliseconds: 13681
Exit code: 0
