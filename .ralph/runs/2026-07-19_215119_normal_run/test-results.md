# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-19_215119_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1189ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  359ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  431ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1540ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  309ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  1044ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1938ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  897ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  463ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2716ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  472ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  405ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 796ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  529ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3530ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  704ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  503ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  536ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 463ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 683ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  573ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 248ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2848ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1336ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1147ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1394ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  412ms
   ✓ 009K CFC payment authorisation workspace > shows the truthful empty queue after an authorised item leaves CFC scope  386ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  576ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1514ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  499ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 546ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  318ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 262ms
 ✓ src/services/portalApi.test.ts (7 tests) 27ms
 ✓ src/services/authSession.test.ts (36 tests) 41ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 242ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 122ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 539ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 13ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 243ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 144ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 7470ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  847ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  554ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  506ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  428ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  396ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  382ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  428ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  375ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  423ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  413ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  924ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 13ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 18ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 100ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 58ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 84ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 61ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 29ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 92ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 15ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 10ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 6763ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3470ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  374ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  457ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  314ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  397ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  380ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  495ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 20ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 6ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1490ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1376ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  22:22:06
   Duration  11.77s (transform 5.84s, setup 0ms, collect 18.40s, tests 37.29s, environment 9.29s, prepare 3.67s)


Duration milliseconds: 12699
Exit code: 0
