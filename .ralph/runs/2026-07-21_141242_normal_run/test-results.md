# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_141242_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 991ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  413ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1519ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  679ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  423ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1775ms
   ✓ 010MA Repayments Hub wiring > renders canonical ledger, statement exceptions, and subsidiary reconciliation evidence  306ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  508ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  361ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  350ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2120ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  325ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  312ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2955ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  329ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  485ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  477ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  380ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 585ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  371ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1026ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  608ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 456ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 324ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 316ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 485ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  423ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 153ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1063ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  385ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  397ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1334ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  565ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 325ms
 ✓ src/services/authSession.test.ts (36 tests) 37ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5723ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  678ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  434ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  368ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  337ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  325ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  331ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  371ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  318ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  328ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  396ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  584ms
 ✓ src/services/portalApi.test.ts (9 tests) 22ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2266ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1204ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  825ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 226ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 373ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 124ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4531ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2446ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 75ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 211ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 9ms
 ✓ src/services/servicingApi.test.ts (4 tests) 10ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 49ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 77ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 9ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 8ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 28ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 38ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 18ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 64ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 12ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 19ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/utils/formatMoney.test.ts (1 test) 1ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1123ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1020ms

 Test Files  47 passed (47)
      Tests  379 passed (379)
   Start at  15:01:10
   Duration  9.67s (transform 4.98s, setup 0ms, collect 15.23s, tests 30.52s, environment 6.96s, prepare 3.18s)


Duration milliseconds: 10398
Exit code: 0
