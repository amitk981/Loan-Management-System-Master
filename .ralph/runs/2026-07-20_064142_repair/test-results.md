# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_060345_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 855ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  340ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1167ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  308ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  609ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1362ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  664ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  386ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1964ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  358ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  356ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 581ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  325ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 300ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2569ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  578ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  444ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 471ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  401ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 167ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2293ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1097ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  927ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 982ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  365ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  373ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1193ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  410ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 389ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 242ms
 ✓ src/services/authSession.test.ts (36 tests) 37ms
 ✓ src/services/portalApi.test.ts (7 tests) 22ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 174ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 63ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 170ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 327ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 76ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 8ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5550ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  452ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  436ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  317ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  300ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  369ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  349ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  360ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  313ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  578ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 12ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 9ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 65ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 44ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 40ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 62ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 8ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 56ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4461ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2197ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 12ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1073ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  968ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  06:50:02
   Duration  8.40s (transform 4.06s, setup 0ms, collect 12.30s, tests 26.85s, environment 5.95s, prepare 2.99s)


Duration milliseconds: 9202
Exit code: 0
