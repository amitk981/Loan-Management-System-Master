# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_151220_normal_run/sfpcl-lms

 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1282ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  619ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  347ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1528ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  521ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  320ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1677ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  324ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2320ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  477ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  362ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2415ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1216ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  877ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1026ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  532ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 820ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  310ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1350ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  447ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 601ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1113ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  326ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  501ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 656ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  655ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 521ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  444ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 588ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  365ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 690ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  524ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5492ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  448ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  361ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  313ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  354ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  321ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  331ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  516ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  395ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  572ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 435ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 306ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 549ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4580ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2305ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  309ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 282ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 392ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 448ms
 ✓ src/pages/Dashboard.test.tsx (23 tests) 344ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 297ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 264ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 165ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 226ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 187ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 64ms
 ✓ src/services/productionSurfaceIsolation.test.ts (1 test) 134ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 265ms
 ✓ src/services/servicingApi.test.ts (13 tests) 31ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 82ms
 ✓ src/pages/applications/ApplicationList.test.tsx (3 tests) 31ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 36ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 62ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 32ms
 ✓ src/services/portalApi.test.ts (10 tests) 31ms
 ✓ src/services/authSession.test.ts (39 tests) 57ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 7ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 12ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 10ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 8ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (4 tests) 2260ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2086ms

 Test Files  55 passed (55)
      Tests  437 passed (437)
   Start at  16:29:16
   Duration  10.55s (transform 5.11s, setup 0ms, collect 15.77s, tests 33.74s, environment 9.19s, prepare 3.52s)


Duration milliseconds: 11096
Exit code: 0
