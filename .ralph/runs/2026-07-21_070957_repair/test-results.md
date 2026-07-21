# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_061125_normal_run/sfpcl-lms

 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1090ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  408ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  438ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1301ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  441ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1890ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  361ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  317ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2429ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1149ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  962ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2681ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  495ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  510ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1101ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  661ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 507ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  343ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1508ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  656ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  394ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 733ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  444ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 859ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  330ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 450ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 242ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 601ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  513ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 227ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 341ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 186ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 223ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 61ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5989ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  523ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  438ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  312ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  332ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  384ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  345ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  394ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  358ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  462ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  410ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  631ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 33ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 70ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 67ms
 ✓ src/services/authSession.test.ts (36 tests) 29ms
 ✓ src/services/portalApi.test.ts (7 tests) 27ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 56ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 32ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 38ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 14ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 14ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 18ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 5146ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2738ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  325ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  303ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  442ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 10ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2991ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2693ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 3ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  07:22:51
   Duration  9.66s (transform 5.70s, setup 0ms, collect 14.80s, tests 31.02s, environment 6.98s, prepare 3.38s)


Duration milliseconds: 10246
Exit code: 0
