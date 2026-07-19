# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-19_154507_normal_run/sfpcl-lms

 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 2958ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  663ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  1949ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 3153ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  1166ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  1114ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 4712ms
   ✓ default AppraisalWorkbench authenticated HTTP container > renders a stale 409 without retry, synthesis, or refresh  326ms
   ✓ default AppraisalWorkbench authenticated HTTP container > clicks 'reviewed decision' through the authenticated boundary and refreshes four reads  522ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  1217ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  969ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 5165ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1748ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  2791ms
   ✓ MemberGovernanceForm > sends a newly entered mobile instead of suppressing a real contact update  367ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 6537ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  380ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  905ms
   ✓ 008M2 documentation workspace contract > posts the exact server-selected generation option and refetches once  616ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  1848ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  786ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1206ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  524ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  399ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1899ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  622ms
   ✓ mounted witness resource actions > corrects protected identity with an identity-only body  300ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 929ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  594ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 803ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  632ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 560ms
   ✓ MemberProfile container > preserves approval 400 VALIDATION_ERROR after one POST and no canonical refetch  313ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 324ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 511ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 1520ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  549ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  672ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 805ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  498ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 90ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 237ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 308ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 11278ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  1002ms
   ✓ SanctionWorkbench authenticated container > keeps the newest empty state when an older detail response arrives last  315ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  1214ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  1146ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  723ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  703ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  479ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  480ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  427ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  566ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  554ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  990ms
   ✓ SanctionWorkbench authenticated container > surfaces action error state 'VALIDATION_ERROR' without retry  417ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 950ms
   ✓ 009J Loan Account 360 initial API view > loads the scoped account list and routes the selected server identity  305ms
   ✓ 009J Loan Account 360 initial API view > renders the header, KPI row, and Summary from exact active server values  483ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 253ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 251ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 170ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 30ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 42ms
 ✓ src/services/authSession.test.ts (36 tests) 61ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 9213ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  5110ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  453ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  403ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  372ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  346ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  862ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  637ms
   ✓ MemberGovernanceForm production container > request preserves the backend 409 STALE_WRITE facts after one mutation and no GET  362ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 79ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 59ms
 ✓ src/services/portalApi.test.ts (7 tests) 29ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 12ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 11ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 6ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 13ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 25ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 7ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 5ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 4164ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  3818ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  42 passed (42)
      Tests  352 passed (352)
   Start at  17:53:01
   Duration  15.76s (transform 8.35s, setup 0ms, collect 21.10s, tests 58.41s, environment 12.16s, prepare 4.46s)


Duration milliseconds: 16408
Exit code: 0
