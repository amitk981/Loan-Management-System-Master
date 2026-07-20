# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_041841_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 973ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  357ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1110ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  303ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  637ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1440ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  609ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  356ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1983ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  383ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 592ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  376ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 304ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2721ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  583ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  479ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  464ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 562ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  491ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 138ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2337ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1113ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  943ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1154ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  395ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 969ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  321ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  417ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 228ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 362ms
 ✓ src/services/authSession.test.ts (36 tests) 36ms
 ✓ src/services/portalApi.test.ts (7 tests) 26ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 176ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 72ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 304ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 154ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 14ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5265ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  593ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  396ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  340ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  309ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  374ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  510ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 100ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 11ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4207ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2098ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 61ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 34ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 37ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 30ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 14ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 46ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 11ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 999ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  901ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  04:56:28
   Duration  8.19s (transform 3.79s, setup 0ms, collect 11.91s, tests 26.52s, environment 5.68s, prepare 2.69s)


Duration milliseconds: 8953
Exit code: 0
