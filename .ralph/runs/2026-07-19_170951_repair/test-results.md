# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-19_154507_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 2420ms
   ✓ mounted witness resource actions > retains Contact correction server facts after one 400 failure without refetch  529ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  707ms
   ✓ mounted witness resource actions > corrects protected identity with an identity-only body  307ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 2445ms
   ✓ SettingsHub Approval Matrix panel > renders active and retained historical rules from the versioned API without local fixtures  467ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  1053ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  613ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 3845ms
   ✓ default AppraisalWorkbench authenticated HTTP container > runs eligibility with the exact request and performs one canonical four-read refresh  662ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  580ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  662ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 4254ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1981ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  1564ms
   ✓ MemberGovernanceForm > sends the current version once and renders authoritative backend field errors inline  302ms
   ✓ MemberGovernanceForm > sends a newly entered mobile instead of suppressing a real contact update  313ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 5483ms
   ✓ 008M2 documentation workspace contract > keeps S26 facts in the approved queue/card vocabulary without the invented facts grid  567ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  485ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  981ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  727ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  809ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 2042ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  522ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  413ms
   ✓ RegistersHub owned approval register panels > loads S25 independently with immutable comments and evidence but no inferred download  334ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 2864ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > renders the approved three-card composition and server advisory only from the mounted projection  406ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  491ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  1854ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 1521ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  1114ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 2333ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  1317ms
   ✓ 009K CFC payment authorisation workspace > shows the truthful empty queue after an authorised item leaves CFC scope  407ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  582ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 766ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  670ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 664ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 631ms
   ✓ MP14 disbursement status > renders only the server projection and downloads through the portal boundary  349ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 659ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  354ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 363ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 225ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 294ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 145ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 385ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 118ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 118ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 11077ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  1106ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  607ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  413ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  771ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  580ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  518ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  676ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  1093ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  626ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  712ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  1249ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 52ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 99ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 47ms
 ✓ src/services/authSession.test.ts (36 tests) 48ms
 ✓ src/services/portalApi.test.ts (7 tests) 36ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 48ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 20ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 16ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 5ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 61ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 15ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 12ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 12ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 14ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 7ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/services/tracerApi.test.ts (2 tests) 4ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 4040ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  3654ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 10214ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  6887ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  391ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  359ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  304ms
   ✓ MemberGovernanceForm production container > submits the complete producer_institution body through the shared HTTP transport  467ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  389ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  302ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  334ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms

 Test Files  42 passed (42)
      Tests  352 passed (352)
   Start at  17:17:24
   Duration  15.48s (transform 7.98s, setup 0ms, collect 22.91s, tests 57.41s, environment 12.41s, prepare 3.95s)


Duration milliseconds: 16678
Exit code: 0
