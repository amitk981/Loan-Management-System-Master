# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-25_104405_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1246ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  348ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  416ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (11 tests) 2120ms
   ✓ 011PA default case and frozen-note read surface > renders list/detail, grace, extension, and frozen note from backend projections  329ms
   ✓ 011PA default case and frozen-note read surface > shows exact pending, rejected, conflicted, and foreign approval blockers without decision controls  408ms
   ✓ 011PA default case and frozen-note read surface > enforces a reason, posts the server-fixed action, and refetches canonical terminal state  876ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2975ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  700ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  359ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3891ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  316ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  943ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  784ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  399ms
 ✓ src/pages/compliance/AuditArchiveHub.test.tsx (11 tests) 4301ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > filters and paginates the S74 explorer through backend query parameters  1282ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > records and revisits a separate immutable M14-FR-012 auditor observation  1156ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > surfaces backend observation validation without exposing details or lifecycle controls  396ms
   ✓ 012DAC audit explorer, observation, and retained archive wiring > surfaces a foreign or stale sample denial without leaking backend details  460ms
 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 1756ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  551ms
   ✓ Task Inbox screen > opens the linked application and completes a permitted comment action  346ms
   ✓ Task Inbox screen > surfaces the backend rejection when task authority changes before an action  398ms
 ✓ src/pages/closure/LoanClosureHub.test.tsx (6 tests) 2319ms
   ✓ 011PC closure readiness and downstream owner wiring > validates notes, closes from server readiness, and refetches canonical downstream reads  490ms
   ✓ 011PC closure readiness and downstream owner wiring > issues NOC then renders the canonical refetch projection  628ms
   ✓ 011PC closure readiness and downstream owner wiring > records server-owned security state and archives only after downstream prerequisites  942ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1789ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  708ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  502ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 751ms
   ✓ interest and monitoring workspaces > makes loan and invoice 101 reachable and accrues the disclosed complete selection  403ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1846ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  490ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  973ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 2308ms
   ✓ 010MA Repayments Hub wiring > renders canonical ledger, statement exceptions, and subsidiary reconciliation evidence  344ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  690ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  570ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  421ms
 ✓ src/pages/compliance/ComplianceDashboard.test.tsx (5 tests) 1693ms
   ✓ 011PD compliance dashboard owner wiring > validates projected reviews, refetches canonical state, and keeps auditors read-only  908ms
   ✓ 011PD compliance dashboard owner wiring > blocks accepted statutory reviews until required Board evidence is named  540ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 828ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  460ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 8420ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  765ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  638ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  438ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  336ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  416ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  314ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  421ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  386ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  543ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  553ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  1146ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 438ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 477ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 356ms
 ✓ src/pages/reports/ReportsMIS.test.tsx (5 tests) 1065ms
   ✓ ReportsMIS report wiring > preserves active filters while backend sorting and pagination change  484ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 598ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 341ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 7534ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  4129ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  515ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  417ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  349ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  326ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  391ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  436ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 531ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 675ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  593ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 714ms
   ✓ 010N Global Search Results > loads server groups, card fields, and permission-valid quick actions  311ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 951ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  619ms
 ✓ src/services/reportApi.test.ts (5 tests) 71ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1485ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  426ms
 ✓ src/pages/compliance/GrievancesHub.test.tsx (3 tests) 1052ms
   ✓ 011PE grievance register owner wiring > requires a projected status and reason, resolves, then refetches canonical state  717ms
 ✓ src/services/auditExplorerApi.test.ts (2 tests) 12ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 3036ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1316ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1338ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1534ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  605ms
   ✓ 009K CFC payment authorisation workspace > shows the truthful empty queue after an authorised item leaves CFC scope  305ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  579ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 605ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  374ms
 ✓ src/services/authSession.test.ts (40 tests) 52ms
 ✓ src/services/servicingApi.test.ts (13 tests) 31ms
 ✓ src/services/portalApi.test.ts (10 tests) 24ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 269ms
 ✓ src/services/recoveryApi.test.ts (8 tests) 9ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 391ms
   ✓ 010N Header search path > navigates the transient query to S02 without building a local result index  390ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 532ms
   ✓ MemberProfile container > preserves approval 400 VALIDATION_ERROR after one POST and no canonical refetch  314ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 427ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 11ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 96ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 10ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 110ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 207ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 11ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 112ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 53ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 49ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/playwright.seed.test.ts (5 tests) 3ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 91ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 28ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 16ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 17ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 303ms
   ✓ production demo surface isolation > removes tracer navigation and rejects direct tracer navigation even with permission  302ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 12ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 2069ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1837ms

 Test Files  64 passed (64)
      Tests  515 passed (515)
   Start at  11:45:41
   Duration  19.32s (transform 7.30s, setup 0ms, collect 26.94s, tests 62.69s, environment 18.69s, prepare 5.94s)


Duration milliseconds: 19959
Exit code: 0
