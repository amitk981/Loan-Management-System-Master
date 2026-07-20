# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-20_092159_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1773ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  637ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  858ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 2140ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  1099ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  508ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2931ms
   ✓ default AppraisalWorkbench authenticated HTTP container > renders a stale 409 without retry, synthesis, or refresh  412ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  603ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  420ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 3489ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1646ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1212ms
   ✓ MemberGovernanceForm > sends a newly entered mobile instead of suppressing a real contact update  301ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3966ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  362ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  731ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  581ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  355ms
   ✓ 008M2 documentation workspace contract > executes the record_signature action family through its returned endpoint  308ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 2008ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  667ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1735ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  677ms
   ✓ 009K CFC payment authorisation workspace > shows the truthful empty queue after an authorised item leaves CFC scope  353ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  652ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 987ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  701ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1484ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  497ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  549ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 771ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  682ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 614ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  401ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 394ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 194ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 216ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 338ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 8042ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  990ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  558ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  340ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  361ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  595ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  626ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  544ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  501ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  737ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  427ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  653ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 202ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 184ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 66ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 68ms
 ✓ src/services/authSession.test.ts (36 tests) 71ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 28ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 51ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 87ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 52ms
 ✓ src/services/portalApi.test.ts (7 tests) 26ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 60ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 12ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 13ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 10ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 7240ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  5101ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  315ms
 ✓ src/playwright.seed.test.ts (3 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 2590ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2358ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  43 passed (43)
      Tests  355 passed (355)
   Start at  10:19:05
   Duration  11.30s (transform 5.89s, setup 0ms, collect 15.83s, tests 41.90s, environment 9.65s, prepare 3.21s)


Duration milliseconds: 12102
Exit code: 0
