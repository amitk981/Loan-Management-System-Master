# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_124034_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1775ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  671ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  578ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 2460ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  655ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  1396ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 2602ms
   ✓ SettingsHub Approval Matrix panel > renders active and retained historical rules from the versioned API without local fixtures  404ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  1046ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  551ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 3885ms
   ✓ default AppraisalWorkbench authenticated HTTP container > runs eligibility with the exact request and performs one canonical four-read refresh  586ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  763ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the returned Credit Manager decision once  359ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  468ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 1136ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  798ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 5816ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  483ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  1033ms
   ✓ 008M2 documentation workspace contract > posts the exact server-selected generation option and refetches once  359ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  1225ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  845ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 618ms
   ✓ MP14 disbursement status > renders only the server projection and downloads through the portal boundary  368ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 747ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  647ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 306ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 3744ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1963ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1354ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1481ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  493ms
   ✓ 009K CFC payment authorisation workspace > shows the truthful empty queue after an authorised item leaves CFC scope  318ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  596ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 642ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  355ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1876ms
   ✓ mounted witness resource actions > retains Contact correction server facts after one 400 failure without refetch  355ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  538ms
 ✓ src/services/authSession.test.ts (36 tests) 89ms
 ✓ src/services/portalApi.test.ts (7 tests) 24ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 426ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 678ms
   ✓ MemberProfile container > preserves approval 400 VALIDATION_ERROR after one POST and no canonical refetch  366ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 13ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 430ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 153ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 312ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 43ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 10334ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  1127ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  778ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  726ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  475ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  514ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  591ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  674ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  372ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  645ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  438ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  1385ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 12ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 178ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 10ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 159ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 55ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 62ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 85ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 9ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 16ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 13ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 109ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 12ms
 ✓ src/playwright.seed.test.ts (3 tests) 3ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 12ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 12ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 5ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 9863ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  6183ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  635ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  458ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  529ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  447ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1556ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  1438ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  13:26:11
   Duration  16.38s (transform 8.88s, setup 0ms, collect 28.23s, tests 51.77s, environment 12.46s, prepare 4.76s)


Duration milliseconds: 17307
Exit code: 0
