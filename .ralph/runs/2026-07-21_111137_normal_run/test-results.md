# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_111137_normal_run/sfpcl-lms

 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1642ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  563ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  354ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1591ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  713ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  388ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2116ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  307ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  411ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2409ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1215ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  921ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2856ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  595ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  472ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  408ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1197ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  701ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1725ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  479ms
   ✓ mounted witness resource actions > corrects protected identity with an identity-only body  448ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1566ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  387ms
   ✓ 009K CFC payment authorisation workspace > shows the truthful empty queue after an authorised item leaves CFC scope  452ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  701ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1256ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  357ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  535ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 860ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  654ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 364ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 745ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  536ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 429ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 451ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 332ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 6351ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  541ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  390ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  325ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  330ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  343ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  338ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  358ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  408ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  596ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  475ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  649ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 167ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 162ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 75ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 278ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 155ms
 ✓ src/services/authSession.test.ts (36 tests) 35ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 97ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 71ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 47ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5610ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3267ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  375ms
 ✓ src/services/portalApi.test.ts (8 tests) 34ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 41ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 40ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 37ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 13ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 13ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 12ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 15ms
 ✓ src/services/servicingApi.test.ts (4 tests) 9ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 8ms
 ✓ src/playwright.seed.test.ts (3 tests) 3ms
 ✓ src/services/tracerApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/utils/formatMoney.test.ts (1 test) 7ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2376ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2227ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  47 passed (47)
      Tests  378 passed (378)
   Start at  12:04:25
   Duration  10.24s (transform 4.97s, setup 0ms, collect 13.80s, tests 35.24s, environment 8.15s, prepare 3.52s)


Duration milliseconds: 10803
Exit code: 0
