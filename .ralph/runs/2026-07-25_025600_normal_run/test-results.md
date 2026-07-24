# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-25_025600_normal_run/sfpcl-lms

 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (11 tests) 1908ms
   ✓ 011PA default case and frozen-note read surface > renders list/detail, grace, extension, and frozen note from backend projections  331ms
   ✓ 011PA default case and frozen-note read surface > shows exact pending, rejected, conflicted, and foreign approval blockers without decision controls  468ms
   ✓ 011PA default case and frozen-note read surface > enforces a reason, posts the server-fixed action, and refetches canonical terminal state  574ms
 ✓ src/pages/tasks/TaskInbox.test.tsx (19 tests) 1993ms
   ✓ Task Inbox screen > renders the S03 API columns and replaces the page through backend pagination  749ms
   ✓ Task Inbox screen > round-trips assigned-to-me, due-today, and overdue filters through the API  336ms
   ✓ Task Inbox screen > opens the linked application and completes a permitted comment action  398ms
   ✓ Task Inbox screen > surfaces the backend rejection when task authority changes before an action  349ms
 ✓ src/pages/closure/LoanClosureHub.test.tsx (6 tests) 2529ms
   ✓ 011PC closure readiness and downstream owner wiring > validates notes, closes from server readiness, and refetches canonical downstream reads  685ms
   ✓ 011PC closure readiness and downstream owner wiring > issues NOC then renders the canonical refetch projection  820ms
   ✓ 011PC closure readiness and downstream owner wiring > records server-owned security state and archives only after downstream prerequisites  735ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2647ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  397ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  440ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3360ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  344ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  706ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  363ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  448ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1251ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  400ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  546ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1985ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  842ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  566ms
 ✓ src/pages/compliance/ComplianceDashboard.test.tsx (5 tests) 2237ms
   ✓ 011PD compliance dashboard owner wiring > validates projected reviews, refetches canonical state, and keeps auditors read-only  1035ms
   ✓ 011PD compliance dashboard owner wiring > blocks accepted statutory reviews until required Board evidence is named  977ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 2797ms
   ✓ 010MA Repayments Hub wiring > renders canonical ledger, statement exceptions, and subsidiary reconciliation evidence  313ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  801ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  936ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  464ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 2154ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > renders the approved three-card composition and server advisory only from the mounted projection  363ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  730ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  929ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 860ms
   ✓ interest and monitoring workspaces > makes loan and invoice 101 reachable and accrues the disclosed complete selection  606ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 747ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  430ms
 ✓ src/pages/Dashboard.test.tsx (24 tests) 436ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 8299ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  735ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  459ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  376ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  412ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  363ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  344ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  533ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  579ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  596ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  1037ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  857ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 666ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 338ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 673ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 485ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 459ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 7806ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  4544ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  333ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  468ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  379ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  344ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  384ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 716ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  549ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 707ms
   ✓ 010N Global Search Results > loads server groups, card fields, and permission-valid quick actions  312ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 903ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  598ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1590ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  526ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 256ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 396ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 458ms
 ✓ src/services/servicingApi.test.ts (13 tests) 23ms
 ✓ src/services/authSession.test.ts (39 tests) 63ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 3206ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1640ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1185ms
 ✓ src/services/portalApi.test.ts (10 tests) 30ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1312ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  419ms
   ✓ 009K CFC payment authorisation workspace > shows the truthful empty queue after an authorised item leaves CFC scope  334ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  529ms
 ✓ src/services/recoveryApi.test.ts (6 tests) 7ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 252ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 76ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 344ms
   ✓ 010N Header search path > navigates the transient query to S02 without building a local result index  343ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 18ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 9ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 309ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 196ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 29ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 172ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 21ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 37ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 94ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 58ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 4ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 34ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 13ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 18ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 3ms
 ✓ src/playwright.seed.test.ts (3 tests) 5ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 246ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 19ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 1595ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1421ms

 Test Files  59 passed (59)
      Tests  484 passed (484)
   Start at  03:24:21
   Duration  17.53s (transform 6.74s, setup 0ms, collect 24.95s, tests 56.87s, environment 16.30s, prepare 5.80s)


Duration milliseconds: 18086
Exit code: 0
