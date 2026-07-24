# test Results

Command: npm test --if-present

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v20.19.6/bin


> sfpcl-lms@1.0.0 test
> vitest run

[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

 RUN  v3.2.6 /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_083044_normal_run/sfpcl-lms

 ✓ src/pages/registers/RegistersHub.test.tsx (8 tests) 798ms
 ✓ src/pages/settings/SettingsHub.test.tsx (10 tests) 1376ms
   ✓ SettingsHub Approval Matrix panel > permits a canonical manager to submit a complete successor version as a pending proposal  630ms
   ✓ SettingsHub remaining panels > creates a complete successor as a separate audited draft for a canonical policy manager  370ms
 ✓ src/pages/repayments/RepaymentsHub.test.tsx (9 tests) 1513ms
   ✓ 010MA Repayments Hub wiring > posts one governed direct attempt, displays backend allocation, and refreshes reads  472ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: Amount must be a positive decimal.  335ms
   ✓ 010MA Repayments Hub wiring > shows backend posting denial without retry or canonical refresh: AuthSessionError: This bank reference is already recorded.  315ms
 ✓ src/pages/appraisal/AppraisalWorkbench.container.test.tsx (14 tests) 1813ms
   ✓ default AppraisalWorkbench authenticated HTTP container > calculates a limit from entered source IDs and refreshes four reads  320ms
   ✓ default AppraisalWorkbench authenticated HTTP container > posts the rejected Credit Manager decision once  311ms
 ✓ src/pages/documentation/DocumentationHub.test.tsx (18 tests) 2524ms
   ✓ 008M2 documentation workspace contract > posts a server-owned approval and refetches once without optimism  600ms
   ✓ 008M2 documentation workspace contract > keeps a conflict visible with no optimistic change, retry, or refetch  428ms
 ✓ src/pages/servicing/InterestMonitoringWorkspaces.test.tsx (6 tests) 428ms
 ✓ src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx (7 tests) 1001ms
   ✓ MP05 loan-limit display authority (006Z2 interim regression) > shows independent 400, 403, and 409 errors without retry or projection refetch  560ms
 ✓ src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx (8 tests) 676ms
   ✓ member portal documentation actions > renders server-owned actions and performs one canonical refetch after upload  408ms
 ✓ src/pages/loan-accounts/LoanAccount360.test.tsx (6 tests) 461ms
 ✓ src/pages/borrower/portal/PortalMemberViews.test.tsx (7 tests) 255ms
 ✓ src/components/layout/Header.notifications.test.tsx (9 tests) 482ms
 ✓ src/pages/borrower/portal/loans/PortalLoanViews.test.tsx (6 tests) 334ms
 ✓ src/pages/borrower/portal/disbursement/MP14_DisbursementStatus.test.tsx (6 tests) 386ms
 ✓ src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx (2 tests) 520ms
   ✓ MP11 deficiency response > uploads a server-contracted response, refetches canonical state, and resubmits  414ms
 ✓ src/pages/search/GlobalSearchResults.test.tsx (5 tests) 580ms
 ✓ src/pages/sanction/SanctionWorkbench.test.tsx (39 tests) 5407ms
   ✓ SanctionWorkbench authenticated container > renders the authoritative total and replaces the queue from the next server page  410ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action detail refresh finishes  359ms
   ✓ SanctionWorkbench authenticated container > keeps a newer denied state authoritative when an action detail refresh fails later  326ms
   ✓ SanctionWorkbench authenticated container > keeps a newer malformed state authoritative when an action detail refresh fails later  334ms
   ✓ SanctionWorkbench authenticated container > keeps a newer empty state authoritative when an action detail refresh fails later  328ms
   ✓ SanctionWorkbench authenticated container > keeps a newer filter authoritative while an action decision refresh finishes  366ms
   ✓ SanctionWorkbench authenticated container > loads frozen case truth and approves through the exact case boundary before canonical refresh  329ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Reject request  378ms
   ✓ SanctionWorkbench authenticated container > requires a reason and sends the exact Return for Clarification request  337ms
   ✓ SanctionWorkbench authenticated container > uploads three application-scoped legal files before recording bounded special-case evidence  537ms
 ✓ src/pages/borrower/portal/PortalCommunicationsViews.test.tsx (5 tests) 695ms
   ✓ MP19-MP24 member communication views > renders all MP24 guide sections, validates required fields, submits, and shows resolution  482ms
 ✓ src/pages/applications/WitnessPanel.container.test.tsx (10 tests) 1158ms
   ✓ mounted witness resource actions > captures with the exact body and refetches the canonical collection once  379ms
 ✓ src/pages/members/MemberGovernanceForm.test.tsx (5 tests) 2286ms
   ✓ MemberGovernanceForm > submits the institution create variant without individual identity/profile fields  1138ms
   ✓ MemberGovernanceForm > submits every individual registration profile field  885ms
 ✓ src/pages/disbursement/DisbursementHub.test.tsx (4 tests) 419ms
 ✓ src/pages/compliance/AuditorEpic011View.test.tsx (4 tests) 222ms
 ✓ src/pages/members/MemberGovernanceForm.container.test.tsx (16 tests) 4610ms
   ✓ MemberGovernanceForm production container > routes Directory registration into canonical Profile readback with the exact create ledger  2456ms
 ✓ src/pages/disbursement/PaymentAuthorisationHub.test.tsx (5 tests) 977ms
   ✓ 009K CFC payment authorisation workspace > shows CFC actions only when the backend projects them and posts the decision reason  336ms
   ✓ 009K CFC payment authorisation workspace > surfaces backend duplicate UTR and permission errors without optimistic success  408ms
 ✓ src/services/authSession.test.ts (39 tests) 33ms
 ✓ src/services/servicingApi.test.ts (13 tests) 24ms
 ✓ src/pages/members/MemberProfile.container.test.tsx (4 tests) 353ms
 ✓ src/services/portalApi.test.ts (10 tests) 21ms
 ✓ src/pages/members/MemberProfile.test.tsx (26 tests) 214ms
 ✓ src/components/layout/Header.search.test.tsx (1 test) 234ms
 ✓ src/services/applicationIntakeApi.test.ts (5 tests) 7ms
 ✓ src/pages/defaults/DefaultRecoveryHub.test.tsx (1 test) 689ms
   ✓ 011F recovery execution surface > uses the approved backend action and uploaded evidence to initiate S57  688ms
 ✓ src/services/creditAssessmentApi.test.ts (5 tests) 8ms
 ✓ src/services/approvalRegistersApi.test.ts (5 tests) 6ms
 ✓ src/pages/applications/ApplicationDetail.test.tsx (9 tests) 91ms
 ✓ src/services/navigationPermissions.test.ts (9 tests) 8ms
 ✓ src/pages/members/Borrower360.test.tsx (4 tests) 79ms
 ✓ src/pages/appraisal/AppraisalWorkbench.test.tsx (22 tests) 180ms
 ✓ src/services/disbursementApi.test.ts (3 tests) 13ms
 ✓ src/services/tracerApi.test.ts (2 tests) 6ms
 ✓ src/pages/applications/CompletenessWorkbench.test.tsx (5 tests) 66ms
 ✓ src/pages/Dashboard.test.tsx (13 tests) 45ms
 ✓ src/pages/notifications/NotificationsCenter.test.tsx (6 tests) 34ms
 ✓ src/services/loanPolicyApi.test.ts (2 tests) 6ms
 ✓ src/pages/members/MemberDirectory.test.tsx (5 tests) 28ms
 ✓ src/utils/applicationDisplay.test.ts (5 tests) 2ms
 ✓ src/contexts/RoleContext.test.tsx (2 tests) 13ms
 ✓ src/pages/applications/ApplicationList.test.tsx (2 tests) 90ms
 ✓ src/pages/profile/MyProfile.test.tsx (1 test) 9ms
 ✓ src/playwright.seed.test.ts (3 tests) 4ms
 ✓ src/pages/applications/NomineeSelectionViews.test.tsx (3 tests) 7ms
 ✓ src/utils/formatMoney.test.ts (1 test) 2ms
 ✓ src/pages/borrower/portal/auth/MP00_Login.test.tsx (2 tests) 8ms
 ✓ src/playwrightBrowser.test.ts (4 tests) 2ms
 ✓ src/services/demoAuthFlag.test.tsx (3 tests) 1102ms
   ✓ VITE_ENABLE_DEMO_AUTH real App/RoleProvider boundary (005FA4) > fails closed when the flag is unset  991ms

 Test Files  54 passed (54)
      Tests  424 passed (424)
   Start at  09:14:18
   Duration  10.31s (transform 4.59s, setup 0ms, collect 15.51s, tests 32.30s, environment 8.20s, prepare 3.28s)


Duration milliseconds: 11056
Exit code: 0
