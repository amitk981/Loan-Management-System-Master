# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-25_074057_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 829ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (11 tests) 1449ms
   ✓ 011PA default case and frozen-note read surface > shows exact pending, rejected, conflicted, and foreign approval blockers without decision controls  316ms
   ✓ 011PA default case and frozen-note read surface > enforces a reason, posts the server-fixed action, and refetches canonical terminal state  577ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1968ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  427ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  365ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2840ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  581ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  493ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  440ms
 ✓ src/pages/compliance/AuditArchiveHub.test.tsx (11 tests) 3265ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > filters and paginates the S74 explorer through backend query parameters  946ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > records and revisits a separate immutable M14-FR-012 auditor observation  883ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > surfaces backend observation validation without exposing details or lifecycle controls  308ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > surfaces a foreign or stale sample denial without leaking backend details  425ms
 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 1378ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  455ms
   ✓ Task Inbox screen > opens the linked application and completes a permitted comment action  314ms
 ✓ src/pages/closure/LoanClosureHub.test.tsx (6 tests) 1946ms
   ✓ 011PC closure readiness and downstream owner wiring > validates notes, closes from server readiness, and refetches canonical downstream reads  503ms
   ✓ 011PC closure readiness and downstream owner wiring > issues NOC then renders the canonical refetch projection  520ms
   ✓ 011PC closure readiness and downstream owner wiring > records server-owned security state and archives only after downstream prerequisites  704ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1362ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  575ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  421ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1565ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  444ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  341ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  386ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1185ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  628ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 466ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 614ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  385ms
 ✓ src/pages/compliance/ComplianceDashboard.test.tsx (5 tests) 1129ms
   ✓ 011PD compliance dashboard owner wiring > validates projected reviews, refetches canonical state, and keeps auditors read-only  625ms
   ✓ 011PD compliance dashboard owner wiring > blocks accepted statutory reviews until required Board evidence is named  311ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5834ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  421ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  455ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  314ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  310ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  314ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  328ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  380ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  391ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  765ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4849ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2333ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  363ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  321ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 311ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 244ms
 ✓ src/pages/reports/ReportsMIS.test.tsx (5 tests) 808ms
   ✓ ReportsMIS report wiring > preserves active filters while backend sorting and pagination change  372ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 458ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 448ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 579ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 341ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 485ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  417ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 525ms
 ✓ src/services/reportApi.test.ts (5 tests) 7ms
 ✓ src/pages/compliance/GrievancesHub.test.tsx (3 tests) 726ms
   ✓ 011PE grievance register owner wiring > requires a projected status and reason, resolves, then refetches canonical state  526ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 781ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  559ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1249ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  443ms
 ✓ src/services/auditExplorerApi.test.ts (2 tests) 8ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 377ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 222ms
 ✓ src/services/authSession.test.ts (40 tests) 38ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1050ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  414ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  390ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 336ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2322ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1102ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  924ms
 ✓ src/services/servicingApi.test.ts (13 tests) 28ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 210ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 286ms
 ✓ src/services/recoveryApi.test.ts (8 tests) 17ms
 ✓ src/services/portalApi.test.ts (10 tests) 34ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 67ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 66ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 241ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 8ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 31ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 81ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 67ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 9ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 34ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/playwright.seed.test.ts (5 tests) 2ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 5ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 12ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 134ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 1217ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1050ms

 Test Files  64 passed (64)
      Tests  515 passed (515)
   Start at  08:18:31
   Duration  13.57s (transform 4.96s, setup 0ms, collect 18.70s, tests 44.61s, environment 12.12s, prepare 4.26s)


Duration milliseconds: 14092
Exit code: 0
