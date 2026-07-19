# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-19_135000_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1591ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  475ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1637ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  792ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  347ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 2563ms
   ✓ default AppraisalWorkbench authenticated HTTP container > runs eligibility with the exact request and performs one canonical four-read refresh  433ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  413ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  367ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2851ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1472ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1070ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 3192ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  748ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  408ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  415ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 956ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  301ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  324ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1179ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  308ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  651ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 750ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  512ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (4 tests) 1078ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  435ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  625ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 1182ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  563ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 828ms
   ✓ MP14 disbursement status > renders only the server projection and downloads through the portal boundary  393ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 861ms
   ✓ 009K disbursement finance workspace > renders named backend blockers and disables initiation while readiness fails  324ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  512ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 667ms
   ✓ MemberProfile container > preserves approval 400 VALIDATION_ERROR after one POST and no canonical refetch  425ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 658ms
   ✓ 009J Loan Account 360 initial API view > loads the scoped account list and routes the selected server identity  420ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 294ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 223ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 104ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 204ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 76ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 66ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 39ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 8135ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  978ms
   ✓ SanctionWorkbench authenticated container > clears prior rows and totals when a later collection fails with 'OBJECT_ACCESS_DENIED'  327ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  580ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  329ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  363ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  416ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  411ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  392ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  515ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  676ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  773ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  654ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 41ms
 ✓ src/services/authSession.test.ts (36 tests) 52ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 43ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 51ms
 ✓ src/services/portalApi.test.ts (7 tests) 36ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 9ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 6648ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  3701ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  642ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  444ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  316ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 9ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 9ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 8ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 9ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 14ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 12ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 3ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 3020ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  2892ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  42 passed (42)
      Tests  351 passed (351)
   Start at  15:28:19
   Duration  11.21s (transform 5.98s, setup 0ms, collect 17.37s, tests 39.13s, environment 9.52s, prepare 3.34s)


Duration milliseconds: 11977
Exit code: 0
