# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_020140_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 895ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  344ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1159ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  710ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1382ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  646ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  376ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1874ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  364ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 570ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  345ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 320ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2745ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  574ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  549ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  377ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 506ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  428ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 251ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2530ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1143ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1114ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1354ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  496ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1172ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  453ms
   ✓ 009K CFC payment authorisation workspace > shows the truthful empty queue after an authorised item leaves CFC scope  303ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  394ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 395ms
 ✓ src/services/authSession.test.ts (36 tests) 33ms
 ✓ src/services/portalApi.test.ts (7 tests) 19ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 229ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 179ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 75ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 358ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 204ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 79ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 14ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5810ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  471ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  394ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  367ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  400ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  336ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  317ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  355ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  343ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  486ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  361ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  653ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 6ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 44ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 75ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 29ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 40ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4697ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2516ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  307ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 13ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 10ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 53ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 18ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1051ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  949ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  02:41:03
   Duration  8.84s (transform 4.32s, setup 0ms, collect 13.05s, tests 28.24s, environment 6.16s, prepare 3.06s)


Duration milliseconds: 9640
Exit code: 0
