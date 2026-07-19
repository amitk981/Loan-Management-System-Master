# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-19_110722_normal_run/sfpcl-lms

 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 2913ms
   ✓ mounted witness resource actions > retains Contact correction server facts after one 400 failure without refetch  613ms
   ✓ mounted witness resource actions > retains Contact correction server facts after one 409 failure without refetch  325ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  1015ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 3495ms
   ✓ SettingsHub Approval Matrix panel > renders active and retained historical rules from the versioned API without local fixtures  482ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  1492ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  717ms
   ✓ SettingsHub remaining panels > keeps server errors visible inside the successor modal and does not label a draft current  405ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 5230ms
   ✓ default AppraisalWorkbench authenticated HTTP container > runs eligibility with the exact request and performs one canonical four-read refresh  562ms
   ✓ default AppraisalWorkbench authenticated HTTP container > PATCHes only the appraisal allowlist and refreshes the canonical resources once  512ms
   ✓ default AppraisalWorkbench authenticated HTTP container > renders HTTP 403 once without retry or refresh  402ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  1093ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the returned Credit Manager decision once  464ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  681ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 5265ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  2523ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  2263ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 7469ms
   ✓ 008M2 documentation workspace contract > keeps S26 facts in the approved queue/card vocabulary without the invented facts grid  510ms
   ✓ 008M2 documentation workspace contract > renders the S26 facts, blockers, workflows, timeline, and terminal status beside Download  768ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  1370ms
   ✓ 008M2 documentation workspace contract > posts the exact server-selected generation option and refetches once  484ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  1287ms
   ✓ 008M2 documentation workspace contract > keeps Download and Verify independent inside the Document Pack  304ms
   ✓ 008M2 documentation workspace contract > submits a signed-copy upload through the opaque action and refetches once  843ms
   ✓ 008M2 documentation workspace contract > executes the record_stamp action family through its returned endpoint  306ms
 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 1946ms
   ✓ RegistersHub owned approval register panels > renders only the server-scoped frozen sanction page and replaces pagination after a filter change  866ms
   ✓ RegistersHub owned approval register panels > applies only canonical financial-year values  644ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 2708ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > renders the approved three-card composition and server advisory only from the mounted projection  498ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > creates, submits exactly once, and canonically refetches the returned amount  786ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  1324ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 873ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  655ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (4 tests) 1303ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  590ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  608ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 1132ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  916ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 818ms
   ✓ MemberProfile container > preserves approval 400 VALIDATION_ERROR after one POST and no canonical refetch  301ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (4 tests) 756ms
   ✓ 009J Loan Account 360 initial API view > loads the scoped account list and routes the selected server identity  507ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 1503ms
   ✓ 009K disbursement finance workspace > renders named backend blockers and disables initiation while readiness fails  598ms
   ✓ 009K disbursement finance workspace > submits Money fields with one stable key and treats replay as success  882ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 896ms
   ✓ MP14 disbursement status > renders only the server projection and downloads through the portal boundary  741ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 211ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 210ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 461ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 12775ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  1466ms
   ✓ SanctionWorkbench authenticated container > clears prior rows and totals when a later collection fails with 'MALFORMED_RESPONSE'  426ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  1115ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty filter authoritative while action submission finishes  808ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  662ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  660ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  685ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  818ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  577ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  581ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  584ms
   ✓ SanctionWorkbench authenticated container > surfaces CONFLICTED_APPROVER_NOT_ALLOWED without fabricating completion or refetching  371ms
   ✓ SanctionWorkbench authenticated container > surfaces GENERAL_MEETING_EVIDENCE_REQUIRED without fabricating completion or refetching  423ms
   ✓ SanctionWorkbench authenticated container > surfaces GENERAL_MEETING_APPROVAL_REJECTED without fabricating completion or refetching  460ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  1197ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (6 tests) 380ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 85ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 169ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 105ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 70ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 86ms
 ✓ src/services/authSession.test.ts (36 tests) 82ms
 ✓ src/services/portalApi.test.ts (7 tests) 20ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 14ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 15ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 9ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 12ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 47ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 8ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 8ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 13ms
 ✓ src/services/tracerApi.test.ts (2 tests) 3ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 9ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 17ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 8ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 4683ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  4133ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is explicit false  364ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 11355ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  7760ms
   ✓ MemberGovernanceForm production container > performs one ordinary human-like update before canonical Profile readback with the exact update ledger  693ms
   ✓ MemberGovernanceForm production container > submits the complete individual_farmer body through the shared HTTP transport  474ms
   ✓ MemberGovernanceForm production container > submits the complete fpc body through the shared HTTP transport  447ms
   ✓ MemberGovernanceForm production container > posts only the protected identity delta through the shared HTTP transport  358ms
   ✓ MemberGovernanceForm production container > request preserves the backend 400 VALIDATION_ERROR facts after one mutation and no GET  415ms
   ✓ MemberGovernanceForm production container > request preserves the backend 403 PERMISSION_DENIED facts after one mutation and no GET  321ms

 Test Files  42 passed (42)
      Tests  351 passed (351)
   Start at  12:19:49
   Duration  17.64s (transform 9.18s, setup 0ms, collect 23.55s, tests 67.17s, environment 14.68s, prepare 4.70s)


Duration milliseconds: 18628
Exit code: 0
