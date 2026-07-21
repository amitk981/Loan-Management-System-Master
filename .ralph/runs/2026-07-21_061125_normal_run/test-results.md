# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_061125_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 963ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  301ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  315ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1362ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  350ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  784ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1466ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  592ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  486ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2213ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  455ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  308ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 600ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  350ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 345ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2935ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  656ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  563ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  363ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 556ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  477ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 464ms
   ✓ member portal backend-backed views > keeps the selected application identity when the list order changes  365ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2813ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1174ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1314ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1750ms
   ✓ mounted witness resource actions > retains Contact correction server facts after one 409 failure without refetch  340ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  536ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1638ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  631ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  636ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 1225ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  1041ms
 ✓ src/services/authSession.test.ts (36 tests) 52ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 240ms
 ✓ src/services/portalApi.test.ts (7 tests) 45ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 230ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 10ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 547ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 148ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 7588ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  523ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  538ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  414ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  359ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  309ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  364ms
   ✓ SanctionWorkbench authenticated container > renders unavailable frozen legacy approver names without a live identity lookup  311ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  542ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  436ms
   ✓ SanctionWorkbench authenticated container > surfaces CONFLICTED_APPROVER_NOT_ALLOWED without fabricating completion or refetching  887ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  602ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 365ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 200ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 10ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 11ms
 ✓ src/services/tracerApi.test.ts (2 tests) 6ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 13ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 118ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 46ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 122ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 157ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 17ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 6816ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3106ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  395ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  925ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  381ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  485ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  429ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 37ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 13ms
 ✓ src/playwright.seed.test.ts (3 tests) 7ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 19ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1614ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1470ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  06:46:08
   Duration  11.81s (transform 5.37s, setup 0ms, collect 18.23s, tests 36.79s, environment 7.94s, prepare 3.75s)


Duration milliseconds: 13123
Exit code: 0
