# content-spec.md
# SFPCL Member Credit Administration & Settlement — Detailed Content Specification

## 1. Document Control

| Item | Detail |
|---|---|
| Document name | `content-spec.md` |
| Product / system | SFPCL Member Credit Administration & Loan Management System |
| Client | Sahyadri Farmers Producer Company Limited |
| Process basis | Member credit administration, loan sanction, documentation, disbursement, repayment, monitoring, settlement and compliance |
| Source basis | Detailed SOP, WhatsLoan visual SOP summary, client brief, user flows, functional specification, information architecture and screen specification prepared in the current analysis |
| Intended audience | Product managers, UX writers, designers, business analysts, engineering team, QA team, compliance team, implementation team and client stakeholders |
| Document purpose | Define all product content, naming, labels, messages, helper text, notifications, document copy, report labels, workflow copy and governance rules required to implement the system consistently |
| Version | 1.0 |
| Status | Draft for implementation alignment |

---

## 2. Purpose of This Content Specification

This document defines the content layer for the SFPCL Member Credit Administration & Settlement system. It translates the SOP-driven process into a controlled content system covering:

- Product terminology and vocabulary.
- Menu and navigation labels.
- Screen titles, section headings and tab names.
- Field labels and field-level help text.
- Status badge labels.
- Workflow action labels.
- Validation messages and blocker messages.
- Empty, loading and success states.
- Notifications, reminders, emails and SMS messages.
- Generated document and template content.
- Report and export names.
- Audit trail wording.
- Compliance disclaimers and borrower-facing explanations.
- Content governance and change-control expectations.

The goal is to make the product clear, compliant, auditable and easy to operate across Credit Assessment, Compliance, Treasury, Accounts, Sanction Committee, CFO, Directors, CFC, auditors and borrowers.

---

## 3. Content Strategy Summary

The system content must support a highly controlled loan lifecycle. The core content design principles are:

1. **Lifecycle clarity** — every loan must visibly move through request, assessment, sanction, documentation, disbursement, repayment, monitoring, default handling and closure.
2. **Control-first language** — content should make approval gates, documentation blockers and compliance requirements explicit.
3. **Role-specific action clarity** — each user must know what task is pending, why it is pending, who owns it and what happens after action.
4. **Borrower-friendly explanation** — borrower-facing content should use simple language and explain terms such as nominee, KYC, crop plan, 7/12 extract, repayment deduction, interest, security and closure.
5. **Audit-ready wording** — system-generated content should produce a clear evidence trail suitable for internal audit, statutory audit and Board review.
6. **No hidden decisions** — approvals, rejections, exceptions, delays and security invocation decisions must always require reasons.
7. **Consistent vocabulary** — the same object must not be called by multiple names in the UI unless the SOP explicitly uses interchangeable terms.
8. **Documented ambiguity** — unresolved SOP contradictions must be surfaced as configuration / policy confirmation items, not silently hardcoded.

---

## 4. Source Process Summary to Anchor Content

### 4.1 Business Context

SFPCL is a farmer-owned Producer Company serving individual farmer shareholders and Farmer Producer Companies. It provides structured financial assistance to eligible members for agriculture and crop-production-related activities.

The system must reflect the SOP’s intended controls:

- Lending only to eligible members.
- Loan application signed by applicant and nominee.
- KYC and document verification before appraisal.
- Appraisal note preparation within 2 days from receipt of application.
- Sanction Committee approval according to the authority matrix.
- Documentation, stamping and security completion before disbursement.
- SAP customer code creation and bank transfer through authorised finance workflow.
- Repayment either directly or through subsidiary deduction from produce payments.
- Monitoring through DPD buckets and quarterly CFO MIS.
- Formal closure with NOC and return of security documents.

### 4.2 Six SOP Stages

Use these stage names consistently in the product:

| Stage | Display name | Short label |
|---:|---|---|
| 1 | Initial Loan Request | Request |
| 2 | Credit Assessment | Assessment |
| 3 | Credit Scrutiny and Approval | Sanction |
| 4 | Documentation and Stamping | Documentation |
| 5 | Loan Disbursement | Disbursement |
| 6 | Monitoring and Repayment | Monitoring |

### 4.3 Hard Control Gates to Communicate

The content must clearly communicate these blockers:

- Application cannot proceed if borrower is not a member.
- Application cannot proceed if required applicant and nominee details are incomplete.
- Appraisal cannot be submitted unless eligibility checks are recorded.
- Sanction cannot be completed unless approval authority is satisfied.
- Documentation cannot be marked complete unless mandatory documents are verified.
- Disbursement cannot be initiated before final approvals, SAP readiness and bank verification.
- Closure cannot be completed until full repayment is confirmed and NOC / security return is recorded.
- SH-4, blank-dated cheque or CDSL pledge invocation must not occur without required approval.

---

## 5. Voice, Tone and Content Style

### 5.1 Product Voice

The voice should be:

- Clear.
- Formal but not legalistic.
- Operationally precise.
- Compliance-aware.
- Farmer-friendly where borrower-facing.
- Direct and action-oriented for internal users.

### 5.2 Tone by Context

| Context | Tone | Example |
|---|---|---|
| Borrower guidance | Simple, reassuring, explanatory | “Please upload your PAN card and Aadhaar card to complete KYC.” |
| Internal workflow | Direct and task-oriented | “Review loan limit and submit appraisal note.” |
| Approval screen | Formal and accountable | “Record approval decision and reason before submitting.” |
| Compliance blocker | Firm and specific | “Disbursement is blocked because the Loan Agreement is not stamped and notarised.” |
| Rejection | Clear, respectful and reason-based | “The application is rejected because active member eligibility is not met.” |
| Default handling | Neutral, documented and non-coercive | “Record reason for non-payment and classify whether it is intentional or non-intentional.” |
| Audit trail | Factual and timestamped | “Checklist verified by Company Secretary on {date_time}.” |

### 5.3 Writing Rules

Use:

- Sentence case for page titles, labels and buttons.
- Title case only for formal document names, registers and legal forms.
- “Borrower” for loan lifecycle records.
- “Member” when referring to eligibility and Producer Company membership.
- “Applicant” before loan sanction or disbursement.
- “Loan account” after disbursement.
- “Nominee” for the person signing application and related documentation.
- “Witness” only for document execution witness.

Avoid:

- Ambiguous verbs like “process” without object.
- Vague statuses such as “Done” or “Pending” without owner.
- Informal wording such as “OK”, “Oops”, “Bad file” or “Failed badly”.
- Making legal assumptions in borrower-facing messages.
- Using “customer” for borrower-facing content unless referring specifically to SAP Customer Code.

### 5.4 Mandatory Reason Capture

Any of the following actions must include a required reason field:

- Application deficiency.
- Credit Assessment rejection.
- Sanction Committee rejection.
- Approval with exception.
- Loan amount exceeding calculated permissible limit.
- Director / relative special case routing.
- Documentation waiver or delay.
- Disbursement hold.
- Tenure extension.
- Non-payment classification.
- Security invocation recommendation.
- Closure delay.
- Any manual override.

---

## 6. Controlled Vocabulary

### 6.1 Core Entity Names

| Preferred term | Use for | Avoid |
|---|---|---|
| Member | Person or Producer Institution that is a member of SFPCL | Customer, party, client |
| Borrower | Member who has applied for or availed a loan | Farmer everywhere, loanee |
| Applicant | Borrower before sanction / disbursement | Lead, prospect |
| Individual member | Farmer shareholder | Retail borrower |
| Producer Institution | FPC or institutional member | Organisation customer |
| Nominee | Person named by applicant and required for signatures | Co-applicant, beneficiary unless legally confirmed |
| Witness | Existing SFPCL shareholder witnessing execution | Guarantor unless explicitly required |
| Loan Application | Application record before disbursement | Case, request ticket |
| Loan Account | Active account after disbursement | Application after disbursement |
| Loan Appraisal Note | Credit Assessment recommendation document | Credit memo, CAM unless configured |
| Credit Sanction Register | Register of sanction decisions | Approval log, sanction tracker |
| Exception Register | Register of deviations and approvals | Issue list |
| Document Checklist | Index and control checklist for loan documents | Document list only |
| Security Instrument | SH-4, blank-dated cheque, CDSL pledge and related security | Collateral only |
| Disbursement Advice | Communication confirming loan disbursement | Payment receipt |
| NOC | No Objection Certificate after full repayment | Closure certificate unless approved |

### 6.2 Role Names

Use role names exactly as below:

| System display role | SOP role / description |
|---|---|
| Credit Manager | Credit Assessment Team lead / reviewer |
| Deputy Manager – Finance | Application completeness and appraisal preparation |
| Company Secretary | Compliance owner, document verification, stamping and legal documentation |
| Compliance Team Member | Prepares documentation set and coordinates checklist |
| Senior Manager – Finance | SAP customer code coordination and disbursement initiation |
| Chief Financial Controller | Final bank transfer approval / authorised signatory |
| Chief Financial Officer | Sanction Committee member and policy / exception approver |
| Director | Executive Director in Sanction Committee |
| Sanction Committee Member | CFO and designated Directors according to approval matrix |
| Accounts Team | Repayment, accrual and SAP financial entries |
| IT Head | Access control and data protection controls |
| Internal Auditor | Audit review user |
| Borrower / Member | Applicant / farmer / FPC using the loan facility |

### 6.3 Legal and Compliance Terms

| Term | Display explanation |
|---|---|
| KYC | Identity and address verification using PAN, Aadhaar and other approved documents. |
| CKYC | Central Know Your Customer record and consent, where applicable. |
| OVD | Officially Valid Document used for identity or address verification. |
| 7/12 extract | Land record document used to verify agricultural land details. |
| Crop plan | Crop details and planned cultivation information used for loan assessment. |
| Scale of Finance | Company-approved per-acre cost of cultivation used to calculate land-based loan eligibility. |
| SH-4 | Share Transfer Form used as security where shares are held physically. |
| CDSL pledge | Online pledge of demat shares through the depository system. |
| Blank-dated cheque | Cheque held as security and used only as per approved recovery process. |
| PoA | Power of Attorney authorising the Company Secretary to act in specified default-related situations. |
| DPD | Days Past Due / overdue classification used for monitoring. |
| NOC | No Objection Certificate issued after complete repayment and closure. |

---

## 7. Formatting Standards

### 7.1 Currency

Use Indian rupee symbol and comma grouping:

- `₹5,00,000`
- `₹20,000 per acre`
- `₹200 per share`

For calculated values, show formula and result:

```text
Shareholding-based limit = 1,000 shares × ₹200 = ₹2,00,000
```

### 7.2 Dates

Internal UI format:

```text
DD MMM YYYY
```

Example:

```text
07 Aug 2025
```

Audit trail format:

```text
DD MMM YYYY, hh:mm AM/PM
```

Example:

```text
07 Aug 2025, 04:35 PM
```

### 7.3 IDs and Reference Numbers

Application reference number format:

```text
LO00000001
```

Display as:

```text
Application No.: LO00000001
```

Do not alter leading zeros.

### 7.4 Percentages

Show percentage and policy basis:

```text
30% of valuation per share
10% of valuation per share — policy confirmation required
```

### 7.5 Names

Use full legal name in formal documents. Use shorter display name only in dashboard cards.

### 7.6 File Names

Generated documents should follow a predictable naming pattern:

```text
{application_no}_{document_type}_{borrower_name}_{YYYYMMDD}.pdf
```

Example:

```text
LO00000001_TermSheet_RameshPatil_20250807.pdf
```

---

## 8. Global Navigation Content

### 8.1 Primary Navigation Labels

Use these navigation labels:

1. Dashboard
2. Tasks
3. Applications
4. Members & Borrowers
5. Loan Accounts
6. Approvals
7. Documentation
8. SAP & Disbursement
9. Repayments
10. Monitoring & Defaults
11. Compliance
12. Reports
13. Admin Settings
14. Audit Trail
15. Help & Templates

### 8.2 Secondary Navigation Labels

| Primary nav | Secondary labels |
|---|---|
| Applications | New Application, Application Queue, Loan Request Register, Rejected Applications |
| Members & Borrowers | Member Directory, Borrower 360, Active Member Review, KYC Records, Shareholding Records |
| Loan Accounts | Active Loans, Closed Loans, Loan Ledger, Security Records |
| Approvals | Pending Sanction, Credit Sanction Register, Exception Register, General Meeting Approvals |
| Documentation | Document Workbench, Checklist Queue, Stamping Queue, PoA, Term Sheet, Loan Agreement, SH-4 / Pledge, Bank Verification |
| SAP & Disbursement | SAP Customer Code Requests, Disbursement Queue, Bank Transfer Approvals, Disbursement Advice |
| Repayments | Direct Repayments, Subsidiary Deductions, Interest Invoices, Accruals, Reconciliation |
| Monitoring & Defaults | DPD Dashboard, Reminder Queue, Extension Notes, Non-Payment Notes, Recovery Approvals |
| Compliance | Section 186 Tracker, NBFC Principal Business Test, KYC / Re-KYC, Stamp Duty, Record Retention, Grievances |
| Reports | CFO MIS, Board Pack, Loan Register Export, Audit Exports, Exception Reports |
| Admin Settings | Policy Configuration, Loan Limit Rules, Interest Rates, User Roles, Templates, Notification Settings |

---

## 9. Global Status Content Taxonomy

### 9.1 Application Status Labels

| Status | Meaning | Recommended badge text |
|---|---|---|
| Draft | Application started but not submitted | Draft |
| Submitted | Applicant submitted application | Submitted |
| Completeness Check | Deputy Manager – Finance reviewing completeness | Completeness Check |
| Deficiency Raised | Missing / incorrect information identified | Deficiency Raised |
| Ready for Appraisal | Complete application ready for credit assessment | Ready for Appraisal |
| Appraisal In Progress | Loan Appraisal Note being prepared | Appraisal In Progress |
| Appraisal Submitted | Appraisal submitted to Credit Manager / Sanction Committee | Appraisal Submitted |
| Rejected by Credit | Credit Assessment Team rejected application | Rejected by Credit |
| Pending Sanction | Awaiting Sanction Committee decision | Pending Sanction |
| Sanctioned | Loan approved | Sanctioned |
| Rejected by Sanction Committee | Sanction Committee rejected application | Rejected by Sanction Committee |
| Documentation In Progress | Approved case in documentation stage | Documentation In Progress |
| Documentation Complete | All required documents verified | Documentation Complete |
| Ready for Disbursement | Documentation, SAP and approval controls satisfied | Ready for Disbursement |
| Disbursement Initiated | Payment initiated by Senior Manager – Finance | Disbursement Initiated |
| Disbursed | Bank transfer complete | Disbursed |
| Active | Loan account active after disbursement | Active |
| Closed | Loan fully repaid and closure completed | Closed |
| Cancelled | Application cancelled before disbursement | Cancelled |

### 9.2 Documentation Status Labels

| Status | Meaning |
|---|---|
| Not Started | Documentation not yet initiated |
| Pending Borrower Documents | Awaiting documents from borrower |
| Pending Witness Documents | Awaiting witness PAN / Aadhaar or signature |
| Pending Drafting | Compliance Team has to prepare document |
| Pending Signature | Document generated but not signed |
| Pending Stamping | Stamp paper / e-stamp incomplete |
| Pending Notarisation | Notarisation incomplete |
| Under CS Review | Company Secretary reviewing file |
| CS Verified | Company Secretary has verified documents |
| Credit Verified | Credit Manager has confirmed limits and loan details |
| Sanction Verified | Sanction Committee has signed checklist |
| Finance Verified | Senior Manager – Finance has verified before disbursement |
| Complete | Documentation checklist completed |
| Deficient | One or more required documents failed validation |

### 9.3 Security Status Labels

| Security | Status values |
|---|---|
| SH-4 | Not Required, Pending, Received, Verified, Returned, Invoked |
| Blank-dated cheque | Pending, Received, Verified, Returned, Presented, Cancelled |
| CDSL pledge | Not Required, Pledge Pending, PRF Submitted, PSN Generated, Accepted by Pledgee DP, Pledged, Invocation Requested, Invoked, Unpledge Requested, Unpledged |
| PoA | Pending Drafting, Pending Signature, Pending Stamping, Pending Notarisation, Executed, Cancelled |

### 9.4 Repayment and Default Status Labels

| Status | Meaning |
|---|---|
| Regular | No scheduled repayment overdue |
| Principal Due | Scheduled principal repayment due |
| Grace Period | Three-month extension after missed scheduled repayment |
| Under Non-Payment Review | Credit Assessment Team reviewing reason for non-payment |
| Non-Intentional Extension | One-year extension granted for non-intentional non-payment |
| Intentional Default Suspected | Case requires decision and evidence review |
| Non-Recoverable Review | Case under scrutiny after extension failure |
| Recovery Approval Pending | Awaiting Sanction Committee decision |
| Recovery Action Approved | Recovery action approved |
| Security Invoked | Security has been invoked |
| Fully Repaid | Principal, interest and charges fully paid |
| Closure Pending | Full repayment received; NOC/security return pending |
| Closed | Loan closure completed |

### 9.5 Compliance Status Labels

| Status | Meaning |
|---|---|
| Compliant | Control requirement met |
| Due Soon | Action will become due within configured period |
| Overdue | Required compliance action not completed by due date |
| Exception Approved | Deviation approved by authorised person |
| Exception Pending | Deviation awaits approval |
| Not Applicable | Requirement does not apply to this record |
| Policy Confirmation Required | SOP inconsistency or missing policy value must be resolved |

---

## 10. Global Buttons and Action Labels

### 10.1 Primary Action Buttons

| Action | Button label |
|---|---|
| Start new application | New Loan Application |
| Save incomplete work | Save Draft |
| Submit application | Submit Application |
| Raise missing document issue | Raise Deficiency |
| Mark application complete | Mark Complete |
| Generate reference number | Generate Application Number |
| Prepare appraisal note | Prepare Appraisal Note |
| Submit to Credit Manager | Submit for Credit Review |
| Submit to Sanction Committee | Submit for Sanction |
| Approve | Approve |
| Reject | Reject |
| Approve with exception | Approve with Exception |
| Send back for correction | Send Back |
| Generate document | Generate Document |
| Upload signed document | Upload Signed Copy |
| Verify document | Verify Document |
| Mark checklist complete | Complete Checklist |
| Create SAP request | Request SAP Customer Code |
| Confirm SAP code | Confirm SAP Code |
| Initiate payment | Initiate Disbursement |
| Approve bank transfer | Approve Bank Transfer |
| Send disbursement advice | Send Disbursement Advice |
| Record repayment | Record Repayment |
| Generate interest invoice | Generate Interest Invoice |
| Post accrual | Post Accrual Entry |
| Send reminder | Send Reminder |
| Create extension note | Create Extension Note |
| Create non-payment note | Create Non-Payment Note |
| Approve recovery action | Approve Recovery Action |
| Generate NOC | Generate NOC |
| Close loan | Close Loan |

### 10.2 Destructive or High-Risk Actions

Use confirmation modals for these actions:

| Action | Button label | Confirmation title |
|---|---|---|
| Reject application | Reject Application | Confirm Rejection |
| Cancel application | Cancel Application | Cancel Loan Application? |
| Approve exception | Approve Exception | Confirm Exception Approval |
| Initiate security invocation | Initiate Security Invocation | Confirm Security Invocation Request |
| Present blank-dated cheque | Record Cheque Presentation | Confirm Cheque Recovery Action |
| Mark non-recoverable | Mark for Non-Recoverable Review | Confirm Non-Recoverable Review |
| Delete draft document | Delete Draft Document | Delete Document Draft? |

---

## 11. Global Empty States

### 11.1 Dashboard Empty State

**Title:** No tasks assigned right now  
**Body:** You do not have any pending tasks in the loan workflow. New items will appear here when applications, approvals, documents or repayments need your action.

### 11.2 Application Queue Empty State

**Title:** No loan applications found  
**Body:** There are no applications matching the selected filters. Try changing the status, date range or borrower search.

### 11.3 Member Search Empty State

**Title:** No member matched your search  
**Body:** Check the member name, folio number, PAN or Aadhaar number and try again. A loan application can proceed only for an eligible member.

### 11.4 Documents Empty State

**Title:** No documents uploaded yet  
**Body:** Upload the required borrower, nominee, witness and loan documents to complete the checklist.

### 11.5 Approvals Empty State

**Title:** No approval items pending  
**Body:** Sanction and exception requests assigned to you will appear here.

### 11.6 Repayment Empty State

**Title:** No repayment entries recorded  
**Body:** Direct RTGS / NEFT payments and subsidiary deductions will appear here after posting.

### 11.7 Audit Trail Empty State

**Title:** No activity recorded yet  
**Body:** System events, user actions and status changes will appear here as the record moves through the workflow.

---

## 12. Global Loading and Success Messages

| Event | Message |
|---|---|
| Saving draft | Saving draft... |
| Draft saved | Draft saved successfully. |
| Submitting application | Submitting loan application... |
| Application submitted | Loan application submitted successfully. |
| Generating application number | Generating application number... |
| Application number generated | Application number {application_no} has been generated. |
| Uploading document | Uploading document... |
| Document uploaded | Document uploaded successfully. |
| Verifying document | Verifying document... |
| Document verified | Document verified successfully. |
| Submitting approval | Submitting decision... |
| Approval recorded | Approval decision recorded successfully. |
| Creating SAP request | Creating SAP customer code request... |
| SAP request created | SAP customer code request has been created. |
| Initiating disbursement | Initiating disbursement... |
| Disbursement initiated | Disbursement has been initiated and sent for final approval. |
| Posting repayment | Posting repayment... |
| Repayment posted | Repayment has been recorded successfully. |
| Closing loan | Closing loan account... |
| Loan closed | Loan account has been closed successfully. |

---

## 13. Validation Message Library

### 13.1 Required Field Messages

Use format:

```text
{Field label} is required.
```

Examples:

- Borrower name is required.
- Folio number is required.
- Nominee Aadhaar number is required.
- Required loan amount is required.
- Purpose of loan is required.
- Crop plan is required.

### 13.2 Format Validation Messages

| Field | Message |
|---|---|
| PAN | Enter a valid PAN in the format ABCDE1234F. |
| Aadhaar | Enter a valid 12-digit Aadhaar number. |
| Email | Enter a valid email address. |
| Mobile number | Enter a valid 10-digit mobile number. |
| IFSC | Enter a valid IFSC code. |
| Bank account number | Enter a valid bank account number. |
| Application number | Application number must follow the configured sequence format. |
| Amount | Enter an amount greater than ₹0. |
| Percentage | Enter a percentage between 0 and 100. |
| Date | Enter a valid date in DD MMM YYYY format. |

### 13.3 Loan Control Messages

| Scenario | Message |
|---|---|
| Non-member borrower | This applicant is not an eligible SFPCL member. Loan application cannot proceed. |
| Inactive member | This member is not marked as active. Record active member evidence or raise an exception before proceeding. |
| Existing default | This borrower has an existing default with SFPCL, subsidiary or associate company. Application cannot proceed without authorised review. |
| Missing nominee | Nominee details are required before application submission. |
| Nominee minor | Nominee cannot be a minor. Enter a nominee who is 18 years or older. |
| Missing crop purpose | Loan purpose must be related to crop production or agricultural activity. |
| Loan amount exceeds eligibility | Requested amount exceeds the calculated eligible amount. Submit as an exception or revise the requested amount. |
| Undefined loan limit policy | Loan limit percentage is not confirmed in policy configuration. Confirm whether 30%, 10% or ₹200 per share applies before sanction. |
| Missing appraisal note | Loan Appraisal Note is required before submission to Sanction Committee. |
| Missing sanction approval | Sanction Committee approval is required before documentation and disbursement. |
| Missing documents | Mandatory documents are incomplete. Complete the checklist before proceeding. |
| Missing stamping | Stamping is incomplete. Disbursement is blocked until stamping is completed. |
| Missing notarisation | Notarisation is incomplete for one or more required documents. |
| Missing SAP code | SAP Customer Code is required before disbursement. |
| Missing bank verification | Bank account verification is incomplete. Disbursement cannot be initiated. |
| Missing CFC approval | Chief Financial Controller approval is required to complete bank transfer. |
| Closure blocked | Loan cannot be closed until full repayment, NOC and security return are recorded. |

### 13.4 Approval Matrix Messages

| Scenario | Message |
|---|---|
| Up to ₹5 lakh | This loan requires approval from CFO and one Director. |
| Above ₹5 lakh | This loan requires approval from CFO and two Directors. |
| Exceeds permissible limit | This loan exceeds the permissible limit and requires joint approval from CFO and two Directors with an Exception Register entry. |
| Director / relative borrower | This is a special case. The applicant must be excluded from approval and member approval in a general meeting must be recorded. |
| Missing reason | Reason is required for this decision. |
| Approver conflict | This approver is marked as applicant, relative or conflicted party and cannot approve this case. |

### 13.5 Document Validation Messages

| Scenario | Message |
|---|---|
| PoA missing | Power of Attorney is required before disbursement. |
| PoA not stamped | Power of Attorney must be executed on ₹500 stamp paper. |
| PoA not notarised | Power of Attorney must be notarised. |
| Tri-party missing | Declaration / Tri-party Agreement is required for subsidiary deduction repayment. |
| SH-4 required | SH-4 is required because shares are held physically. |
| CDSL pledge required | CDSL pledge is required because shares are held in demat form. |
| Term Sheet missing | Term Sheet is required before disbursement. |
| Loan Agreement missing | Loan Agreement is required before disbursement. |
| Loan Agreement not stamped | Loan Agreement must be executed on ₹500 stamp paper. |
| Witness missing | Witness details and signature are required. |
| Witness not shareholder | Witness must be an existing SFPCL shareholder. |
| Blank-dated cheque missing | Blank-dated cheque is required as security. |
| Cancelled cheque missing | Cancelled cheque is required for bank verification and disbursement. |
| Signature mismatch | Signature mismatch detected. Upload Bank Verification Letter or borrower declaration on non-judicial stamp paper. |

---

## 14. Screen-Level Content Specification

This section defines the required content elements for the screens identified in the current screen specification.

---

## S00 — Login / Access Landing

### Page Title

`SFPCL Member Credit Administration`

### Subtitle

`Secure access for loan application, sanction, documentation, disbursement and monitoring workflows.`

### Field Labels

- Email / User ID
- Password
- One-time password

### Buttons

- Sign In
- Verify OTP
- Forgot Password

### Helper Text

`Access is restricted to authorised users. All actions are logged for audit and compliance.`

### Error Messages

- Enter your User ID.
- Enter your password.
- Invalid User ID or password.
- Your session has expired. Sign in again to continue.
- You do not have access to this module. Contact the system administrator.

---

## S01 — Role-Based Dashboard

### Page Title

`Dashboard`

### Intro Text

`Track pending loan applications, approvals, documentation, disbursements, repayments, defaults and compliance actions assigned to your role.`

### Common Dashboard Cards

| Card title | Description |
|---|---|
| Pending Applications | Applications awaiting completeness check or appraisal. |
| Pending Sanctions | Applications awaiting Sanction Committee decision. |
| Documentation Pending | Sanctioned cases with incomplete documents or checklist items. |
| Ready for Disbursement | Cases ready for SAP and payment processing. |
| Active Loans | Disbursed loans currently under monitoring. |
| Repayments Due | Loan accounts with upcoming or overdue repayments. |
| Exceptions Pending | Policy or process deviations requiring approval. |
| Compliance Due | KYC, Section 186, NBFC, stamp duty, retention or grievance actions due. |

### Role-Specific Card Copy

#### Credit Manager

- Applications to review
- Appraisal notes due within 2 days
- Rejection notes pending communication
- DPD reminders due
- Extension notes pending

#### Company Secretary

- Documents awaiting CS review
- Stamping pending
- Notarisation pending
- SH-4 / PoA custody actions
- Grievance responses due

#### Sanction Committee Member

- Sanction requests pending
- Exception approvals pending
- Special case approvals pending
- Recovery approvals pending

#### Senior Manager – Finance

- SAP code requests pending
- Ready for final disbursement verification
- Bank payment initiation pending
- Disbursement advice pending

#### Chief Financial Controller

- Bank transfers awaiting approval
- Disbursement exceptions
- Payment failures

#### CFO

- High-value approvals
- Exceptions over permissible limits
- Quarterly DPD MIS
- Section 186 tracker
- NBFC principal business test tracker

### Empty State

`No items require your action right now.`

---

## S02 — Global Search Results

### Page Title

`Search Results`

### Search Placeholder

`Search by application number, borrower name, folio number, PAN, Aadhaar, SAP code or loan account number`

### Result Group Labels

- Applications
- Members & Borrowers
- Loan Accounts
- Documents
- Approvals
- Repayments
- Compliance Records

### No Results Message

`No records found. Check the search term or try another identifier.`

---

## S03 — Task Inbox

### Page Title

`Task Inbox`

### Intro Text

`View and complete tasks assigned to you across the loan lifecycle.`

### Column Labels

- Task ID
- Task Type
- Application No.
- Borrower
- Current Stage
- Priority
- Due Date
- Assigned By
- Assigned On
- Status
- Action

### Task Type Labels

- Completeness Check
- Appraisal Preparation
- Credit Review
- Sanction Decision
- Exception Approval
- Document Preparation
- CS Verification
- SAP Code Creation
- Disbursement Initiation
- Bank Transfer Approval
- Repayment Posting
- Interest Invoice
- DPD Review
- Extension Note
- Recovery Approval
- Loan Closure

### Empty State

`No tasks assigned. New tasks will appear here when a workflow step requires your action.`

---

## S04 — Notifications and Alerts Center

### Page Title

`Notifications`

### Tabs

- All
- Action Required
- Approvals
- Documents
- Repayments
- Defaults
- Compliance
- System

### Notification Fields

- Notification type
- Application No.
- Borrower
- Message
- Date and time
- Priority
- Read status
- Related task

### Bulk Actions

- Mark as Read
- Mark as Unread
- Open Related Record

---

## S05 — Member Directory

### Page Title

`Member Directory`

### Intro Text

`Search and verify SFPCL members before creating a loan application.`

### Search Placeholder

`Search by member name, folio number, PAN, Aadhaar or FPC name`

### Column Labels

- Member Name
- Member Type
- Folio Number
- Shareholding
- Active Status
- PAN
- Aadhaar
- Produce Supply Status
- Existing Loan Status
- Default Status
- Actions

### Active Status Labels

- Active
- Inactive
- New / Recent Member Relaxation
- Status Review Required

### Empty State

`No members found. A loan application can be created only for a valid SFPCL member.`

---

## S06 — Member Profile

### Page Title Pattern

`Member Profile: {member_name}`

### Tabs

- Overview
- Shareholding
- Produce Supply History
- Services Availed
- KYC
- Land & Crop Evidence
- Loans
- Documents
- Audit Trail

### Overview Section Labels

- Member name
- Member type
- Folio number
- Date of membership
- Active member status
- PAN
- Aadhaar
- Mobile number
- Email address
- Address
- Associated Producer Institution
- Subsidiary relationship

### Help Text

`Active member status is determined using the Articles of Association criteria for services availed and produce supplied.`

### Action Labels

- Start Loan Application
- Update KYC
- Review Active Status
- View Loan History

---

## S07 — Borrower 360

### Page Title Pattern

`Borrower 360: {borrower_name}`

### Header Data

- Borrower name
- Member type
- Folio number
- Active status
- Total shares
- Current outstanding
- Default status
- KYC status
- Latest application number

### Sections

- Borrower summary
- Nominee details
- KYC documents
- Land and crop evidence
- Shareholding and pledge details
- Loan applications
- Active loan accounts
- Repayment history
- Defaults and extensions
- Communication history
- Audit trail

### Empty State

`No loan history is available for this borrower.`

---

## S08 — New Loan Application

### Page Title

`New Loan Application`

### Intro Text

`Create a loan application for an eligible SFPCL member. The applicant and nominee must sign the application before submission.`

### Section Headings

1. Applicant Details
2. Membership and Shareholding
3. Loan Request Details
4. Nominee Details
5. KYC and Supporting Documents
6. Declarations and Consent
7. Review and Submit

### Field Labels

#### Applicant Details

- Borrower type
- Borrower name
- Folio number
- PAN
- Aadhaar number
- Mobile number
- Email address
- Address
- Associated FPC / Producer Institution

#### Membership and Shareholding

- Number of shares held
- Share certificate number
- Shareholding mode
- Demat account available?
- Maximum permissible loan limit

#### Loan Request Details

- Required loan amount
- Purpose of loan
- Crop / agricultural activity
- Proposed tenure
- Preferred repayment channel
- Subsidiary company involved

#### Nominee Details

- Nominee name
- Nominee age
- Nominee gender
- Nominee PAN
- Nominee Aadhaar number
- Relationship with borrower
- Nominee mobile number

#### KYC and Documents

- Borrower PAN card
- Borrower Aadhaar card
- Nominee PAN card
- Nominee Aadhaar card
- Share certificate
- 7/12 extract
- Crop plan
- Bank statement for past 6 months

### Declarations

- I confirm that the loan purpose is related to crop production or agricultural activity.
- I confirm that the information provided is true and complete.
- I consent to KYC / CKYC verification where applicable.
- I agree to execute the Term Sheet, Loan Agreement and required security documents if the loan is sanctioned.

### Buttons

- Save Draft
- Validate Application
- Submit Application

### Success Message

`Loan application submitted successfully. The application will now be checked for completeness.`

---

## S09 — Application Completeness Check

### Page Title

`Application Completeness Check`

### Intro Text

`Verify that all required applicant, nominee, KYC, shareholding, land, crop and bank documents are complete before generating the application number.`

### Checklist Labels

- Applicant details complete
- Nominee details complete
- Borrower PAN uploaded
- Borrower Aadhaar uploaded
- Nominee PAN uploaded
- Nominee Aadhaar uploaded
- Share certificate uploaded
- 7/12 extract uploaded
- Crop plan uploaded
- Bank statement for past 6 months uploaded
- Loan purpose captured
- Application signed by applicant
- Application signed by nominee

### Deficiency Modal

**Title:** Raise Deficiency  
**Reason label:** Deficiency reason  
**Details label:** Details to be communicated to borrower  
**Button:** Send Deficiency Note

### Success Message

`Application is complete. Application number {application_no} has been generated and added to the Loan Request Register.`

---

## S10 — Loan Request Register

### Page Title

`Loan Request Register`

### Intro Text

`System-generated register of all loan applications and their current lifecycle status.`

### Column Labels

- Application No.
- Application Date
- Borrower Name
- Member Type
- Folio No.
- Requested Amount
- Eligible Amount
- Current Status
- Assigned To
- Last Updated
- Decision
- Actions

### Export Name

`loan-request-register_{date}.xlsx`

---

## S11 — Loan Appraisal Note

### Page Title

`Loan Appraisal Note`

### Intro Text

`Prepare the appraisal note within 2 days of application receipt and record eligibility, loan limit, repayment capacity, risk and recommendation.`

### Section Headings

1. Application Summary
2. Eligibility Verification
3. Loan Limit Calculation
4. Repayment Capacity
5. Risk Assessment
6. Recommended Terms
7. Credit Manager Review

### Eligibility Labels

- Active member verified
- No default with SFPCL / subsidiary / associate company
- Land documents submitted
- KYC documents submitted
- Bank statement submitted
- Crop plan submitted
- Loan purpose agriculture-related
- Borrower agrees to Term Sheet and Loan Agreement

### Risk Labels

- Market risk
- Operational risk
- Borrower-specific risk
- Repayment risk
- Security adequacy
- Risk mitigation notes

### Recommendation Options

- Recommend Approval
- Recommend Rejection
- Send Back for Clarification

### Required Reason Labels

- Recommendation reason
- Rejection reason
- Clarification required

---

## S12 — Loan Limit Calculator

### Page Title

`Loan Limit Calculator`

### Intro Text

`Calculate borrower eligibility using shareholding-based and land-based limits. The final eligible amount is the lower of the two limits.`

### Formula Labels

- Shareholding-based limit
- Agricultural land-based limit
- Final eligible loan amount

### Display Formulae

```text
Shareholding-based limit = Number of shares held × Applicable percentage / value per share
Land-based limit = Per-acre cost of cultivation × Land area under cultivation
Final eligible amount = Lower of the two limits
```

### Policy Warning

`Policy confirmation required: The SOP references 30% of valuation per share, 10% of valuation per share and ₹200 per share. Confirm the operative value in Admin Settings before final sanction.`

### Field Labels

- Number of shares held
- Valuation per share
- Applicable percentage
- Applicable per-share amount
- Per-acre cost of cultivation
- Land area under cultivation
- Current cap per acre
- Requested loan amount
- Eligible loan amount
- Excess amount

---

## S13 — Credit Review and Rejection

### Page Title

`Credit Review`

### Intro Text

`Review the appraisal note and decide whether to submit the case for sanction, raise clarification or reject the application.`

### Rejection Note Fields

- Rejection reason category
- Detailed reason
- Criteria not met
- Documents missing
- Whether borrower may reapply
- Reapplication condition
- Communication mode

### Common Rejection Reasons

- Applicant is not an active member.
- Applicant has an existing default.
- KYC documents are incomplete.
- Land documents are incomplete.
- Crop plan is missing.
- Bank statement is missing.
- Loan purpose is not related to crop production or agriculture.
- Requested amount exceeds eligibility and exception is not approved.

### Rejection Success Message

`Rejection Note has been generated and marked for communication to the borrower.`

---

## S14 — Sanction Committee Review

### Page Title

`Sanction Committee Review`

### Intro Text

`Review eligibility, loan amount, purpose, compliance, borrowing history, risks and documents before recording the sanction decision.`

### Review Checklist

- Eligibility verified
- Loan amount within permissible limits
- Loan purpose aligned with company policy
- Compliance checks completed
- Past borrowing history reviewed
- Risk assessment reviewed
- Required documents authenticated
- Approval authority confirmed
- Conflict of interest checked

### Decision Options

- Approve
- Reject
- Approve with Exception
- Send Back for Clarification

### Approval Matrix Reminder

`Loans up to ₹5,00,000 require CFO + one Director. Loans above ₹5,00,000 or exceeding the permissible limit require CFO + two Directors.`

### Decision Reason Label

`Decision reason`

### Success Message

`Sanction decision recorded in the Credit Sanction Register.`

---

## S15 — Special Case Approval

### Page Title

`Special Case Approval`

### Intro Text

`Use this workflow when the borrower is a Sanction Committee member, Director or relative. Conflicted approvers must be excluded and member approval in a general meeting must be recorded.`

### Field Labels

- Special case type
- Conflicted person
- Relationship to borrower
- Excluded from approval?
- Remaining approvers
- General meeting approval date
- General meeting resolution reference
- Supporting minutes uploaded
- Remarks

### Blocker Message

`This case cannot be sanctioned until the required special approval details and general meeting approval evidence are recorded.`

---

## S16 — Documentation Workbench

### Page Title

`Documentation Workbench`

### Intro Text

`Prepare, upload, verify and approve all documents required after sanction and before disbursement.`

### Document Groups

- Borrower and nominee documents
- Witness documents
- Security documents
- Loan documents
- Bank verification documents
- Checklist and approvals

### Document Row Labels

- Document name
- Required / optional
- Status
- Owner
- Last updated
- Stamping required
- Notarisation required
- Signed by
- Verified by
- Actions

### Document Status Copy

- Pending upload
- Uploaded
- Pending signature
- Pending stamping
- Pending notarisation
- Pending verification
- Verified
- Rejected
- Not applicable

---

## S17 — Power of Attorney

### Page Title

`Power of Attorney`

### Intro Text

`Prepare and verify the Power of Attorney in favour of the Company Secretary. This document authorises specified actions in the event of loan default.`

### Requirement Note

`Power of Attorney must be signed by the farmer / borrower and nominee, executed on ₹500 stamp paper and notarised.`

### Field Labels

- Borrower name
- Nominee name
- Company Secretary name
- Stamp paper number
- Stamp value
- Execution date
- Notary details
- Signed by borrower
- Signed by nominee
- Verified by Company Secretary

---

## S18 — Tri-party Agreement / Declaration

### Page Title

`Declaration / Tri-party Agreement`

### Intro Text

`Use this document where repayment will be deducted by a subsidiary company from produce payments and transferred to SFPCL.`

### Parties Section

- Borrower
- SFPCL
- Subsidiary company

### Key Content Points

- Borrower sells produce to subsidiary company.
- Subsidiary deducts principal, interest or other dues from produce payment.
- Deducted amount is transferred to SFPCL.
- SFPCL adjusts the amount against outstanding loan obligation.

---

## S19 — SH-4 / CDSL Pledge

### Page Title

`Share Security`

### Tabs

- Physical Shares — SH-4
- Demat Shares — CDSL Pledge

### SH-4 Requirement Note

`SH-4 is required where shares are held physically. It must be signed by the shareholder and a valid witness.`

### CDSL Requirement Note

`For demat shares, pledge must be created through CDSL using the pledge request process. Record PRF, PSN, pledge acceptance and pledge status.`

### CDSL Field Labels

- Pledgor BO ID
- Pledgee BO ID
- Depository Participant
- Pledge Request Form submitted
- Pledge Sequence Number
- Pledge accepted by pledgee DP
- Agreement number informed
- Pledge status
- Invocation status
- Unpledge status

---

## S20 — Term Sheet

### Page Title

`Term Sheet`

### Intro Text

`Record and generate the borrower-facing summary of sanctioned loan terms.`

### Required Sections

- Borrower details
- Nominee details
- Shareholding details
- Facility type
- Loan amount
- Purpose of loan
- Rate of interest
- Interest tenure
- Repayment date
- Penalty interest
- Other charges / fees
- Security
- Dispute resolution
- Signing authority

### Signing Authority Note

`For loan amount below ₹5,00,000, Term Sheet must be signed by CFO. For loan amount exceeding ₹5,00,000, it must be signed by CFO and two Directors.`

---

## S21 — Loan Agreement

### Page Title

`Loan Agreement`

### Intro Text

`Generate and verify the legally binding loan agreement after Term Sheet execution.`

### Requirement Note

`Loan Agreement must be executed on ₹500 stamp paper, notarised and signed by the loan applicant and witness.`

### Required Fields

- Agreement date
- Borrower details
- Sanctioned loan amount
- Purpose
- Interest rate
- Tenure
- Repayment obligations
- Security details
- Default events
- Remedies
- Charges
- Dispute resolution
- Witness details

---

## S22 — Bank Verification

### Page Title

`Bank Verification`

### Intro Text

`Verify borrower bank account details and resolve any signature mismatch before disbursement.`

### Required Items

- Cancelled cheque
- Bank account number
- IFSC
- Branch
- Account holder name
- Signature match status
- Bank Verification Letter, if required
- Borrower declaration on non-judicial stamp paper, if used instead

### Signature Mismatch Alert

`Signature mismatch found. Upload a Bank Verification Letter signed and stamped by the bank or borrower declaration on non-judicial stamp paper before disbursement.`

---

## S23 — Document Checklist

### Page Title

`Document Checklist`

### Intro Text

`Use the checklist as the final document control index before disbursement.`

### Sign-Off Labels

- Company Secretary verification
- Credit Manager verification
- Sanction Committee verification
- Senior Manager – Finance disbursement confirmation

### Sign-Off Meaning Text

| Signatory | Text |
|---|---|
| Company Secretary | I confirm that all documents required for loan disbursement have been verified and attached. |
| Credit Manager | I confirm that loan limits have been reviewed and confirmed. |
| Sanction Committee | I confirm final approval for loan disbursement as per authority matrix. |
| Senior Manager – Finance | I confirm that the loan has been disbursed to the applicant’s bank account. |

---

## S24 — SAP Customer Code Request

### Page Title

`SAP Customer Code Request`

### Intro Text

`Create or confirm the SAP Customer Code required for loan accounting and disbursement.`

### Field Labels

- Existing SAP Customer Code?
- SAP Customer Code
- Borrower full name
- Aadhaar number
- PAN number
- Address
- Email ID
- Loan application number
- Request sent to Senior Manager – Finance
- Confirmation received

### Rule Message

`A new SAP Customer Code is created only for first-time borrowers. Existing borrowers continue with the existing Customer ID.`

---

## S25 — Disbursement Queue

### Page Title

`Disbursement Queue`

### Intro Text

`Review cases that have completed sanction, documentation, SAP setup and bank verification and are ready for payment initiation.`

### Columns

- Application No.
- Borrower Name
- Sanctioned Amount
- Bank Account
- SAP Code
- Documentation Status
- Final Approval Status
- Disbursement Status
- Assigned To
- Actions

### Blocker Banner

`Disbursement cannot be initiated because one or more required controls are incomplete.`

---

## S26 — Disbursement Initiation

### Page Title

`Initiate Disbursement`

### Intro Text

`Verify approved loan details and initiate online payment through SFPCL’s RBL Bank account.`

### Confirmation Checklist

- Sanction Committee approval completed
- Checklist signed by required users
- SAP Customer Code created / confirmed
- Borrower bank account verified
- Cancelled cheque verified
- Loan amount matches sanction
- Payment details reviewed

### Button

`Initiate Disbursement`

### Success Message

`Disbursement initiated and sent to Chief Financial Controller for final approval.`

---

## S27 — Bank Transfer Approval

### Page Title

`Bank Transfer Approval`

### Intro Text

`Final approval by Chief Financial Controller is required before the bank transfer is executed.`

### Decision Options

- Approve Transfer
- Reject Transfer
- Send Back for Correction

### Confirmation Text

`I confirm that the bank transfer details match the sanctioned loan and verified borrower bank account.`

---

## S28 — Disbursement Advice

### Page Title

`Disbursement Advice`

### Intro Text

`Send disbursement confirmation to the borrower after bank transfer completion.`

### Required Content

- Application No.
- Loan account number
- Borrower name
- Disbursed amount
- Disbursement date
- Bank account last four digits
- Repayment start / due details
- Contact for queries

---

## S29 — Loan Account 360

### Page Title Pattern

`Loan Account: {loan_account_no}`

### Header Fields

- Loan account number
- Application number
- Borrower name
- Loan status
- Sanctioned amount
- Disbursed amount
- Outstanding principal
- Outstanding interest
- Next due date
- Repayment channel
- DPD status

### Tabs

- Overview
- Ledger
- Repayments
- Interest
- Documents
- Security
- Monitoring
- Defaults
- Communications
- Audit Trail

---

## S30 — Direct Repayment Posting

### Page Title

`Record Direct Repayment`

### Intro Text

`Record RTGS / NEFT repayment received directly from borrower. Partial repayments must be adjusted first against principal.`

### Field Labels

- Loan account number
- Borrower name
- Payment date
- Amount received
- Payment mode
- Bank reference number
- Principal allocation
- Interest allocation
- Charges allocation
- Posted in SAP?
- SAP posting date

### Allocation Rule Note

`Partial repayment is adjusted first against principal before interest recovery, as per SOP.`

---

## S31 — Subsidiary Deduction Posting

### Page Title

`Record Subsidiary Deduction`

### Intro Text

`Record repayment deducted by subsidiary company from borrower produce payment and transferred to SFPCL.`

### Field Labels

- Subsidiary company
- Borrower name
- Application number
- Loan account number
- Produce payment reference
- Deducted amount
- Transfer date
- Bank statement reference
- Principal allocation
- Interest allocation
- Charges allocation
- SAP receipt entry

### Validation Message

`Bank statement transaction must clearly identify borrower name and loan application number.`

---

## S32 — Interest Invoice

### Page Title

`Interest Invoice`

### Intro Text

`Generate yearly interest invoice for each farmer who has availed a loan.`

### Field Labels

- Financial year
- Loan account number
- Borrower name
- Principal outstanding
- Interest rate
- Interest period
- Interest amount
- Invoice date
- Due date
- Invoice status

### Capitalisation Warning

`If interest remains unpaid up to 30 April of the next financial year, it will be added to principal at the beginning of the next financial year and interest will be calculated on revised principal.`

---

## S33 — Monthly Accrual Entry

### Page Title

`Monthly Interest Accrual`

### Intro Text

`Review and post monthly interest accrual entries in SAP.`

### Field Labels

- Accrual month
- Loan account number
- Borrower name
- Outstanding principal
- Interest rate
- Accrued interest
- SAP entry number
- Posted by
- Posted date

---

## S34 — DPD Monitoring Dashboard

### Page Title

`DPD Monitoring Dashboard`

### Intro Text

`Monitor overdue loan accounts and prepare quarterly MIS for CFO review.`

### DPD Buckets

- 1 year to 2 years
- 2 years to 3 years
- More than 3 years

### Columns

- Loan account number
- Borrower name
- Outstanding principal
- Outstanding interest
- Last repayment date
- Days past due
- DPD bucket
- Reminder status
- Extension status
- Next action

---

## S35 — Reminder Queue

### Page Title

`Reminder Queue`

### Intro Text

`Send SMS or phone reminders for loans outstanding beyond one year at quarter-end.`

### Field Labels

- Borrower name
- Loan account number
- Outstanding amount
- Last reminder date
- Reminder mode
- Reminder notes
- Next follow-up date

### Reminder Mode Labels

- SMS
- Phone Call
- Email
- Letter

---

## S36 — Extension Note

### Page Title

`Extension Note`

### Intro Text

`Record extension details where non-payment is assessed as non-intentional.`

### Field Labels

- Missed repayment date
- Grace period end date
- Reason for non-payment
- Non-payment classification
- Evidence reviewed
- Extension granted until
- Prepared by Credit Manager
- Approval reference
- Remarks

### Rule Note

`If principal remains unpaid after the three-month grace period and non-payment is non-intentional, the company may provide a further one-year extension.`

---

## S37 — Non-Payment Note

### Page Title

`Note for Non-Payment`

### Intro Text

`Prepare the note for Sanction Committee review when repayment remains incomplete after extension or when recovery action is being considered.`

### Field Labels

- Loan account number
- Borrower name
- Outstanding principal
- Outstanding interest
- Original due date
- Grace period granted
- Extension granted
- Current non-payment reason
- Intentional / non-intentional assessment
- Evidence summary
- Recommended action
- Prepared by
- Submitted to Sanction Committee

---

## S38 — Recovery Approval

### Page Title

`Recovery Approval`

### Intro Text

`Sanction Committee must approve recovery action before invoking SH-4, CDSL pledge or blank-dated cheque.`

### Recovery Options

- Initiate sale of shares
- Invoke CDSL pledge
- Present blank-dated cheque
- Continue follow-up
- Send back for further scrutiny

### Confirmation Text

`I confirm that the Note for Non-Payment has been reviewed and this recovery decision is recorded for audit purposes.`

---

## S39 — Loan Closure

### Page Title

`Loan Closure`

### Intro Text

`Close the loan account after full repayment and completion of NOC, security return and archival requirements.`

### Closure Checklist

- Principal fully repaid
- Interest fully paid or adjusted
- Charges fully paid or waived with approval
- SAP ledger reconciled
- NOC generated
- SH-4 returned, if applicable
- Blank-dated cheque returned
- CDSL unpledge completed, if applicable
- Documents archived for 8 years
- Closure communication sent

### Success Message

`Loan account closed successfully. NOC and security return records have been updated.`

---

## S40 — Compliance Dashboard

### Page Title

`Compliance Dashboard`

### Intro Text

`Track statutory, policy and internal control requirements across the loan portfolio.`

### Cards

- Producer Company lending controls
- Section 186 loan limit tracker
- NBFC principal business test
- KYC / AML and re-KYC
- Stamp duty and documentation
- Money-lending law review
- Accounting and reporting
- Data protection and access review
- Record retention
- Grievances

---

## S41 — Section 186 Tracker

### Page Title

`Section 186 Tracker`

### Intro Text

`Monitor loan limits against paid-up capital, free reserves and securities premium as required by the SOP.`

### Field Labels

- Paid-up capital
- Free reserves
- Securities premium
- 60% limit calculation
- 100% free reserves and securities premium calculation
- Higher permissible threshold
- Existing loan exposure
- Proposed exposure
- Headroom available
- Special resolution required?
- Board approval reference

---

## S42 — NBFC Principal Business Test

### Page Title

`NBFC Principal Business Test`

### Intro Text

`Track whether financial assets and income from financial assets cross the 50% thresholds requiring NBFC registration review.`

### Field Labels

- Total assets
- Financial assets
- Financial assets percentage
- Gross income
- Income from financial assets
- Financial income percentage
- Test period
- Status
- Board note reference
- CFO reviewer

---

## S43 — KYC / Re-KYC Tracker

### Page Title

`KYC / Re-KYC Tracker`

### Intro Text

`Monitor borrower KYC completion and periodic re-KYC every two years.`

### Columns

- Borrower name
- PAN status
- Aadhaar status
- CKYC consent status
- Risk rating
- Last KYC date
- Re-KYC due date
- KYC status
- Action

---

## S44 — Stamp Duty Tracker

### Page Title

`Stamp Duty Tracker`

### Intro Text

`Track stamp paper, e-stamp and notarisation requirements for loan documents.`

### Columns

- Application No.
- Document name
- Stamp value
- Stamp paper number
- Execution date
- Notarisation status
- Verified by CS
- Deficiency

---

## S45 — Grievance Log

### Page Title

`Grievance Log`

### Intro Text

`Record borrower complaints and track resolution within the defined TAT.`

### Fields

- Grievance ID
- Borrower name
- Loan account number
- Grievance category
- Description
- Received date
- Received through
- Assigned to
- Resolution due date
- Resolution details
- Closure date
- Status

---

## S46 — Reports

### Page Title

`Reports`

### Intro Text

`Generate operational, compliance, sanction, repayment and audit reports.`

### Report Names

- Loan Request Register
- Credit Sanction Register
- Exception Register
- Active Loan Portfolio
- Disbursement Report
- Repayment Report
- Interest Invoice Report
- DPD Monitoring Report
- CFO Quarterly MIS
- Board Pack
- KYC / Re-KYC Report
- Stamp Duty Report
- Record Retention Report
- Grievance Report
- Audit Trail Export

---

## S47 — Admin Settings

### Page Title

`Admin Settings`

### Intro Text

`Configure policy values, roles, templates, notification rules and compliance parameters. Board approval is required for policy changes defined in the SOP.`

### Setting Groups

- Loan Product Configuration
- Loan Limit Rules
- Share Valuation
- Scale of Finance
- Interest Rate and Charges
- Approval Matrix
- Document Templates
- Notification Templates
- Compliance Settings
- User Roles and Permissions
- Audit and Retention Settings

### Policy Change Warning

`Changing this value may require Board approval. Record the Board approval reference before activating the change.`

---

## 15. Field Label Dictionary

### 15.1 Borrower and Member Fields

| Data field | UI label | Help text |
|---|---|---|
| borrower_type | Borrower type | Select Individual Member or Producer Institution / FPC. |
| member_name | Member name | Use the full legal name as per membership records. |
| folio_number | Folio number | Enter the folio number of shares held in SFPCL. |
| member_status | Member status | Shows whether the applicant is an eligible SFPCL member. |
| active_status | Active member status | Based on services availed and produce supplied as per Articles of Association. |
| pan | PAN | Permanent Account Number of borrower. |
| aadhaar | Aadhaar number | 12-digit Aadhaar number of borrower. |
| mobile | Mobile number | Used for borrower reminders and communication. |
| email | Email address | Used for official borrower communication. |
| address | Address | Current communication address. |
| associated_fpc | Associated FPC | Producer Institution through which the individual may supply produce. |
| subsidiary_link | Subsidiary company link | Subsidiary company involved in produce purchase or repayment deduction. |

### 15.2 Nominee Fields

| Data field | UI label | Help text |
|---|---|---|
| nominee_name | Nominee name | Enter full name of nominee. |
| nominee_age | Nominee age | Nominee must not be a minor. |
| nominee_gender | Nominee gender | Select gender as provided by applicant. |
| nominee_pan | Nominee PAN | PAN of nominee. |
| nominee_aadhaar | Nominee Aadhaar number | Aadhaar number of nominee. |
| nominee_relationship | Relationship with borrower | Relationship between nominee and borrower. |
| nominee_signature | Nominee signature | Required on application and applicable documents. |

### 15.3 Witness Fields

| Data field | UI label | Help text |
|---|---|---|
| witness_name | Witness name | Witness must be an existing SFPCL shareholder. |
| witness_pan | Witness PAN | PAN copy required. |
| witness_aadhaar | Witness Aadhaar number | Aadhaar copy required. |
| witness_shareholder_status | Witness shareholder status | Confirm witness is an existing SFPCL shareholder. |
| witness_signature | Witness signature | Required on Loan Agreement and SH-4 where applicable. |

### 15.4 Loan Application Fields

| Data field | UI label | Help text |
|---|---|---|
| application_no | Application No. | System-generated reference number beginning with LO00000001. |
| application_date | Application date | Date application is submitted. |
| requested_amount | Required loan amount | Amount requested by borrower. |
| purpose | Purpose of loan | Must be related to crop production or agricultural activity. |
| crop_activity | Crop / agricultural activity | Crop or activity for which loan is requested. |
| tenure_requested | Requested tenure | Proposed loan tenure. |
| repayment_channel | Repayment channel | Select Direct by Farmer or Through Subsidiary Company. |
| subsidiary_company | Subsidiary company | Required when repayment is through subsidiary deduction. |
| application_status | Application status | Current stage in the loan lifecycle. |

### 15.5 Loan Limit Fields

| Data field | UI label | Help text |
|---|---|---|
| shares_held | Number of shares held | Used to calculate shareholding-based loan limit. |
| share_valuation | Valuation per share | Based on latest audited financials approved at AGM. |
| valuation_method | Valuation method | Net Asset Value Method based on Fair Market Valuation. |
| loan_limit_percentage | Applicable percentage | Policy percentage used for shareholding-based limit. |
| per_share_cap | Per-share cap | Current SOP references ₹200 per share; confirm policy. |
| land_area | Land area under cultivation | Used for land-based limit. |
| scale_of_finance | Scale of Finance | Per-acre cost of cultivation fixed annually by company. |
| per_acre_cap | Current per-acre cap | Current cap is ₹20,000 per acre. |
| share_limit | Shareholding-based limit | Limit calculated from shareholding. |
| land_limit | Land-based limit | Limit calculated from land area. |
| eligible_amount | Final eligible loan amount | Lower of shareholding-based and land-based limits. |
| excess_amount | Excess over eligibility | Amount by which request exceeds eligible limit. |

### 15.6 Appraisal Fields

| Data field | UI label | Help text |
|---|---|---|
| eligibility_summary | Eligibility summary | Summary of member eligibility and document checks. |
| repayment_capacity | Repayment capacity | Credit assessment of borrower’s ability to repay. |
| past_borrowing | Past borrowing history | Previous loans and repayment discipline. |
| default_check | Default check | Check default with SFPCL, subsidiary or associate company. |
| risk_rating | Risk rating | Internal risk classification. |
| risk_notes | Risk notes | Market, operational and borrower-specific risks. |
| recommended_amount | Recommended loan amount | Amount recommended by Credit Assessment Team. |
| recommended_tenure | Recommended tenure | Tenure recommended in appraisal. |
| recommended_security | Recommended security | Security documents or pledge required. |
| appraisal_status | Appraisal status | Draft, submitted, approved or rejected. |

### 15.7 Approval Fields

| Data field | UI label | Help text |
|---|---|---|
| approval_authority | Approval authority | Required authority based on amount and exception status. |
| approver_name | Approver name | CFO or Director assigned to decision. |
| decision | Decision | Approve, reject, approve with exception or send back. |
| decision_reason | Decision reason | Required for all rejection, exception and send-back decisions. |
| sanction_date | Sanction date | Date sanction decision is recorded. |
| credit_sanction_register_ref | Credit Sanction Register reference | Reference for recorded decision. |
| exception_required | Exception required? | Indicates if requested amount exceeds permissible limit or policy deviation exists. |
| exception_register_ref | Exception Register reference | Required for approved deviations. |

### 15.8 Documentation Fields

| Data field | UI label | Help text |
|---|---|---|
| document_name | Document name | Name of required document. |
| document_type | Document type | KYC, security, loan, bank, checklist or compliance. |
| document_status | Document status | Current status of document. |
| stamp_required | Stamping required? | Indicates whether stamp paper / e-stamp is required. |
| stamp_value | Stamp value | Stamp duty value, such as ₹500. |
| stamp_number | Stamp paper number | Unique stamp paper or e-stamp identifier. |
| notarisation_required | Notarisation required? | Indicates whether notarisation is required. |
| signed_by | Signed by | Parties who have signed the document. |
| verified_by | Verified by | User who verified the document. |
| verification_date | Verification date | Date document was verified. |

### 15.9 SAP and Disbursement Fields

| Data field | UI label | Help text |
|---|---|---|
| sap_customer_code | SAP Customer Code | Unique SAP code used for accounting entries. |
| sap_request_status | SAP request status | Requested, in progress, confirmed or rejected. |
| disbursement_amount | Disbursement amount | Final amount to transfer. |
| bank_account_no | Bank account number | Borrower bank account verified using cancelled cheque. |
| ifsc | IFSC | Bank branch IFSC code. |
| disbursement_bank | Disbursement bank | SFPCL bank account used for transfer. |
| payment_reference | Payment reference | Bank transaction reference. |
| cfc_approval_status | CFC approval status | Final approval status by Chief Financial Controller. |
| disbursement_date | Disbursement date | Date bank transfer completed. |

### 15.10 Repayment and Monitoring Fields

| Data field | UI label | Help text |
|---|---|---|
| repayment_mode | Repayment mode | Direct RTGS / NEFT or subsidiary deduction. |
| repayment_amount | Repayment amount | Amount received. |
| principal_allocation | Principal allocation | Portion applied to principal. |
| interest_allocation | Interest allocation | Portion applied to interest. |
| outstanding_principal | Outstanding principal | Principal balance after repayments. |
| outstanding_interest | Outstanding interest | Interest not yet paid. |
| due_date | Due date | Scheduled repayment due date. |
| dpd_bucket | DPD bucket | Overdue ageing classification. |
| reminder_status | Reminder status | Whether reminder was sent. |
| extension_status | Extension status | Grace or one-year extension status. |

---

## 16. Notification and Communication Specification

### 16.1 Notification Channels

Supported channels should include:

- In-app notification.
- Email.
- SMS.
- Hard copy letter tracking.
- Phone call log.

Not every message needs every channel. Borrower-facing official decisions should be recordable by email or courier / letter where required.

### 16.2 Internal Task Notification Templates

#### Application Submitted

**Title:** New loan application submitted  
**Message:** Application {application_no} for {borrower_name} has been submitted and is ready for completeness check.

#### Appraisal Due

**Title:** Appraisal due  
**Message:** Loan Appraisal Note for {application_no} must be prepared within the 2-day TAT from application receipt.

#### Sanction Request

**Title:** Sanction decision required  
**Message:** Application {application_no} for {borrower_name} is pending Sanction Committee review.

#### Exception Approval Required

**Title:** Exception approval required  
**Message:** Application {application_no} exceeds the permissible loan limit or policy threshold. Review and record decision in the Exception Register.

#### Documents Ready for CS Review

**Title:** Documents ready for CS review  
**Message:** Documentation set for {application_no} has been prepared and is awaiting Company Secretary verification.

#### SAP Code Request

**Title:** SAP Customer Code required  
**Message:** Create or confirm SAP Customer Code for borrower {borrower_name}, application {application_no}.

#### Bank Transfer Approval

**Title:** Bank transfer approval required  
**Message:** Disbursement for {application_no} is awaiting final approval by Chief Financial Controller.

#### Quarterly DPD Review

**Title:** Quarterly DPD review due  
**Message:** DPD monitoring report is ready for CFO review for the current quarter.

### 16.3 Borrower Acknowledgement Message

**Subject:** Loan application received — {application_no}

**Body:**

```text
Dear {borrower_name},

We have received your loan application. Your application reference number is {application_no}.

The application will be checked for completeness and eligibility. If any document or information is missing, we will inform you.

Regards,
Sahyadri Farmers Producer Company Limited
```

### 16.4 Deficiency Message

**Subject:** Action required for loan application {application_no}

**Body:**

```text
Dear {borrower_name},

Your loan application {application_no} requires the following corrections or additional documents:

{deficiency_list}

Please submit the required information so that the application can be processed further.

Regards,
Sahyadri Farmers Producer Company Limited
```

### 16.5 Rejection Message

**Subject:** Loan application decision — {application_no}

**Body:**

```text
Dear {borrower_name},

Your loan application {application_no} has not been approved for the following reason:

{rejection_reason}

You may re-apply after fulfilling the required criteria, where applicable.

Regards,
Sahyadri Farmers Producer Company Limited
```

### 16.6 Sanction Approval Message

**Subject:** Loan sanctioned — {application_no}

**Body:**

```text
Dear {borrower_name},

Your loan application {application_no} has been sanctioned for ₹{sanctioned_amount}, subject to completion of documentation, stamping, verification and disbursement controls.

The Compliance Team will coordinate the required documents and signatures.

Regards,
Sahyadri Farmers Producer Company Limited
```

### 16.7 Disbursement Advice Message

**Subject:** Loan disbursed — {loan_account_no}

**Body:**

```text
Dear {borrower_name},

Your loan has been disbursed.

Application No.: {application_no}
Loan Account No.: {loan_account_no}
Disbursed Amount: ₹{disbursement_amount}
Disbursement Date: {disbursement_date}
Bank Account: ****{bank_last_four}

Please follow the repayment terms communicated in your Term Sheet and Loan Agreement.

Regards,
Sahyadri Farmers Producer Company Limited
```

### 16.8 Interest Rate Change Message

**Subject:** Interest rate update for loan account {loan_account_no}

**Body:**

```text
Dear {borrower_name},

The interest rate applicable to your loan account {loan_account_no} has been revised to {new_interest_rate}% with effect from {effective_date}.

This change is based on the floating rate terms stated in your Term Sheet.

Regards,
Sahyadri Farmers Producer Company Limited
```

### 16.9 Interest Capitalisation Message

**Subject:** Outstanding interest added to principal — {loan_account_no}

**Body:**

```text
Dear {borrower_name},

Interest outstanding on your loan account {loan_account_no} remained unpaid up to 30 April. As per the loan terms, the unpaid interest of ₹{interest_amount} has been added to principal at the beginning of the new financial year.

Revised principal: ₹{revised_principal}

Future interest will be calculated on the revised principal.

Regards,
Sahyadri Farmers Producer Company Limited
```

### 16.10 Repayment Reminder SMS

```text
Reminder: Loan account {loan_account_no} has outstanding amount ₹{outstanding_amount}. Please contact SFPCL or make repayment as per agreed terms.
```

### 16.11 Closure and NOC Message

**Subject:** Loan closed and NOC issued — {loan_account_no}

**Body:**

```text
Dear {borrower_name},

Your loan account {loan_account_no} has been fully repaid and closed.

The No Objection Certificate has been issued. Security documents, including SH-4 and blank-dated cheque where applicable, have been returned / marked for return.

Regards,
Sahyadri Farmers Producer Company Limited
```

---

## 17. Generated Document Content Specification

### 17.1 Loan Application Form

Must include:

- Borrower name and details.
- Member type.
- Folio number.
- Number of shares held.
- Maximum permissible loan limit.
- Required loan amount.
- Purpose of loan.
- Nominee details including name, age, Aadhaar, PAN and gender.
- Document checklist.
- Applicant declaration.
- Nominee declaration / acknowledgement.
- Applicant signature.
- Nominee signature.
- Date and place.

### 17.2 Loan Appraisal Note

Must include:

- Application details.
- Borrower details.
- Membership status.
- Active member eligibility.
- Existing default check.
- KYC status.
- Land document status.
- Crop plan status.
- Bank statement status.
- Loan purpose.
- Shareholding-based loan limit.
- Land-based loan limit.
- Final eligible amount.
- Requested amount.
- Recommended amount.
- Risk assessment.
- Repayment capacity assessment.
- Security recommendation.
- Recommendation decision.
- Prepared by Deputy Manager – Finance.
- Reviewed by Credit Manager.
- Date and time.

### 17.3 Power of Attorney

Must include:

- Borrower details.
- Nominee details.
- Company Secretary as attorney holder.
- Authority to initiate sale of shares in default scenario.
- Stamp paper reference.
- Notary details.
- Borrower signature.
- Nominee signature.
- Witness / execution details where required.

### 17.4 Declaration / Tri-party Agreement

Must include:

- SFPCL details.
- Borrower details.
- Subsidiary company details.
- Produce sale relationship.
- Deduction authorisation.
- Amounts covered: principal, interest and other dues.
- Transfer obligation from subsidiary to SFPCL.
- Adjustment against outstanding loan.
- Applicant and nominee signature.
- Company / subsidiary signature blocks.

### 17.5 SH-4

Must include or track:

- Shareholder details.
- Transferee / security holder details as per applicable process.
- Share details.
- Signature of shareholder.
- Witness details and signature.
- Custody status.
- Return or invocation status.

### 17.6 Term Sheet

Must include:

- Borrower details.
- Nominee details.
- Share details.
- Facility type: short-term or long-term.
- Loan amount.
- Purpose of loan.
- Rate of interest.
- Tenure of interest.
- Repayment date.
- Penalty interest.
- Other charges / fees.
- Security details.
- Dispute resolution.
- Signature of applicant and nominee.
- CFO / Directors signature as per threshold.

### 17.7 Loan Agreement

Must include:

- Parties.
- Sanctioned amount.
- Disbursement terms.
- Purpose and end-use.
- Interest and charges.
- Tenure and repayment obligations.
- Security documents.
- Events of default.
- Remedies.
- Borrower covenants.
- Dispute resolution.
- Stamp paper reference.
- Notarisation details.
- Applicant signature.
- Witness signature.

### 17.8 Bank Verification Letter

Must include:

- Borrower name.
- Bank account number.
- IFSC.
- Branch.
- Signature confirmation.
- Bank official name.
- Bank stamp.
- Date.

### 17.9 Document Checklist

Must include:

- Application Form.
- Borrower KYC.
- Nominee KYC.
- Witness PAN and Aadhaar.
- Cancelled cheque.
- Blank-dated cheque.
- PoA.
- Tri-party Agreement / Declaration.
- SH-4 or CDSL pledge evidence.
- Term Sheet.
- Loan Agreement.
- Bank Verification Letter or borrower declaration if required.
- CS verification sign-off.
- Credit Manager verification sign-off.
- Sanction Committee sign-off.
- Senior Manager – Finance disbursement sign-off.

### 17.10 Rejection Note

Must include:

- Application number.
- Borrower name.
- Rejection stage.
- Rejection reason.
- Deficiencies / unmet criteria.
- Whether reapplication is allowed.
- Conditions for reapplication.
- Prepared by.
- Approved by if required.
- Communication mode.
- Date.

### 17.11 Extension Note

Must include:

- Loan account number.
- Borrower name.
- Scheduled repayment due date.
- Grace period granted.
- Reason for non-payment.
- Intentional / non-intentional assessment.
- Evidence reviewed.
- Extension period.
- Prepared by Credit Manager.
- Approval record.

### 17.12 Note for Non-Payment

Must include:

- Loan account number.
- Borrower name.
- Outstanding principal.
- Outstanding interest.
- Repayment history.
- Reminder history.
- Grace and extension history.
- Reason for continued non-payment.
- Classification recommendation.
- Recommended recovery action.
- Sanction Committee decision section.

### 17.13 NOC

Must include:

- Borrower name.
- Loan account number.
- Application number.
- Confirmation of full repayment.
- Closure date.
- Confirmation of no dues.
- Security return details.
- Authorised signatory.
- Date.

---

## 18. Report and Export Content Specification

### 18.1 Loan Request Register Export

File name:

```text
loan-request-register_{YYYYMMDD}.xlsx
```

Columns:

- Application No.
- Application Date
- Borrower Name
- Member Type
- Folio No.
- Requested Amount
- Eligible Amount
- Application Status
- Current Owner
- Decision
- Decision Date
- Rejection Reason

### 18.2 Credit Sanction Register Export

Columns:

- Application No.
- Borrower Name
- Requested Amount
- Eligible Amount
- Sanctioned Amount
- Approval Authority
- CFO Decision
- Director 1 Decision
- Director 2 Decision
- Decision Date
- Decision Reason
- Exception Required
- Exception Register Ref.

### 18.3 Exception Register Export

Columns:

- Exception ID
- Application No.
- Borrower Name
- Exception Type
- Policy Rule
- Requested Deviation
- Reason
- Approver(s)
- Approval Date
- Status
- Closure Remarks

### 18.4 Disbursement Report

Columns:

- Application No.
- Loan Account No.
- Borrower Name
- Sanctioned Amount
- Disbursed Amount
- SAP Customer Code
- Bank Account Last Four Digits
- Disbursement Date
- Payment Reference
- Initiated By
- Approved By CFC

### 18.5 Repayment Report

Columns:

- Loan Account No.
- Borrower Name
- Repayment Date
- Payment Mode
- Amount Received
- Principal Allocation
- Interest Allocation
- Charges Allocation
- Outstanding Principal
- Outstanding Interest
- SAP Entry Reference

### 18.6 DPD Monitoring Report

Columns:

- Loan Account No.
- Borrower Name
- Due Date
- Outstanding Principal
- Outstanding Interest
- Last Payment Date
- Days Past Due
- DPD Bucket
- Reminder Status
- Extension Status
- Recommended Next Action

### 18.7 CFO Quarterly MIS

Sections:

- Portfolio summary.
- New applications received.
- Loans sanctioned.
- Loans disbursed.
- Loans rejected.
- Outstanding portfolio.
- Repayments received.
- Interest accrued.
- DPD buckets.
- Defaults and extensions.
- Exceptions approved.
- Compliance actions due.

---

## 19. Audit Trail Content Specification

### 19.1 Audit Event Format

Use this structure:

```text
{action} by {user_name} ({role}) on {date_time}. {details}
```

Examples:

- Application submitted by Ramesh Patil (Borrower) on 07 Aug 2025, 10:32 AM.
- Application number LO00000001 generated by Deputy Manager – Finance on 07 Aug 2025, 11:05 AM.
- Loan Appraisal Note submitted by Credit Manager on 08 Aug 2025, 04:10 PM.
- Sanction approved by CFO on 09 Aug 2025, 12:30 PM.
- Power of Attorney verified by Company Secretary on 10 Aug 2025, 03:40 PM.
- Disbursement initiated by Senior Manager – Finance on 11 Aug 2025, 02:15 PM.
- Bank transfer approved by Chief Financial Controller on 11 Aug 2025, 02:40 PM.

### 19.2 Audit Event Categories

- Application
- Eligibility
- Appraisal
- Sanction
- Exception
- Documentation
- Security
- SAP
- Disbursement
- Repayment
- Interest
- Monitoring
- Default
- Recovery
- Closure
- Compliance
- Admin Configuration
- User Access

### 19.3 Change Log Copy

For field changes:

```text
{field_label} changed from {old_value} to {new_value} by {user_name} on {date_time}.
```

For file changes:

```text
{document_name} uploaded by {user_name} on {date_time}.
```

For policy configuration changes:

```text
{policy_setting} changed from {old_value} to {new_value}. Board approval reference: {approval_reference}.
```

---

## 20. Compliance Content Specification

### 20.1 Producer Company Lending Control

Display text:

`Loans may be processed only for eligible SFPCL members as permitted under the Producer Company framework and the company’s Articles of Association.`

### 20.2 Section 186 Warning

Display text:

`Review whether the proposed loan exposure remains within Section 186 limits. If limits are exceeded, required Board and special resolution approvals must be recorded before proceeding.`

### 20.3 NBFC Test Warning

Display text:

`Quarterly NBFC principal business test must be reviewed. If financial assets and income from financial assets exceed applicable thresholds, regulatory registration implications must be assessed.`

### 20.4 KYC / AML Notice

Display text:

`KYC documents must be collected, verified and retained as per applicable KYC / AML requirements. Re-KYC must be monitored every two years.`

### 20.5 Stamp Duty Notice

Display text:

`Loan documents requiring stamp duty must be stamped before disbursement. Unstamped or insufficiently stamped documents may be inadmissible as evidence and may attract penalties.`

### 20.6 Data Protection Notice

Display text:

`KYC and borrower documents contain sensitive information. Access is restricted by role and all activity is logged.`

### 20.7 Record Retention Notice

Display text:

`Loan files, registers, minutes and related records must be retained for at least eight years or longer if required by law or internal policy.`

---

## 21. Help Text and Tooltips

### 21.1 Application Number

`Generated sequentially after completeness check. The sequence starts with LO00000001.`

### 21.2 Active Member

`An active member is determined based on services availed and produce supplied to SFPCL, subsidiaries, step-down subsidiaries or through an eligible Producer Institution as per the Articles of Association.`

### 21.3 Loan Limit

`The eligible loan amount is the lower of the shareholding-based limit and the land-based Scale of Finance limit.`

### 21.4 Scale of Finance

`Per-acre cost of cultivation fixed annually by SFPCL based on prevailing agricultural cost norms. Current SOP cap is ₹20,000 per acre.`

### 21.5 Share Valuation

`Share valuation is based on latest audited financial statements approved at AGM using Net Asset Value Method based on Fair Market Valuation.`

### 21.6 Floating Interest Rate

`The interest rate may change based on bank rates and must be communicated to the borrower by SMS or email.`

### 21.7 Blank-Dated Cheque

`Collected as security. It may be used for recovery only after required approval and as per the approved recovery process.`

### 21.8 SH-4

`Required when shares are held physically. It is retained as security and returned after loan closure unless invoked through approved recovery action.`

### 21.9 CDSL Pledge

`Required when shares are held in demat form. Pledge and unpledge actions are recorded through the depository process.`

### 21.10 NOC

`No Objection Certificate issued after complete repayment and closure of the loan account.`

---

## 22. Error Pages and System-Level Messages

### 22.1 General Error

**Title:** Something went wrong  
**Body:** The request could not be completed. Please try again or contact support if the issue continues.

### 22.2 Permission Error

**Title:** Access restricted  
**Body:** You do not have permission to view or update this record. Contact the system administrator if you need access.

### 22.3 Record Locked

**Title:** Record locked for review  
**Body:** This record is currently being reviewed or approved by another user. You can view the record but cannot make changes until the lock is released.

### 22.4 Workflow Blocked

**Title:** Workflow blocked  
**Body:** This action cannot be completed because required previous steps are incomplete.

### 22.5 File Upload Error

**Title:** File upload failed  
**Body:** The document could not be uploaded. Check the file type and size, then try again.

### 22.6 Duplicate Application Warning

**Title:** Possible duplicate application  
**Body:** This borrower already has an active or pending loan application. Review existing records before creating another application.

---

## 23. Content Governance

### 23.1 Ownership

| Content area | Owner |
|---|---|
| Product labels and UI copy | Product / Business Analyst |
| Legal document templates | Company Secretary |
| Compliance notices | Company Secretary and CFO |
| Loan limit and interest configuration copy | CFO and Credit Manager |
| Notification templates | Product, Credit Manager and Compliance Team |
| Borrower-facing official communication | Company Secretary / authorised business owner |
| Reports and MIS labels | CFO / Accounts Head |
| Help content and training copy | Product and Operations |

### 23.2 Change Control

Changes requiring formal approval:

- Loan limit formula copy.
- Interest rate benchmark or disclosure language.
- Penal interest and fee descriptions.
- Approval matrix wording.
- Security invocation wording.
- Legal document templates.
- Borrower declarations.
- Compliance notices.
- Record retention rules.

Policy-related copy changes must capture:

- Requested change.
- Reason for change.
- Approver.
- Board approval reference where applicable.
- Effective date.
- Version number.

### 23.3 Template Versioning

Generated templates must display:

- Template name.
- Template version.
- Effective date.
- Approval reference where applicable.

Example:

```text
Template: Loan Agreement
Version: 1.0
Effective Date: 07 Aug 2025
```

---

## 24. Localization and Language Guidance

The current content specification is in English. Borrower-facing communication may require Marathi, Hindi or other local language support depending on implementation.

### 24.1 Translation Rules

- Legal terms should be translated only after Company Secretary review.
- Amounts, dates, IDs and names must remain consistent across languages.
- Borrower-facing translations must use simple language.
- System status labels may remain English for internal users unless localization is required.
- SMS messages must be short and avoid legal complexity.

### 24.2 Borrower-Friendly Plain Language

Replace complex internal wording with simpler borrower-facing wording:

| Internal term | Borrower-facing wording |
|---|---|
| Documentation and stamping pending | Some required documents are still pending. |
| Sanction Committee scrutiny | Your application is being reviewed for approval. |
| Interest capitalisation | Unpaid interest has been added to your loan balance. |
| DPD | Loan repayment is overdue. |
| Security invocation | Security may be used for recovery as per loan terms and approvals. |
| Deficiency | Missing or incorrect information. |

---

## 25. Accessibility Content Requirements

- Every icon-only action must have text label or accessible name.
- Status badges must not rely on colour alone; they must include text.
- Error messages must identify the field and the correction needed.
- Required fields must include both visual indicator and text explanation.
- Links must be descriptive, e.g., `View Loan Agreement`, not `Click here`.
- Document upload areas must describe accepted file types and maximum file size.
- Tables must have clear column headings.
- Confirmation modals must state consequences clearly.

---

## 26. Open Content and Policy Issues

These issues must remain visible in product backlog and content governance until client confirmation.

### 26.1 Loan Limit Formula Contradiction

The SOP references:

- 30% of valuation per share.
- 10% of valuation per share.
- Current result of ₹200 per share.

Content requirement:

`Do not hardcode borrower-facing or approval copy until the client confirms the operative policy. Show “Policy confirmation required” in admin and calculation screens.`

### 26.2 Annexure Numbering Conflict

The SOP refers to Annexure K as both Credit Sanction Register and Grievance Form / Complaint-Handling Log.

Content requirement:

`Template names should be shown by document title, not only annexure number, until annexure numbering is corrected.`

### 26.3 Interest Rate Details Missing

The SOP does not define:

- Current interest rate.
- Benchmark.
- Spread.
- Reset frequency.
- Penal interest rate.
- APR method.

Content requirement:

`Use placeholder fields in Term Sheet and Admin Settings and require authorised configuration before document generation.`

### 26.4 Penal Charges and Fees Missing

Content requirement:

`Do not display default charge values unless configured and approved.`

### 26.5 NACH / ECS Ambiguity

Borrower compliance mentions NACH / ECS if required, but repayment process focuses on RTGS / NEFT and subsidiary deduction.

Content requirement:

`Use “NACH / ECS mandate, if applicable” until policy is confirmed.`

### 26.6 Guarantor Ambiguity

Borrower compliance mentions guarantor details if required, but no trigger is defined.

Content requirement:

`Use “Guarantor details, if required by sanction terms” and do not make guarantor mandatory globally.`

### 26.7 Intentional Default Criteria Missing

Content requirement:

`Default review screens must require reason, evidence and classification notes, but criteria should be configured after client policy confirmation.`

---

## 27. Content Acceptance Criteria

Content implementation is acceptable when:

1. All lifecycle stages use the agreed stage names.
2. Every screen has a clear title, purpose and primary action.
3. Every required field has a clear label and validation message.
4. Every blocker explains exactly what is missing and how to fix it.
5. Every rejection, exception and recovery action requires a reason.
6. Approval matrix language matches the SOP thresholds.
7. Documentation content reflects PoA, Tri-party Agreement, SH-4 / CDSL pledge, Term Sheet, Loan Agreement, Bank Verification Letter and Checklist requirements.
8. Disbursement content clearly shows SAP, bank verification and CFC approval gates.
9. Repayment content distinguishes direct repayment and subsidiary deduction.
10. Interest content explains yearly invoices, monthly accruals and 30 April capitalisation rule.
11. Default content follows the three-month grace, non-payment review, one-year extension and recovery approval flow.
12. Closure content includes NOC, security return and 8-year archival.
13. Compliance content covers Producer Company lending, Section 186, NBFC test, KYC / AML, stamp duty, money-lending review, accounting, data protection, recovery conduct, record retention and audit.
14. Open policy issues are not hidden or hardcoded.
15. Generated documents and notifications use approved templates and version control.
16. Audit trail content is factual, timestamped and role-specific.
17. Borrower-facing communication is simple, respectful and non-coercive.
18. Internal workflow communication is precise and action-oriented.

---

## 28. Implementation Notes for Design and Engineering

- Build labels and messages as reusable content tokens where possible.
- Store notification and document templates with versioning.
- Allow role-based message variants where needed.
- All status labels should map to backend state values.
- Validation messages should be centralised to avoid inconsistent wording.
- Generated documents should use the same labels as screens and reports.
- Do not allow admins to edit legal template wording without approval workflow.
- Preserve all generated communication history inside Borrower 360 and Loan Account 360.
- Ensure export column names match report labels in this content specification.
- Ensure all borrower-facing messages include application number or loan account number.
- Ensure all internal task messages include owner, due date and related record.

---

## 29. Final Summary

The content layer of the SFPCL Member Credit Administration & Settlement system must do more than label screens. It must enforce understanding, accountability and compliance across a controlled lending process. Every word should help users answer:

- What record am I looking at?
- What stage is it in?
- What is required now?
- Who owns the next action?
- What rule or policy applies?
- What evidence is required?
- What happens if I approve, reject, send back or proceed?
- What will be recorded for audit?

The system should therefore use precise vocabulary, reason-based decisions, clear status labels, explicit blockers, borrower-friendly communication and version-controlled templates. This content specification should be treated as the single source of truth for UI copy, notification copy, generated document structure and content governance during product design and implementation.
