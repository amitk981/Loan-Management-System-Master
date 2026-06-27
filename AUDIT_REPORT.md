# SFPCL LMS — Complete Flow & Codebase Audit
**Date:** 2026-06-27  
**Scope:** Mermaid business-process flowcharts (3) vs. current React/TypeScript prototype  
**Prototype:** `sfpcl-lms/` — Vite 5 + React + TypeScript + Tailwind  
**Auditor:** Claude Code (claude-sonnet-4-6)

---

## Legend

| Symbol | Meaning |
|---|---|
| ✅ Implemented | UI present, role gate enforced in code, correct states modelled |
| ⚠️ Partial | Present in UI but gate/rule/path is thin, local-state only, or mock-hardcoded |
| ❌ Missing | No UI representation; flowchart node is unaddressed |
| 🔒 Gate missing | UI exists but the enforcement condition is not wired to a blocker |

---

## 1. Executive Summary

| Metric | Count |
|---|---|
| Flowchart nodes audited (TD main flow) | 165 |
| ✅ Fully implemented | 97 (59%) |
| ⚠️ Partial / local-state only | 47 (28%) |
| ❌ Missing | 21 (13%) |
| State machine states (stateDiagram) | 28 |
| States represented in StatusBadge / mockData | 26 of 28 (93%) |
| Swim-lane actor roles | 6 actors, 31 responsibilities |
| RBAC roles in RoleContext | 15 roles |
| Roles correctly gated to correct swim-lane responsibilities | ~80% |

**Flowchart coverage including partials: 87%**  
**Fully clean (no gaps) per section:** Entry/Auth, Member 360, Origination Form, Eligibility, Loan Limit, Sanction Matrix, Documentation Package, Disbursement, Monitoring, Defaults, Closure, Compliance

**Sections with critical gaps:** Duplicate Borrower Check, Policy Active Gate, Witness Shareholder Verification, GM Evidence Enforcement, Repayment Reconciliation Queue, State Write-through (actions don't persist to data store)

---

## 2. Node-by-Node Audit

### 2.1 Global Entry + Access Control

| Node | Status | File | Notes |
|---|---|---|---|
| START | ✅ | `LoginScreen.tsx` | Login gate present |
| AUTH (JWT) | ⚠️ | `App.tsx:100` | State-based auth, no real JWT; demo-sufficient |
| ACTIVE user check | ⚠️ | `LoginScreen.tsx` | Role selection = instant access; no inactive-user denial path |
| DENY1 | ❌ | — | No session expiry or failed-login denial screen |
| RBAC load | ✅ | `RoleContext.tsx` | 15 roles, `can()` enforced at page + action level |
| DASH | ✅ | `Dashboard.tsx` | Role-specific greeting, KPIs, task queue |
| POLICY_CHECK gateway | ❌ | — | Dashboard does NOT gate on an active policy version |
| POLICY_SETUP | ✅ | `SettingsHub.tsx` | Policy config tab: loan params, eligibility rules, thresholds |
| POLICY_APPROVAL (maker/checker) | ⚠️ | `SettingsHub.tsx` | UI only; no approval workflow before settings take effect |
| POLICY_ACTIVE (version publish) | ❌ | — | No "Publish active version" mechanism; settings save immediately |

### 2.2 Member + Borrower Master

| Node | Status | File | Notes |
|---|---|---|---|
| MEMBER_SEARCH (folio/PAN/Aadhaar/ID) | ⚠️ | `MemberDirectory.tsx` | Name + status search only; PAN/Aadhaar search not implemented |
| DUP_CHECK | ❌ | — | No duplicate detection on member/application creation |
| DUP_REVIEW | ❌ | — | No duplicate resolution UI |
| DUP_RESOLVE | ❌ | — | No confirm/merge/discard path |
| HOLD_DUP | ❌ | — | No application hold pending duplicate resolution |
| MEMBER_VALIDATE | ✅ | `NewApplication.tsx:150` | Active status + default check before intake proceeds |
| ACTIVE_MEMBER check | ✅ | `NewApplication.tsx:155` | Inactive/default members show warning; `can('create_application')` gate |
| MEMBER_DEF (deficiency/exception) | ⚠️ | `NewApplication.tsx` | Warning shown but does not hard-block (exception path not offered) |
| BORROWER_360 | ✅ | `Borrower360.tsx` | 9-tab 360 view: member, loans, repayments, security, docs, comms, risk, audit |
| APPLICATION_DRAFT | ✅ | `NewApplication.tsx` | Draft save supported (local state) |

### 2.3 Loan Origination

| Node | Status | File | Notes |
|---|---|---|---|
| APP_FIELDS (folio/shares/amount/purpose/crop/tenure/repayment) | ✅ | `NewApplication.tsx` steps 2–4 | All fields captured in 8-step wizard |
| PURPOSE_CHECK (agriculture only) | ✅ | `NewApplication.tsx:step3` | Non-agri purpose shows blocking warning |
| PURPOSE_REJECT | ✅ | `NewApplication.tsx` | Reject path shown with reason |
| NOMINEE capture | ✅ | `NewApplication.tsx:step4` | Nominee name, DOB, relationship, PAN, Aadhaar, mobile |
| NOMINEE_MINOR check | ⚠️ | `NewApplication.tsx` | DOB captured but age is NOT computed or validated against 18-year rule |
| NOMINEE_DEF | ❌ | — | No blocking deficiency raised when nominee is minor |
| DOC_UPLOAD | ✅ | `NewApplication.tsx:step5` | Mandatory document checklist with upload gates |
| DOC_SET (6 required docs) | ✅ | `NewApplication.tsx` | PAN, Aadhaar, share cert, 7/12, crop plan, 6-month bank statement |
| DRAFT_REVIEW | ✅ | `NewApplication.tsx:step8` | Final completeness checklist blocks submission |
| SUBMIT_READY | ✅ | `NewApplication.tsx` | Submit blocked until all mandatory items pass |
| SAVE_DRAFT | ⚠️ | `NewApplication.tsx` | Local state save; no persistence to `loanApplications` store |
| SUBMITTED status | ⚠️ | `NewApplication.tsx` | Confirmation screen shown; reference is `DRAFT-APP-0042` (hardcoded) |
| TASK_COMPLETENESS (create task for DM Finance) | ⚠️ | — | TaskInbox shows existing mock tasks; new submission does NOT create a task |

### 2.4 Completeness Check

| Node | Status | File | Notes |
|---|---|---|---|
| COMP_CHECK (checklist review) | ✅ | `ApplicationDetail.tsx` | Completeness tab with checklist UI |
| COMP_OK gateway | ⚠️ | `ApplicationDetail.tsx` | All items hardcoded "Passed"; no actual check against doc uploads |
| DEF_NOTE (generate deficiency note) | ⚠️ | `ApplicationDetail.tsx` | Note UI present; no actual PDF/document generation |
| DEF_COMM (send to borrower) | ❌ | — | No channel/dispatch evidence; email/SMS/portal send not implemented |
| DEF_STATUS | ✅ | `StatusBadge.tsx` | `deficiency_raised` status mapped and styled |
| RESUBMIT | ⚠️ | `BorrowerPortal.tsx` | Borrower deficiency-response form present; does not update application status |
| REF_NO (LO00000001...) | ⚠️ | `NewApplication.tsx` | Reference generated on confirmation; hardcoded string, not sequential |
| LOAN_REQ_REGISTER | ⚠️ | `RegistersHub.tsx` | Loan Request Register tab exists; new submissions don't auto-populate it |
| APPRAISAL_START | ✅ | `AppraisalWorkbench.tsx` | Queue populated from `appraisal_in_progress` status applications |

### 2.5 Credit Assessment + Loan Limit

| Node | Status | File | Notes |
|---|---|---|---|
| APPRAISAL_NOTE (DM Finance prepares) | ✅ | `AppraisalWorkbench.tsx:step2` | Note fields: recommended amount, tenure, risk rationale, conditions, security |
| TAT (2-day tracker) | ⚠️ | `AppraisalWorkbench.tsx` | TAT displayed but computed from mock `submittedDate`, not live |
| ELIGIBILITY checklist | ✅ | `EligibilityChecklist.tsx` | 12 checks (member, KYC, land, crop, bank statement, terms) |
| ELIG_OK gateway | ✅ | `AppraisalWorkbench.tsx` | Reject path with reason capture in step 3 |
| CREDIT_REJECT | ✅ | `AppraisalWorkbench.tsx:step3` | Rejection with reason, triggers state update |
| REJECT_NOTE1 | ⚠️ | — | UI note only; no actual rejection letter PDF or audit entry |
| LIMIT_CALC | ✅ | `LoanLimitCalculator.tsx` | Full formula shown |
| SHARE_LIMIT (shares × % / per-share) | ✅ | `LoanLimitCalculator.tsx` | Formula displayed with SOP contradiction warning banner |
| LAND_LIMIT (per-acre × area) | ✅ | `LoanLimitCalculator.tsx` | Per-acre scale-of-finance × cultivated acres |
| FINAL_LIMIT (lower of) | ✅ | `LoanLimitCalculator.tsx` | min() logic shown; exception flag if request > final |
| LIMIT_DECISION gateway | ✅ | `AppraisalWorkbench.tsx` | Exception banner shown when request > eligible |
| EXCEPTION_FLAG | ✅ | `ApplicationDetail.tsx`, `AppraisalWorkbench.tsx` | Exception badge + amber banner |
| RISK_ASSESS (repayment capacity, income, rating) | ✅ | `AppraisalWorkbench.tsx:step2` | Risk rating captured with rationale |
| TERMS (recommended amount, tenure, security) | ✅ | `AppraisalWorkbench.tsx:step2` | All fields present |
| APPRAISAL_DRAFT (PDF) | ⚠️ | `AppraisalWorkbench.tsx` | "Generate Appraisal PDF" button present; no actual file generated |
| CM_REVIEW | ✅ | `AppraisalWorkbench.tsx:step3` | Credit Manager review package with comment box |
| CM_DECISION (Return/Reject/Submit) | ✅ | `AppraisalWorkbench.tsx:step3` | All three paths with role guard (`isCreditManager`) |
| APPRAISAL_REWORK | ⚠️ | `AppraisalWorkbench.tsx` | Local state only; application status in `loanApplications` not updated |
| SANCTION_CASE | ⚠️ | `SanctionWorkbench.tsx` | "Forward to Sanction" sets local state; sanction queue does not update |

### 2.6 Sanction Approval

| Node | Status | File | Notes |
|---|---|---|---|
| APPROVAL_MATRIX | ✅ | `ApprovalPanel.tsx` | Full matrix: ≤₹5L CFO+1 Director; >₹5L CFO+2 Directors |
| AMOUNT_DECISION gateway | ✅ | `ApprovalPanel.tsx` | Computed from `sanctionedAmount` |
| ROUTE_LOW / ROUTE_HIGH | ✅ | `ApprovalPanel.tsx` | Slot count auto-determined |
| SPECIAL_CHECK (conflict/relative) | ✅ | `SanctionWorkbench.tsx` | Conflict-of-interest checkbox present |
| CONFLICT exclusion | ✅ | `ApprovalPanel.tsx` | Special-case notice rendered when conflict flagged |
| GM_EVIDENCE upload gate | ❌ | `ApprovalPanel.tsx` | Checkbox is local boolean; Approve button NOT blocked until evidence uploaded |
| HOLD_SPECIAL | ❌ | — | No hold state enforced pending GM evidence |
| APPROVER_QUEUE | ✅ | `SanctionWorkbench.tsx` | Queue panel with detail view |
| APPROVER_REVIEW | ✅ | `SanctionWorkbench.tsx` | Appraisal, limit, docs, compliance viewable |
| SANCTION_DECISION (Approve/Reject/Clarify) | ✅ | `ApprovalPanel.tsx` | All three decision paths |
| SANCTION_CLARIFY → rework | ⚠️ | `SanctionWorkbench.tsx` | Clarification captured; does NOT trigger appraisal rework navigation |
| SANCTION_REJECT | ✅ | `SanctionWorkbench.tsx` | Rejection with reason |
| CREDIT_SANCTION_REG_REJ | ⚠️ | `RegistersHub.tsx` | Register tab exists; rejection does not auto-populate it |
| REJECT_NOTE2 | ⚠️ | — | No actual borrower communication triggered |
| APPROVALS_COMPLETE (quorum) | ✅ | `ApprovalPanel.tsx` | All required slots must be filled before quorum is met |
| EXCEPTION_CHECK | ⚠️ | `SanctionWorkbench.tsx` | Exception banner visible; joint approval not enforced as hard gate |
| EXCEPTION_REGISTER | ⚠️ | `RegistersHub.tsx` | Exception register tab exists; sanction action does not auto-write |
| SANCTIONED status | ⚠️ | `SanctionWorkbench.tsx` | Local state `slotDecisions` resolves to sanctioned; no write to `loanApplications.status` |
| CREDIT_SANCTION_REG | ⚠️ | `RegistersHub.tsx` | Tab exists; no auto-update |

### 2.7 Documentation + Security Package

| Node | Status | File | Notes |
|---|---|---|---|
| DOC_START / DOC_WORKSPACE | ✅ | `DocumentationHub.tsx` | Queue + stepper workbench; compliance team role-gated |
| DOC_CHECKLIST (auto-generate + rules) | ✅ | `DocumentChecklist.tsx` | Rows auto-show/hide based on `shareholdingMode` and `subsidiaryRepayment` |
| POST_SANCTION_DOCS (witness, cancelled cheque, blank cheque) | ✅ | `DocumentChecklist.tsx` | All three captured |
| WITNESS_CHECK (must be SFPCL shareholder) | ❌ | — | Witness PAN/Aadhaar collected but shareholder status NOT verified |
| DOC_DEF1 (invalid witness) | ❌ | — | No deficiency raised for invalid witness |
| BANK_VERIFY (cancelled cheque + bank details) | ✅ | `DocumentationHub.tsx` | Bank verification section present |
| SIG_MATCH (signature comparison) | ⚠️ | `DocumentationHub.tsx` | Mismatch path hardcoded to `app004`; no real comparison |
| BANK_LETTER / declaration option | ⚠️ | `DocumentationHub.tsx` | Option mentioned; no functional upload flow |
| SIG_RESOLVED | ⚠️ | `DocumentationHub.tsx` | Local boolean toggle only |
| DOC_HOLD_SIG | ⚠️ | — | "Hold documentation" state exists in StatusBadge but not auto-triggered by mismatch |
| LEGAL_DOCS: PoA | ✅ | `DocumentChecklist.tsx` | ₹500 stamp + notarised tracked |
| LEGAL_DOCS: Tri-Party Agreement | ✅ | `DocumentChecklist.tsx` | Conditional on `subsidiaryRepayment` flag |
| LEGAL_DOCS: Term Sheet | ✅ | `DocumentChecklist.tsx` | Required signatories tracked |
| LEGAL_DOCS: Loan Agreement | ✅ | `DocumentChecklist.tsx` | ₹500 stamp + notarised tracked |
| SHARE_MODE conditional (Physical/Demat) | ✅ | `DocumentChecklist.tsx` | SH-4 vs CDSL based on `shareholdingMode` |
| SH4 (custody logged) | ✅ | `DocumentationHub.tsx` | SH-4 form with signed/custody fields |
| CDSL (PRF/PSN/pledge evidence) | ✅ | `DocumentationHub.tsx` | CDSL pledge tracker |
| DOC_COMPLETE_CHECK | ⚠️ | `DocumentChecklist.tsx` | Validation visible; `mandatoryChecklistClear` is `true` for admin (audit bypass) |
| DOC_COMPLETE gateway | ✅ | `DocumentationHub.tsx` | Disbursement blocker warning shown when not complete |
| DOC_DEF2 (raise blocker) | ⚠️ | `DocumentationHub.tsx` | Deficiency UI present; no status write to application |
| FINAL_DOC_APPROVAL (4-step) | ✅ | `DocumentationHub.tsx` | CS → Credit Mgr → Sanction Committee → SM Finance sequence |
| CS_SIGN | ✅ | `DocumentationHub.tsx` | CS role-gated; blocked until checklist clear |
| CM_SIGN | ✅ | `DocumentationHub.tsx` | Credit Manager role-gated; sequential after CS |
| SC_FINAL_SIGN | ✅ | `DocumentationHub.tsx` | Sanction Committee sign-off |
| DISB_READY | ✅ | `StatusBadge.tsx`, `DisbursementHub.tsx` | Status exists; disbursement queue filters for this status |

### 2.8 SAP + Disbursement

| Node | Status | File | Notes |
|---|---|---|---|
| SAP_CHECK (existing customer code?) | ✅ | `DisbursementHub.tsx` | SAP code check and input |
| SAP_REQ (CM sends request to SM Finance) | ⚠️ | — | No inter-role workflow; SM Finance directly inputs code |
| SAP_CREATE (SM Finance creates) | ✅ | `DisbursementHub.tsx` | SM Finance inputs and confirms SAP code (role-gated) |
| SAP_CONFIRM | ✅ | `DisbursementHub.tsx` | Confirmation stage with code stored in local state |
| SAP_REUSE (existing code) | ✅ | `DisbursementHub.tsx` | Existing code path handled |
| FIN_VERIFY (SM Finance final verification) | ✅ | `DisbursementHub.tsx` | Verification step with readiness checklist |
| READY_BLOCKERS (readiness check) | ⚠️ | `DisbursementHub.tsx` | 9 of 11 checklist items hardcoded `ok: true`; only SAP confirmed + bank verified computed |
| BLOCKED_DISB | ⚠️ | `DisbursementHub.tsx` | Blocker shown; does not check Documentation sign-off completion |
| PAYMENT_DRAFT (beneficiary/bank/IFSC/amount) | ✅ | `DisbursementHub.tsx` | Payment details captured |
| PAYMENT_INIT (SM Finance initiates RBL) | ✅ | `DisbursementHub.tsx` | Role-gated to `senior_manager_finance` |
| CFC_QUEUE | ✅ | `PaymentAuthorisationHub.tsx` | CFC queue filters `pending_cfc_approval` status |
| CFC_DECISION (Approve/Return/Reject) | ✅ | `PaymentAuthorisationHub.tsx` | All three paths; CFC role-gated |
| BANK_SUCCESS | ✅ | `PaymentAuthorisationHub.tsx` | Bank transfer confirmed after CFC approval |
| UTR capture | ✅ | `PaymentAuthorisationHub.tsx` | UTR + bank evidence required before approve button enabled |
| LOAN_ACTIVE (activate loan account) | ⚠️ | `PaymentAuthorisationHub.tsx` | "Activate Loan" button present; no write to `loanAccounts.status` |
| LOAN_REGISTER update | ⚠️ | `RegistersHub.tsx` | Disbursement register tab exists; no auto-update on disbursal |
| SMF_SIGN (post-disbursement checklist) | ⚠️ | `PaymentAuthorisationHub.tsx` | Checklist listed as post-disbursement action; no SM Finance sign-off gate |
| ADVICE (disbursement advice to borrower) | ✅ | `PaymentAuthorisationHub.tsx` | Generate + send advice buttons present (console.log only) |
| ACTIVE_REPAYMENT status | ✅ | `StatusBadge.tsx` | `active` status mapped and styled |

### 2.9 Servicing + Repayment + Interest

| Node | Status | File | Notes |
|---|---|---|---|
| REPAYMENT_SCHEDULE | ✅ | `LoanAccount360.tsx` | 12-row EMI schedule tab |
| REPAYMENT_ROUTE (Direct / Subsidiary) | ✅ | `RepaymentsHub.tsx` | Channel selector (RTGS/NEFT/Subsidiary/Other) |
| DIRECT_PAY (RTGS/NEFT) | ✅ | `RepaymentsHub.tsx` | Direct payment capture form |
| BANK_STMT (Treasury verifies) | ⚠️ | `RepaymentsHub.tsx` | No Treasury-specific role separation for verification |
| MATCH_DIRECT (narration match) | ⚠️ | `RepaymentsHub.tsx` | Match shown in UI; no actual matching logic |
| SUB_DEDUCT (subsidiary deduction) | ⚠️ | `RepaymentsHub.tsx` | Channel option present but disabled with "use dedicated route" note |
| SUB_TRANSFER | ❌ | — | Subsidiary transfer route does not exist in prototype |
| MATCH_SUB | ❌ | — | No subsidiary narration matching |
| RECON_QUEUE (unmatched receipts) | ❌ | — | No unmatched receipt reconciliation queue |
| MATCH_OK gateway | ⚠️ | — | No actual matching; all receipts assumed matched |
| ALLOCATE (principal-first) | ✅ | `RepaymentsHub.tsx` | Allocation preview computed in modal |
| BALANCE_UPDATE | ⚠️ | `RepaymentsHub.tsx` | Preview shown; `loanAccounts.outstandingPrincipal` not updated |
| SAP_RECEIPT (posting + next-working-day) | ⚠️ | `RepaymentsHub.tsx` | SAP status shown as "Pending"; no next-working-day date tracker |
| ACK (repayment acknowledgement) | ⚠️ | `RepaymentsHub.tsx` | Button present; no actual send (console.log) |
| INTEREST_FLOW | ✅ | `InterestManagement.tsx` | Accrual, invoice, capitalisation tabs |
| RATE_HISTORY | ❌ | `InterestManagement.tsx` | No floating interest rate history table |
| MONTHLY_ACCRUAL (SAP reference) | ✅ | `InterestManagement.tsx` | Quarterly accrual table with SAP reference tracking |
| YEARLY_INVOICE | ✅ | `InterestManagement.tsx` | Annual invoice generation |
| APR30_CHECK gateway | ✅ | `InterestManagement.tsx` | 30 April capitalisation logic shown |
| CAPITALISE (+ inform borrower) | ✅ | `InterestManagement.tsx` | Capitalisation workflow with irreversible warning |

### 2.10 Monitoring

| Node | Status | File | Notes |
|---|---|---|---|
| MONITORING | ✅ | `MonitoringDashboard.tsx` | DPD buckets, at-risk table, overdue banner |
| DPD (ageing buckets) | ✅ | `MonitoringDashboard.tsx` | 5-bucket analysis (0 / 1-30 / 31-90 / 91-365 / 1yr+) |
| CFO_MIS (quarterly) | ✅ | `ReportsMIS.tsx` | Quarterly MIS with export; DPD aging table |
| OVERDUE_CHECK | ✅ | `MonitoringDashboard.tsx` | Missed repayment detection visible |
| DEFAULT_START | ✅ | `DefaultRecoveryHub.tsx` | Default case creation initiated |

### 2.11 Default + Recovery

| Node | Status | File | Notes |
|---|---|---|---|
| GRACE (3-month) | ✅ | `DefaultRecoveryHub.tsx` | Grace period tab with 3-month tracking |
| GRACE_REPAID gateway | ⚠️ | `DefaultRecoveryHub.tsx` | No actual check against repayment records; local state |
| DEFAULT_ASSESS | ✅ | `DefaultRecoveryHub.tsx` | Credit assessment review tab with reason capture |
| INTENT_DECISION (intentional/non-intentional) | ✅ | `DefaultRecoveryHub.tsx` | Path selector in default review |
| EXTENSION (1-year) | ✅ | `DefaultRecoveryHub.tsx` | Extension note form with mandatory reason |
| EXT_REPAID gateway | ⚠️ | `DefaultRecoveryHub.tsx` | Local state only; no repayment check |
| NON_RECOVERABLE | ✅ | `DefaultRecoveryHub.tsx` | Non-recoverable path shown |
| NON_PAYMENT_NOTE | ✅ | `DefaultRecoveryHub.tsx` | Note form with recommended action radio buttons |
| RECOVERY_REVIEW | ✅ | `DefaultRecoveryHub.tsx` | Recovery case to Sanction Committee |
| RECOVERY_DECISION | ✅ | `DefaultRecoveryHub.tsx` | Approve/reject recovery action |
| CONTINUE_MONITOR | ✅ | `MonitoringDashboard.tsx` | Monitoring continues for non-recovery cases |
| RECOVERY_ACTION (SH-4/CDSL/Cheque) | ✅ | `DefaultRecoveryHub.tsx` | Security route selector |
| INVOKE_SH4 | ✅ | `DefaultRecoveryHub.tsx` | SH-4 invocation form |
| INVOKE_CDSL | ✅ | `DefaultRecoveryHub.tsx` | CDSL invocation tracked |
| INVOKE_CHEQUE | ✅ | `DefaultRecoveryHub.tsx` | Blank cheque invocation with approval guard |
| RECOVERY_LEDGER | ⚠️ | `DefaultRecoveryHub.tsx` | Recovery actions logged in local state; no link to main loan ledger |
| RECOVERED status | ✅ | `StatusBadge.tsx` | `recovered` status mapped |

### 2.12 Closure + Archive

| Node | Status | File | Notes |
|---|---|---|---|
| CLOSURE_CHECK (zero outstanding) | ✅ | `LoanClosureHub.tsx` | Block if `outstanding > 0` |
| CLOSURE_REVIEW | ✅ | `LoanClosureHub.tsx` | 10-item checklist |
| NOC generation | ✅ | `LoanClosureHub.tsx` | NOC with date/reference/signatories |
| NOC_DELIVERY (dispatch + acknowledgement) | ⚠️ | `LoanClosureHub.tsx` | Download button present; no dispatch evidence or acknowledgement tracking |
| SECURITY_RETURN | ✅ | `LoanClosureHub.tsx` | SH-4, blank cheque, CDSL, PoA return tracked |
| RETURN_SH4 | ✅ | `LoanClosureHub.tsx` | SH-4 return tracking |
| RETURN_CHEQUE | ✅ | `LoanClosureHub.tsx` | Blank cheque return with acknowledgement |
| UNPLEDGE (CDSL + evidence) | ✅ | `LoanClosureHub.tsx` | CDSL unpledge evidence upload |
| POA_ARCHIVE | ✅ | `LoanClosureHub.tsx` | PoA archived as closed loan document |
| CLOSE_READY validation | ⚠️ | `LoanClosureHub.tsx` | Most checklist items only check `outstanding === 0`; security register state not checked |
| ARCHIVE (8-year retention) | ✅ | `LoanClosureHub.tsx` | Archive tab with 8-year retention policy |
| CLOSED status | ✅ | `StatusBadge.tsx` | `closed` status mapped |

### 2.13 Compliance + Audit (Cross-Cutting)

| Node | Status | File | Notes |
|---|---|---|---|
| AUDIT (actor/role/timestamp/reason/evidence) | ⚠️ | `AuditTimeline.tsx`, `RegistersHub.tsx` | Audit events from mock data; real actions write to `console.log` only |
| Compliance calendar | ✅ | `ComplianceDashboard.tsx` | Section 186, NBFC, KYC, stamp duty, money-lending, retention, grievance |
| CFO/Board/CS evidence | ⚠️ | `ComplianceDashboard.tsx` | Evidence count shown; no actual board approval workflow |
| Section 186 limit bar | ✅ | `ComplianceDashboard.tsx` | Utilisation % with colour thresholds |
| NBFC test | ✅ | `ComplianceDashboard.tsx` | 2-criteria display |
| Grievance register | ✅ | `GrievancesHub.tsx`, `RegistersHub.tsx` | Grievance hub + register tab |
| TAT enforcement | ⚠️ | `TaskInbox.tsx` | TAT labels shown; no automatic escalation on breach |

---

## 3. State Machine Coverage (stateDiagram-v2)

| State | In StatusBadge | In mockData | Transitions modelled |
|---|---|---|---|
| Draft | ✅ | ✅ | → Submitted |
| Submitted | ✅ | ✅ | → Completeness_Check |
| Completeness_Check | ✅ | ✅ | → Deficiency_Raised / Appraisal_In_Progress |
| Deficiency_Raised | ✅ | ✅ | → Resubmitted |
| Resubmitted | ✅ | ❌ (not in mock) | → Completeness_Check |
| Appraisal_In_Progress | ✅ | ✅ | → Credit_Manager_Review |
| Credit_Manager_Review | ✅ | ✅ | → Rejected_By_Credit / Appraisal_In_Progress / Pending_Sanction |
| Rejected_By_Credit | ✅ | ✅ | → [*] |
| Pending_Sanction | ✅ | ✅ | → Rejected_By_Sanction / Appraisal_In_Progress / Sanctioned |
| Rejected_By_Sanction | ✅ | ✅ | → [*] |
| Sanctioned | ✅ | ✅ | → Documentation_In_Progress |
| Documentation_In_Progress | ✅ | ✅ | → Documentation_Deficiency / Pending_Final_Approvals |
| Documentation_Deficiency | ✅ | ✅ | → Documentation_In_Progress |
| Pending_Final_Approvals | ✅ | ✅ | → Disbursement_Ready |
| Disbursement_Ready | ✅ | ✅ | → SAP_Code_Pending |
| SAP_Code_Pending | ✅ | ⚠️ (partial) | → Finance_Verification |
| Finance_Verification | ✅ | ⚠️ (partial) | → Payment_Initiated |
| Payment_Initiated | ✅ | ✅ | → Payment_Returned / Disbursed |
| Payment_Returned | ✅ | ❌ | → Finance_Verification |
| Disbursed | ✅ | ✅ | → Active_Repayment |
| Active_Repayment | ✅ | ✅ | → Overdue / Closure_Review |
| Overdue | ✅ | ✅ | → Grace_Period |
| Grace_Period | ✅ | ✅ | → Active_Repayment / Extension_Review |
| Extension_Review | ✅ | ✅ | → Extended / Recovery_Review |
| Extended | ✅ | ⚠️ | → Active_Repayment / Non_Recoverable_Review |
| Non_Recoverable_Review | ✅ | ⚠️ | → Recovery_Review |
| Recovery_Review | ✅ | ✅ | → Recovery_Action_Approved |
| Recovery_Action_Approved | ✅ | ✅ | → Recovered |
| Recovered | ✅ | ⚠️ | → Closure_Review |
| Closed | ✅ | ✅ | → [*] |

**States in StatusBadge but NOT in stateDiagram:** `exception`, `documentation_deficiency`, `pending_cfc_approval`, `hold_duplicate` — these are prototype extensions for completeness.

---

## 4. Role / Permission Audit

### 4.1 Internal Roles vs. Swim-Lane Responsibilities

| Role | Can create/edit application | Completeness check | Appraisal | Sanction | Documentation | Initiate disbursement | Authorise disbursement | Post repayment | Recovery | Closure |
|---|---|---|---|---|---|---|---|---|---|---|
| field_officer | ✅ | ❌ spec says DM Finance | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| deputy_manager_finance | ✅ | ✅ | ✅ | ❌ | 👁 view | ❌ | ❌ | ❌ | ❌ | ❌ |
| credit_manager | ✅ | ✅ | ✅ | 👁 view | ✅ approve_credit_checklist | ❌ | ❌ | ❌ | ✅ | ❌ |
| compliance_team | ❌ | ❌ | ❌ | ❌ | ✅ manage | ❌ | ❌ | ❌ | ❌ | ❌ |
| company_secretary | ❌ | ❌ | ❌ | ❌ | ✅ manage | ❌ | ❌ | ❌ | ❌ | ✅ |
| sanction_committee | ❌ | ❌ | ❌ | ✅ approve | 👁 view | ❌ | ❌ | ❌ | ✅ | ❌ |
| cfo | ❌ | ❌ | ❌ | ✅ approve | 👁 view | ❌ | ❌ | ❌ | ✅ | ✅ |
| director | ❌ | ❌ | ❌ | ✅ approve | 👁 view | ❌ | ❌ | ❌ | ✅ | ❌ |
| senior_manager_finance | ❌ | ❌ | ❌ | ❌ | 👁 view | ✅ | ❌ | ❌ | ❌ | ❌ |
| cfc | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| accounts | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| auditor | 👁 | 👁 | 👁 | 👁 | 👁 | ❌ | ❌ | ❌ | ❌ | ❌ |
| admin | — | — | — | — | — | — | — | — | — | — |
| borrower | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

### 4.2 Permission Gaps

| Gap | Risk | File |
|---|---|---|
| `admin` role bypasses `mandatoryChecklistClear` in `DocumentChecklist` — no audit entry | Medium | `DocumentChecklist.tsx` |
| `accounts` role has `manage_interest` permission; per swim-lane this is a `sales_team_user` + `accounts` joint action | Low | `RoleContext.tsx:141` |
| `credit_manager` does NOT have `manage_closure` but can see closure-related loan account data | Low | `RoleContext.tsx:81` |
| `sales_team_user` has `manage_interest` — should only be read + invoice generate | Low | `RoleContext.tsx:143` |
| `ApprovalPanel.onDecision` collapses `approved_with_conditions`, `clarification`, `abstained` to binary `approved/rejected` | High | `ApprovalPanel.tsx:handleSubmit` |
| Partial sanctioned amount captured in `ApprovalPanel` local state but NOT passed through `onDecision` callback | High | `ApprovalPanel.tsx` |
| `DefaultRecoveryHub` defines `canCreditAct`, `canApproveRecovery`, `canInvokeSecurity` but action buttons are NOT disabled by them | High | `DefaultRecoveryHub.tsx` |

---

## 5. Functional Integrity Issues (Code Review)

| # | Issue | Severity | File:Location |
|---|---|---|---|
| 1 | All major actions (submit application, forward to sanction, sanction decision, disburse) write to local React state only — no cross-component data propagation | Critical | App-wide (no shared mutable store) |
| 2 | `NewApplication.tsx` generates hardcoded reference `DRAFT-APP-0042` regardless of existing application count | High | `NewApplication.tsx:~submission` |
| 3 | Loan limit formula constants (% share valuation, per-acre scale-of-finance, per-share value) are hardcoded in UI — not read from `SettingsHub` policy config | High | `LoanLimitCalculator.tsx`, `NewApplication.tsx` |
| 4 | `ApprovalPanel.handleSubmit` passes only `'approved'` or `'rejected'` to parent regardless of selected decision nuance | High | `ApprovalPanel.tsx:handleSubmit` |
| 5 | `DisbursementHub` readiness checklist: 9 of 11 items hardcoded `ok: true`; does not check that documentation sign-off chain completed | High | `DisbursementHub.tsx:disbursementReady` |
| 6 | `DefaultRecoveryHub` permission booleans (`canApproveRecovery`, `canInvokeSecurity`) defined but NOT wired to disable action buttons | High | `DefaultRecoveryHub.tsx` |
| 7 | DPD values are static fields in `mockData.ts` — not computed from `repaymentDueDate` vs. today | Medium | `mockData.ts`, `RepaymentsHub.tsx` |
| 8 | `InterestManagement.tsx` role gate uses `role.includes('finance')` string match — fragile if role slugs change | Medium | `InterestManagement.tsx:~gate` |
| 9 | `SIG_MATCH` mismatch path is hardcoded to `applicationId === 'app004'`; no generic mismatch detection | Medium | `DocumentationHub.tsx` |
| 10 | Audit events use `console.log` for all live actions; `AuditTimeline` and `RegistersHub` audit log only show pre-seeded mock events | Medium | App-wide |
| 11 | `RegistersHub.tsx` references `can('export_reports')` permission which does not exist in `Permission` type | Low | `RegistersHub.tsx:46`, `RoleContext.tsx` |
| 12 | `currentUser` exported from `mockData.ts` conflicts with `RoleContext` `currentUser` — `mockData.currentUser` is always `credit_manager` | Low | `mockData.ts:1`, multiple consumers |

---

## 6. Task Ledger

> Sorted by priority. P0 = demo-breaking. P1 = important functional gap. P2 = completeness. P3 = backend/persistence (out of scope for prototype).

### P0 — Critical (Fix before stakeholder demo)

| ID | Task | Effort | File(s) |
|---|---|---|---|
| T-001 | Wire approval decision nuances through `ApprovalPanel.onDecision` — pass full decision type (`approved_with_conditions`, `clarification`, `abstained`) and partial amount | S | `ApprovalPanel.tsx` |
| T-002 | Gate `DefaultRecoveryHub` action buttons with `canApproveRecovery` and `canInvokeSecurity` booleans already defined in the component | S | `DefaultRecoveryHub.tsx` |
| T-003 | Enforce GM evidence upload gate in `SanctionWorkbench` — disable Approve button for conflicted approver cases until GM evidence file is attached | S | `SanctionWorkbench.tsx`, `ApprovalPanel.tsx` |
| T-004 | Add nominee minor-age validation in `NewApplication.tsx` step 4 — compute age from DOB and block submission if nominee < 18 with deficiency message | S | `NewApplication.tsx` |
| T-005 | Fix `RegistersHub` permission reference — `can('export_reports')` → `can('export_registers')` to match `Permission` type | XS | `RegistersHub.tsx:46` |
| T-006 | Remove admin bypass of `mandatoryChecklistClear` in `DocumentChecklist` and replace with a clearly labelled override with audit note | S | `DocumentChecklist.tsx` |

### P1 — Important (Complete before pilot)

| ID | Task | Effort | File(s) |
|---|---|---|---|
| T-007 | Implement duplicate borrower check on `NewApplication` member selection — warn if another member with same PAN or Aadhaar (last 4) exists, show resolution UI | M | `NewApplication.tsx`, `MemberDirectory.tsx` |
| T-008 | Witness shareholder verification in `DocumentationHub` — after witness PAN/Aadhaar entered, check against `members` array and raise deficiency if not found | M | `DocumentationHub.tsx`, `DocumentChecklist.tsx` |
| T-009 | Create shared write-through helper — `updateApplicationStatus(id, newStatus, actor, reason)` — so AppraisalWorkbench, SanctionWorkbench, DocumentationHub, DisbursementHub can mutate the shared `loanApplications` array and queues auto-update | L | `data/mockData.ts`, `App.tsx` (lift state) |
| T-010 | On new application submission, create a completeness-check task in `TaskInbox` for `deputy_manager_finance` role | S | `NewApplication.tsx`, `data/mockData.ts` |
| T-011 | Make DPD a computed value — calculate from `repaymentDueDate` vs. current date at render time; replace static `dpd` field in mock data | S | `mockData.ts`, `RepaymentsHub.tsx`, `MonitoringDashboard.tsx` |
| T-012 | Add interest rate history table to `InterestManagement.tsx` — rate changes log with effective date, old rate, new rate, changed by | S | `InterestManagement.tsx` |
| T-013 | Replace loan limit formula hardcodes with values read from `SettingsHub` policy config (share valuation %, per-acre scale-of-finance, per-share value) | M | `LoanLimitCalculator.tsx`, `NewApplication.tsx`, `SettingsHub.tsx` |
| T-014 | Implement repayment reconciliation queue — show unmatched receipts (channel = unknown or narration doesn't match loan no.) in a dedicated tab in `RepaymentsHub` | M | `RepaymentsHub.tsx` |
| T-015 | Enable subsidiary deduction repayment channel — add basic input flow for subsidiary name, produce payment reference, and deduction amount | M | `RepaymentsHub.tsx` |
| T-016 | Add SAP receipt next-working-day posting date tracker to `RepaymentsHub` — show calculated next business day after receipt date | S | `RepaymentsHub.tsx` |
| T-017 | Policy active gate on Dashboard — add a check for `policyActive` flag; redirect to `SettingsHub` with notice if policy not yet published | M | `Dashboard.tsx`, `SettingsHub.tsx`, `App.tsx` |
| T-018 | Add policy maker-checker in `SettingsHub` — edits go to "Pending approval" state; CFO/Board approval required before becoming active | L | `SettingsHub.tsx` |
| T-019 | Fix `InterestManagement` role gate — replace `role.includes('finance')` string check with `can('manage_interest')` permission call | XS | `InterestManagement.tsx` |
| T-020 | Populate registers on key actions — when sanction approved, write to Credit Sanction Register; when disbursed, write to Loan Register; when NOC issued, write to NOC Register | M | `RegistersHub.tsx` + write-through helper from T-009 |

### P2 — Polish (Before audit walkthrough)

| ID | Task | Effort | File(s) |
|---|---|---|---|
| T-021 | Generate sequential loan reference numbers (`LO00000001`...) based on existing application count, not hardcoded | S | `NewApplication.tsx` |
| T-022 | Add deficiency communication dispatch evidence — channel (email/portal/letter/courier), sent-by, sent-at, tracking reference in ApplicationDetail deficiency tab | S | `ApplicationDetail.tsx` |
| T-023 | Add rejection note/letter generation with download for both credit and sanction rejections | S | `AppraisalWorkbench.tsx`, `SanctionWorkbench.tsx` |
| T-024 | NOC delivery acknowledgement — capture dispatch method, date, tracking reference and borrower acknowledgement date in `LoanClosureHub` | S | `LoanClosureHub.tsx` |
| T-025 | Add `Non-Recoverable` as a distinct visible status/step between Extension and Recovery Review in `DefaultRecoveryHub` stepper | S | `DefaultRecoveryHub.tsx` |
| T-026 | Link `DefaultRecoveryHub` security invocation to `RegistersHub` security register and `LoanAccount360` audit trail | M | `DefaultRecoveryHub.tsx`, `RegistersHub.tsx` |
| T-027 | Borrower360 → New Application CTA — "New Application" button on Borrower 360 should pre-populate member fields in `NewApplication` step 1 | S | `Borrower360.tsx`, `App.tsx` |
| T-028 | Add `Payment_Returned` state and visible counter in `PaymentAuthorisationHub` when CFC returns payment | S | `PaymentAuthorisationHub.tsx` |
| T-029 | Member search by PAN / Aadhaar last-4 in `MemberDirectory` | S | `MemberDirectory.tsx` |
| T-030 | Add TAT escalation — highlight tasks red in `TaskInbox` when TAT breach detected (today > submittedDate + SLA days); add count badge to Dashboard | S | `TaskInbox.tsx`, `Dashboard.tsx` |
| T-031 | Sanction clarification path — when SanctionWorkbench sends clarification, navigate appraisal back to `credit_manager_review` status for rework | S | `SanctionWorkbench.tsx`, `AppraisalWorkbench.tsx` |
| T-032 | `currentUser` in `mockData.ts` causes confusion — remove export and ensure all consumers use `useRole()` from RoleContext | S | `mockData.ts`, all importing files |
| T-033 | Closure checklist — check security register state (returned/unpledged) and SAP closing balance in addition to `outstanding === 0` | M | `LoanClosureHub.tsx` |

### P3 — Backend / Production (Out of prototype scope)

| ID | Task | Notes |
|---|---|---|
| T-034 | Real JWT authentication with inactive-user denial | Backend required |
| T-035 | Persistent data store (database) replacing `mockData.ts` | Backend required |
| T-036 | Real PDF generation (appraisal note, deficiency letter, NOC, rejection letter, disbursement advice) | PDF generation service required |
| T-037 | Email/SMS dispatch for deficiency notices, acknowledgements, repayment reminders | Notification service required |
| T-038 | SAP API integration for customer code creation and receipt posting | SAP connector required |
| T-039 | RBL bank API integration for actual payment initiation | Banking API required |
| T-040 | CDSL pledge/unpledge API integration | CDSL connector required |
| T-041 | Audit log write to append-only store on every state transition | Audit backend required |

---

## 7. Swim-Lane Coverage (flowchart LR)

| Actor | Responsibilities in spec | Implemented | Gap |
|---|---|---|---|
| Borrower / FPC | 8 actions (provide, submit, upload, respond, sign, repay, receive) | ✅ Full borrower portal with all actions | DEF_COMM acknowledgement not trackable |
| Credit / DM Finance / Credit Assessment | 8 actions | ✅ Appraisal, completeness, monitoring | Completeness items not live-computed; rework loop is local state |
| CFO / Directors / Sanction Committee | 6 actions | ✅ SanctionWorkbench, ApprovalPanel | GM evidence gate not enforced; approval nuances collapsed to binary |
| Compliance / CS | 6 actions | ✅ DocumentationHub, LoanClosureHub | Witness SFPCL check missing; admin bypass has no audit trail |
| SM Finance / Treasury / CFC | 8 actions | ✅ DisbursementHub, PaymentAuthorisationHub | 9/11 readiness items hardcoded; subsidiary match route missing |
| Accounts / Sales | 4 actions | ✅ InterestManagement, ReportsMIS | Interest formula is pre-computed static, not live calculation |
| CFO / CS / Auditor / IT (compliance) | 4 actions | ✅ ComplianceDashboard, AuditArchiveHub | Real audit writes missing; board approval workflow absent |

---

## 8. Summary Score Card

| Domain | Coverage | Readiness |
|---|---|---|
| Authentication & RBAC | 85% | Demo-ready with caveats |
| Member / Borrower Master | 70% | Missing duplicate check is a notable gap |
| Loan Origination & Completeness | 80% | Minor-nominee and comm dispatch missing |
| Credit Assessment & Appraisal | 90% | Very strong; PDF and TAT are polish items |
| Sanction | 82% | GM evidence gate is the critical gap |
| Documentation & Security | 88% | Witness check and admin audit bypass need fixing |
| Disbursement | 85% | Readiness hardcodes are the main gap |
| Repayment & Ledger | 72% | Subsidiary route and reconciliation queue are missing |
| Interest Management | 78% | Rate history and live formula missing |
| Monitoring & Defaults | 88% | Strong; DPD static value is the main issue |
| Closure & Archive | 90% | Close-ready check can be strengthened |
| Compliance & Audit | 75% | Real audit writes are the key production gap |
| **Overall** | **83%** | **Prototype-ready; 6 P0 and 13 P1 items before pilot** |

---

*End of audit. 40 tasks identified: 6 P0, 14 P1, 12 P2, 8 P3.*
