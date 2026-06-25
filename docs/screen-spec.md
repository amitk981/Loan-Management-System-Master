# screen-spec.md

# SFPCL Member Credit Administration & Settlement — Detailed Screen Specification

## 1. Document Control

| Item | Detail |
|---|---|
| Product / System | SFPCL Member Credit Administration & Loan Management System |
| Document Type | Detailed screen specification |
| Output File | `screen-spec.md` |
| Primary Business Process | Member loan request, appraisal, sanction, documentation, disbursement, repayment, monitoring, default handling and closure |
| Source Basis | Uploaded detailed SOP, WhatsLoan summary deck, client brief, user flows, functional specification and information architecture prepared in the current analysis |
| Intended Readers | Product manager, UX designer, UI designer, engineering team, QA team, implementation team, compliance team and business process owners |
| Primary Organisation | Sahyadri Farmers Producer Company Limited |
| SOP Reference | `SOP_SFPCL_LOANDISBURSEMENT` |
| SOP Version Referenced | Version 1.0, August 2025 |

---

## 2. Purpose of This Screen Specification

This document defines the required screens, page structures, fields, user actions, validations, state behaviours, role permissions and system outputs for a digital system that implements the SFPCL Member Credit Administration and Settlement SOP.

The screen specification converts the process into practical product screens that can be designed and built. It is intentionally detailed so that a product, design or engineering team can understand how the operational SOP should appear and behave in a working application.

The screens described here must support the following full lifecycle:

1. Policy and reference data configuration.
2. Member and borrower identification.
3. Initial loan request.
4. Application completeness checking.
5. KYC and supporting document capture.
6. Active member validation.
7. Loan eligibility assessment.
8. Loan limit calculation.
9. Loan appraisal note preparation.
10. Credit Manager review.
11. Sanction Committee scrutiny.
12. Approval, rejection and exception handling.
13. Special case handling for director / Sanction Committee member / relative borrower.
14. Documentation and stamping.
15. Security document handling, including SH-4 and CDSL pledge.
16. SAP customer code creation request.
17. Loan disbursement initiation and authorisation.
18. Loan account creation and monitoring.
19. Direct repayment and subsidiary-based repayment.
20. Interest accrual, invoicing and capitalisation.
21. DPD monitoring and CFO MIS.
22. Default management, extension and recovery action.
23. Closure, NOC, unpledge and security return.
24. Compliance dashboards, registers and audit trail.

---

## 3. Product Scope Reflected in Screens

## 3.1 In Scope

The screen set covers all major modules required by the SOP:

| Module | Included Screens |
|---|---|
| Dashboard and Work Queues | Role-based dashboard, global search, tasks, alerts and exception queues |
| Member and Borrower Master | Member directory, member profile, borrower 360, nominee, witness, shareholding, land and crop records |
| Loan Origination | New application, application detail, completeness check, deficiency and rejection handling |
| Eligibility and Appraisal | Active member validation, KYC verification, loan limit calculator, appraisal note |
| Sanction | Credit Manager review, Sanction Committee workbench, sanction decision, special approvals |
| Documentation | Document checklist, PoA, tri-party agreement, SH-4, CDSL pledge, term sheet, loan agreement, bank verification letter |
| SAP and Finance Setup | SAP customer code request, customer code confirmation, finance readiness |
| Disbursement | Disbursement initiation, Senior Manager Finance verification, Chief Financial Controller authorisation, disbursement advice |
| Loan Account | Loan account 360, repayment schedule, ledger, statements, outstanding balance |
| Repayment | Direct RTGS / NEFT receipt, subsidiary deduction reconciliation, principal-first allocation |
| Interest | Interest accrual, yearly invoices, unpaid interest capitalisation after 30 April |
| Monitoring | DPD dashboard, quarterly CFO MIS, reminders, ageing reports |
| Default and Recovery | Grace period, reason analysis, extension note, non-payment note, recovery approval, SH-4 / cheque invocation |
| Closure | NOC generation, security return, CDSL unpledge, archival |
| Compliance | Section 186 tracker, NBFC principal business test, KYC / AML tracker, stamp duty register, money-lending annual review, record retention |
| Administration | Policy settings, user roles, approval matrix, templates, audit logs |

## 3.2 Out of Scope Unless Separately Confirmed

The following are not fully defined by the SOP and should be shown as configurable or pending client confirmation:

1. Exact interest benchmark, spread, reset frequency and APR disclosure method.
2. Penal interest rate and fee values.
3. Whether credit bureau checks are mandatory.
4. Whether NACH / ECS mandate is operationally required.
5. Guarantor rules and thresholds.
6. Automated integration with SAP, RBL Bank or CDSL. The base screen spec assumes workflow tracking and document capture; API integration may be added later.
7. Mobile app borrower self-service unless separately prioritised. This spec assumes an internal web application with optional borrower-facing digital intake.
8. Automated e-stamping or notarisation integration.
9. Full legal case management after recovery action.
10. External regulator filing workflows beyond internal compliance tracking.

---

## 4. Design Principles for All Screens

## 4.1 Lifecycle-First Design

Every loan record should be organised around its lifecycle stage. Users should always be able to see where the loan currently is, what has already happened, what is pending and who owns the next action.

Recommended stage stepper:

```text
Application -> Completeness -> Appraisal -> Sanction -> Documentation -> SAP Setup -> Disbursement -> Active Loan -> Monitoring -> Closure
```

For defaulted loans, an additional overlay state should appear:

```text
Normal -> Overdue -> Grace Period -> Extension -> Non-Payment Review -> Recovery Action -> Closed / Written Off / Resolved
```

## 4.2 Control Gates Must Be Visible

The SOP has strict controls. Screens must not hide these controls. A user should see explicit blockers such as:

- Non-member applicant.
- Inactive member.
- Missing PAN / Aadhaar.
- Missing nominee signature.
- Minor nominee.
- Missing 7/12 extract.
- Missing crop plan.
- Missing six-month bank statement.
- Loan purpose not agriculture / crop production.
- Requested amount exceeding eligible limit.
- Documentation not stamped.
- Loan Agreement not notarised.
- SH-4 missing for physical shares.
- CDSL pledge incomplete for demat shares.
- SAP customer code not created.
- Bank account not verified.
- Sanction approval missing.
- Special case approval missing.

## 4.3 Registers Should Be Generated Views

The SOP refers to several registers. In the digital system, these should be structured views generated from underlying records, not separately maintained duplicate spreadsheets.

Registers include:

- Loan Request Register.
- Credit Sanction Register.
- Exception Register.
- Security Register.
- Stamp Duty Register.
- KYC / CKYC Register.
- Grievance Register.
- Recovery Log.
- Archive Register.

## 4.4 One Source of Truth Per Loan

Every screen should connect back to a single Loan Application ID and Loan Account ID.

Key identifiers:

| Identifier | Description |
|---|---|
| Application Reference Number | Starts at `LO00000001` and increments sequentially. Assigned after completeness check. |
| Member ID / Folio Number | Identifies the shareholder / member. |
| SAP Customer Code | Created or confirmed before disbursement. |
| Loan Account Number | Created after disbursement. May be same as or derived from Application Reference Number. |
| Security Reference | SH-4 reference or CDSL Pledge Sequence Number. |

## 4.5 Role-Specific Workspaces

Screens should show only the tasks relevant to the logged-in role, while still allowing authorised users to see the overall loan context.

Role examples:

- Deputy Manager - Finance: application completeness and appraisal preparation.
- Credit Manager: review, rejection, appraisal finalisation, loan register, repayment monitoring.
- Company Secretary: documentation, stamping, PoA, SH-4, compliance evidence.
- Compliance Team Member: document preparation and checklist management.
- Sanction Committee: sanction decisions and exception approvals.
- CFO: approvals, MIS, statutory compliance monitoring.
- Senior Manager - Finance: SAP request, disbursement verification and payment initiation.
- Chief Financial Controller: final bank transfer approval.
- Accounts Team: repayment entries, accruals, invoices and DPD reports.
- Internal Auditor: read-only access to complete audit trails and documents.

---

## 5. Global Screen Components

These components should be reused across the system.

## 5.1 Global Header

| Element | Behaviour |
|---|---|
| SFPCL logo / product name | Navigates to dashboard. |
| Global search | Search by borrower name, application number, loan account number, folio number, Aadhaar last four digits, PAN, SAP customer code, mobile number or security reference. |
| Notification bell | Shows pending approvals, deficiencies, expiring TATs, overdue loans, compliance alerts. |
| User profile | Shows role, team, branch / office if applicable, and logout. |
| Help / SOP reference | Opens contextual guidance or SOP extracts where configured. |

## 5.2 Left Navigation

Recommended top-level navigation:

1. Dashboard.
2. Applications.
3. Members & Borrowers.
4. Appraisal.
5. Sanction.
6. Documentation.
7. SAP & Disbursement.
8. Loan Accounts.
9. Repayments.
10. Monitoring & Defaults.
11. Compliance.
12. Reports.
13. Settings.
14. Audit & Archive.

Navigation should be role-filtered.

## 5.3 Page Header Pattern

Every primary detail screen should include:

| Field | Description |
|---|---|
| Page title | Example: `Loan Application LO00000047` |
| Borrower name | Individual farmer or FPC name |
| Member type | Individual / FPC / Producer Institution |
| Current status | Status badge |
| Current owner | Role or user responsible for next action |
| TAT timer | Shows elapsed and remaining time where applicable |
| Critical flags | Exceptions, director-related borrower, overdue, high risk, documentation blocker |
| Primary action | Context-specific next action |
| Secondary actions | Save draft, download, request clarification, reject, view audit trail |

## 5.4 Status Badge System

Recommended status categories:

| Category | Example Values |
|---|---|
| Application | Draft, Submitted, Incomplete, Reference Generated, Appraisal Pending |
| Eligibility | Pending, Eligible, Ineligible, Exception Required |
| Sanction | Pending Review, Approved, Rejected, Special Approval Required |
| Documentation | Not Started, In Preparation, Pending Signature, Pending Stamping, Pending Notary, Complete |
| SAP | Not Requested, Requested, Code Created, Code Reused, Error |
| Disbursement | Pending Verification, Payment Initiated, Awaiting CFC Approval, Disbursed, Failed |
| Loan | Active, Fully Repaid, Closed, Overdue, Grace Period, Extension, Recovery Review |
| Compliance | Compliant, Warning, Breach, Pending Board Approval |

## 5.5 Stage Stepper

Every application and loan detail screen should include a stage stepper. Completed stages should show date and responsible role.

Example:

| Stage | Display Detail |
|---|---|
| Application | Submitted by Credit Assessment Team on date |
| Completeness | Verified by Deputy Manager - Finance |
| Appraisal | Prepared by Deputy Manager - Finance and reviewed by Credit Manager |
| Sanction | Approved / rejected by Sanction Committee |
| Documentation | Verified by Company Secretary |
| SAP Setup | Customer code created / reused |
| Disbursement | Payment approved by CFC |
| Monitoring | Active loan, repayment due dates |
| Closure | NOC issued and securities returned |

## 5.6 Audit Trail Drawer

Every screen that changes data must provide an audit trail.

Audit fields:

- Timestamp.
- User name.
- User role.
- Action performed.
- Before value.
- After value.
- Comment / reason.
- Linked document version.
- IP / device metadata if available.

Actions requiring mandatory reason:

- Rejection.
- Exception approval.
- Change in eligible amount.
- Override of system-calculated value.
- Special case approval.
- Document waiver.
- Extension approval.
- Recovery action.
- Closure before all checklist items complete.

## 5.7 Document Viewer

Screens with documents should use a standard document viewer with:

- File preview.
- Download.
- Version history.
- Upload new version.
- Mark as verified.
- Reject document with reason.
- Signature status.
- Stamp status.
- Notary status.
- Physical original custody location.
- Linked checklist item.

## 5.8 Notification Pattern

Notifications should be generated for:

- Application reference generated.
- Deficiency identified.
- Rejection note issued.
- Appraisal submitted to Sanction Committee.
- Sanction approved / rejected.
- Documentation pending.
- Signature mismatch detected.
- SAP customer code request sent.
- SAP customer code created.
- Payment initiated.
- Payment approved and disbursed.
- Repayment received.
- Interest invoice generated.
- Interest unpaid after 30 April and capitalised.
- Loan overdue.
- Grace period started.
- Extension note required.
- Non-payment note sent to Sanction Committee.
- Recovery action approved.
- Loan fully repaid.
- NOC issued.
- SH-4 / cheque returned.

Notification channels to support:

- In-app notification.
- Email.
- SMS, where borrower-facing.
- Hard-copy letter tracking, where required by SOP.

---

## 6. Role and Permission Matrix at Screen Level

| Role | View | Create | Edit | Approve | Reject | Upload Docs | Disburse | Compliance Admin |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Borrower / Member | Own application only | Limited self-application if enabled | Own draft only | No | No | Own documents if portal enabled | No | No |
| Deputy Manager - Finance | Assigned applications | Yes | Application and appraisal draft | No | No | Yes | No | No |
| Credit Manager | Applications, appraisal, loan register | Yes | Eligibility, appraisal, rejection notes, monitoring notes | Review / recommend | Yes at credit assessment stage | Yes | No | Limited |
| Compliance Team Member | Documentation workspace | Document records | Documentation fields | No | Document rejection only | Yes | No | Limited |
| Company Secretary | Documentation, compliance, registers | Compliance records | Legal document status, stamp duty, security custody | Documentation approval | Documentation blocker | Yes | No | Yes |
| Sanction Committee Member | Sanction cases | No | Comments only | Yes | Yes | No | No | No |
| CFO | Approvals, MIS, compliance | No | Comments, exception decisions | Yes | Yes | No | No | Yes |
| Senior Manager - Finance | SAP and disbursement | SAP request / finance task | Finance status, disbursement initiation | Checklist signature after disbursement | Block disbursement | Finance docs | Initiate | No |
| Chief Financial Controller | Payment approvals | No | Payment comments | Final bank transfer approval | Reject / return payment | No | Authorise | No |
| Accounts Team | Loan accounts, repayments, invoices | Repayment and invoice records | Ledger entries | No | No | Payment evidence | No | No |
| IT Head / Admin | System settings | Users / roles | System settings | No | No | No | No | Technical only |
| Internal Auditor | All records read-only | No | No | No | No | No | No | Audit review only |

---

## 7. Screen Inventory

| ID | Screen Name | Module | Primary Users |
|---|---|---|---|
| S00 | Login / Access Landing | Access | All users |
| S01 | Role-Based Dashboard | Dashboard | All internal users |
| S02 | Global Search Results | Dashboard | All authorised users |
| S03 | Task Inbox | Dashboard | All internal users |
| S04 | Notifications and Alerts Center | Dashboard | All internal users |
| S05 | Member Directory | Members | Credit, Compliance, Accounts, Auditors |
| S06 | Member Profile | Members | Credit, Compliance, Accounts |
| S07 | Borrower 360 | Members / Loan Accounts | Credit, Sanction, Finance, Accounts |
| S08 | Nominee Detail Panel | Members | Credit, Compliance |
| S09 | Witness Detail Panel | Documentation | Compliance, CS |
| S10 | New Loan Application | Applications | Deputy Manager - Finance, Credit Manager, Borrower portal if enabled |
| S11 | Application Draft Review | Applications | Deputy Manager - Finance, Credit Manager |
| S12 | Application Completeness Check | Applications | Deputy Manager - Finance |
| S13 | Loan Request Register | Applications | Credit Manager, Auditors |
| S14 | Deficiency / Rejection Note Builder | Applications | Credit Manager |
| S15 | Eligibility Assessment | Appraisal | Deputy Manager - Finance, Credit Manager |
| S16 | Active Member Verification | Appraisal | Credit Manager |
| S17 | KYC Verification | Appraisal / Compliance | Credit, Compliance |
| S18 | Loan Limit Calculator | Appraisal | Credit Manager |
| S19 | Loan Appraisal Note | Appraisal | Deputy Manager - Finance, Credit Manager |
| S20 | Credit Manager Review | Appraisal | Credit Manager |
| S21 | Sanction Committee Workbench | Sanction | CFO, Directors |
| S22 | Sanction Case Detail | Sanction | Sanction Committee |
| S23 | Credit Sanction Register | Sanction | Sanction Committee, CS, Auditors |
| S24 | Special Case Approval | Sanction | Sanction Committee, CFO, CS |
| S25 | Exception Register | Sanction / Compliance | CFO, CS, Credit Manager |
| S26 | Documentation Workspace | Documentation | Compliance Team, CS |
| S27 | Document Checklist | Documentation | Compliance, CS, Credit, Sanction, Finance |
| S28 | Power of Attorney Screen | Documentation | Compliance, CS |
| S29 | Tri-Party Agreement Screen | Documentation | Compliance, CS |
| S30 | SH-4 Physical Share Security Screen | Documentation / Security | Compliance, CS |
| S31 | CDSL Pledge Screen | Documentation / Security | Compliance, CS |
| S32 | Term Sheet Screen | Documentation | Compliance, CFO, Directors |
| S33 | Loan Agreement Screen | Documentation | Compliance, CS |
| S34 | Bank Verification / Signature Mismatch Screen | Documentation | Credit, Compliance |
| S35 | Final Documentation Approval Screen | Documentation | CS, Credit Manager, Sanction Committee, Senior Manager - Finance |
| S36 | SAP Customer Code Request | SAP & Finance | Credit Manager, Senior Manager - Finance |
| S37 | SAP Customer Code Confirmation | SAP & Finance | Senior Manager - Finance |
| S38 | Disbursement Readiness Review | Disbursement | Senior Manager - Finance |
| S39 | Payment Initiation Screen | Disbursement | Senior Manager - Finance |
| S40 | CFC Payment Authorisation Screen | Disbursement | Chief Financial Controller |
| S41 | Disbursement Advice Screen | Disbursement | Treasury, Credit |
| S42 | Loan Account 360 | Loan Account | Credit, Accounts, Finance, CFO |
| S43 | Repayment Schedule Screen | Loan Account | Credit, Accounts |
| S44 | Direct Repayment Entry | Repayments | Accounts, Credit |
| S45 | Subsidiary Deduction Reconciliation | Repayments | Treasury, Accounts |
| S46 | Loan Ledger | Loan Account | Accounts, Credit, Auditors |
| S47 | Interest Accrual Screen | Interest | Accounts, Credit Manager |
| S48 | Yearly Interest Invoice Screen | Interest | Sales Team, Accounts, Credit Manager |
| S49 | Interest Capitalisation Screen | Interest | Accounts, Credit Manager |
| S50 | Monitoring Dashboard | Monitoring | Credit Manager, CFO |
| S51 | DPD / Portfolio at Risk Screen | Monitoring | Credit, CFO, Accounts |
| S52 | Reminder Management Screen | Monitoring | Credit Manager |
| S53 | Default Case Detail | Default | Credit, Sanction, CFO |
| S54 | Grace Period and Extension Screen | Default | Credit Manager, CFO |
| S55 | Note for Non-Payment Screen | Default | Credit Assessment Team, Sanction Committee |
| S56 | Recovery Action Approval Screen | Default / Recovery | Sanction Committee, CFO, CS |
| S57 | Security Invocation Screen | Recovery | CS, Compliance, CFO |
| S58 | Loan Closure Screen | Closure | Accounts, Credit, Compliance |
| S59 | NOC Generation Screen | Closure | Compliance, CS |
| S60 | Security Return / Unpledge Screen | Closure | Compliance, CS |
| S61 | Archive Screen | Closure / Audit | CS, Auditor |
| S62 | Compliance Dashboard | Compliance | CFO, CS, Compliance, Auditor |
| S63 | Section 186 Limit Tracker | Compliance | CFO, Accounts |
| S64 | NBFC Principal Business Test | Compliance | CFO, Accounts |
| S65 | KYC / AML and Re-KYC Tracker | Compliance | Credit Head, Compliance |
| S66 | Stamp Duty Register | Compliance | CS |
| S67 | Money-Lending Annual Review | Compliance | CS |
| S68 | Grievance Register | Compliance | CS, Credit Head |
| S69 | Reports and MIS Center | Reports | CFO, Credit, Accounts, Auditors |
| S70 | Policy and Product Configuration | Settings | Admin, CFO, CS |
| S71 | Approval Matrix Settings | Settings | Admin, CFO, CS |
| S72 | Template Management | Settings | Compliance, CS, Admin |
| S73 | User and Role Management | Settings | Admin |
| S74 | Audit Log Explorer | Audit | Auditor, Admin, CS |

---

# 8. Detailed Screen Specifications

## S00 — Login / Access Landing

### Purpose

Allow authorised internal users to access the loan management system securely.

### Primary Users

All internal users.

### Layout

1. SFPCL logo and product name.
2. Login form or single sign-on entry.
3. User ID / email.
4. Password or SSO button.
5. Forgot password link.
6. Support contact link.
7. Environment label for staging / production.

### Functional Requirements

- Support role-based routing after login.
- Show last login time after successful login.
- Lock account after configured failed attempts.
- Enforce multi-factor authentication if enabled.
- Maintain login audit trail.

### Validations

- User must be active.
- User must have at least one mapped role.
- User must not be suspended.

### Post-Login Routing

| Role | Default Landing |
|---|---|
| Deputy Manager - Finance | Task Inbox: Applications pending completeness / appraisal |
| Credit Manager | Dashboard: application pipeline and monitoring alerts |
| Compliance Team | Documentation Workspace |
| Company Secretary | Documentation and Compliance Dashboard |
| Sanction Committee | Sanction Committee Workbench |
| Senior Manager - Finance | SAP and Disbursement Queue |
| Chief Financial Controller | Payment Authorisation Queue |
| Accounts Team | Repayment and Interest Work Queue |
| CFO | Executive Dashboard |
| Auditor | Audit Log / Reports Center |

---

## S01 — Role-Based Dashboard

### Purpose

Provide a single landing page showing the current workload, stage distribution, risks, exceptions, approvals and compliance alerts for the logged-in user.

### Core Components

1. Welcome header.
2. Role-specific task cards.
3. Lifecycle funnel.
4. Overdue and TAT alerts.
5. Approval queue.
6. Documentation blockers.
7. Disbursement blockers.
8. Portfolio monitoring summary.
9. Compliance alerts.
10. Recent activity.

### Common Dashboard Metrics

| Metric | Description |
|---|---|
| New applications received | Count of submitted applications pending completeness check. |
| Applications incomplete | Count of applications returned for deficiencies. |
| Appraisals pending | Count requiring Loan Appraisal Note preparation or review. |
| Sanctions pending | Count waiting for Sanction Committee decision. |
| Documentation pending | Count approved but not documentation-complete. |
| SAP setup pending | Count waiting for SAP customer code request or confirmation. |
| Disbursement pending | Count documentation-complete but not yet paid. |
| Active loans | Count of disbursed loans not closed. |
| Overdue loans | Count with missed scheduled repayment. |
| Loans in grace period | Count within three-month extension after missed repayment. |
| Loans in extension | Count granted one-year non-intentional default extension. |
| Closure pending | Count fully repaid but NOC / security return pending. |

### Role-Specific Cards

#### Credit Manager Dashboard

- Applications awaiting review.
- Appraisals nearing 2-day TAT breach.
- Ineligible applications requiring rejection note.
- Loans exceeding eligible limits.
- Quarterly DPD status.
- Reminder calls / SMS due.
- Re-KYC due cases.

#### Company Secretary Dashboard

- Documentation files pending preparation.
- Stamp duty pending.
- PoA notarisation pending.
- SH-4 custody pending.
- CDSL pledge pending.
- NOC pending.
- Security return pending.
- Compliance review alerts.

#### Sanction Committee Dashboard

- Cases awaiting approval.
- Cases above ₹5 lakh requiring CFO + two Directors.
- Cases exceeding permissible loan limit.
- Director / relative borrower cases.
- Rejected cases pending communication.

#### Senior Manager - Finance Dashboard

- SAP code requests pending.
- SAP confirmation pending.
- Disbursement readiness review pending.
- Payment initiation pending.
- Failed bank transfers.

#### Chief Financial Controller Dashboard

- Bank transfers awaiting authorisation.
- High-value payments.
- Returned payment requests.

#### CFO Dashboard

- Portfolio outstanding.
- Loans by DPD bucket.
- Exceptions by type.
- Section 186 utilisation.
- NBFC principal business test ratios.
- Quarterly MIS readiness.
- Loans above ₹5 lakh.
- Recovery action approvals.

### Actions

- Open task.
- Filter dashboard by date range, role, status and loan amount.
- Export dashboard summary.
- Open exception list.
- Open overdue list.

### Empty States

- “No pending tasks for your role.”
- “No compliance alerts.”
- “No overdue loans in the selected period.”

---

## S02 — Global Search Results

### Purpose

Allow authorised users to find members, applications, loan accounts, documents and registers quickly.

### Search Inputs

Search should support:

- Borrower name.
- FPC name.
- Application reference number.
- Loan account number.
- Folio number.
- Number of shares.
- PAN.
- Aadhaar last four digits.
- Mobile number.
- Email.
- SAP Customer Code.
- Cheque number.
- CDSL Pledge Sequence Number.
- SH-4 reference.
- Bank account last four digits.

### Result Grouping

Results should be grouped by:

1. Members.
2. Loan Applications.
3. Loan Accounts.
4. Documents.
5. Repayments.
6. Compliance records.
7. Audit logs, for authorised users.

### Result Card Fields

| Field | Description |
|---|---|
| Title | Borrower name / application / loan account |
| Identifier | Application number, folio number, SAP code |
| Status | Current stage and risk status |
| Amount | Requested / sanctioned / outstanding amount if applicable |
| Owner | Current workflow owner |
| Last updated | Date and user |
| Quick action | Open, view documents, view loan account |

### Permissions

Search results must be permission-filtered. A user should not see records outside their authorised role scope.

---

## S03 — Task Inbox

### Purpose

Provide each user with a list of actionable items assigned to them or their role.

### Columns

| Column | Description |
|---|---|
| Task ID | System-generated task reference |
| Task type | Completeness check, appraisal, sanction, document verification, SAP setup, disbursement, repayment posting, default review |
| Application / Loan ID | Linked record |
| Borrower | Borrower name |
| Amount | Requested / sanctioned / outstanding amount |
| Priority | Normal, High, Critical |
| SLA / TAT | Remaining time or overdue days |
| Current status | Stage state |
| Assigned to | User / role |
| Created date | Task creation date |
| Due date | System calculated |
| Action | Open task |

### Filters

- Task type.
- Due today.
- Overdue.
- Borrower type.
- Amount threshold.
- Special case.
- Exception required.
- Assigned to me.
- Assigned to my team.

### Actions

- Open.
- Reassign, where permitted.
- Add comment.
- Mark blocked.
- Export.

---

## S04 — Notifications and Alerts Center

### Purpose

Centralise system alerts, borrower communications, internal notifications and compliance reminders.

### Notification Categories

| Category | Examples |
|---|---|
| Application | Application submitted, incomplete, reference generated |
| Appraisal | TAT breach warning, appraisal submitted |
| Sanction | Approval pending, approved, rejected |
| Documentation | Signature pending, stamp pending, mismatch found |
| Disbursement | SAP pending, payment initiated, disbursed |
| Repayment | Repayment received, interest invoice generated |
| Monitoring | Overdue, DPD bucket change, reminder due |
| Default | Grace period started, extension note due, recovery approval required |
| Compliance | Section 186 threshold, NBFC test warning, re-KYC due |

### Fields

- Notification title.
- Linked record.
- Severity.
- Timestamp.
- Sender / system.
- Recipient.
- Read / unread.
- Action button.

### Actions

- Mark as read.
- Open linked record.
- Snooze reminder.
- Dismiss, where permitted.

---

## S05 — Member Directory

### Purpose

Provide a searchable list of SFPCL members who may be eligible borrowers.

### Columns

| Column | Description |
|---|---|
| Member ID | Internal member identifier |
| Folio Number | Folio number of shares held |
| Name | Individual farmer / FPC / Producer Institution |
| Member Type | Individual / FPC / Producer Institution |
| Active Status | Active / Inactive / Pending verification |
| Share Count | Number of shares held |
| Shareholding Mode | Physical / Demat / Mixed |
| Produce Supply Status | Four-year condition met / one-year relaxation / not met |
| Services Availed | Yes / No / Unknown |
| Default Status | No default / Existing default / Past default |
| KYC Status | Complete / Missing / Re-KYC Due |
| Open Loans | Count and total outstanding |
| Last Updated | Date |

### Filters

- Member type.
- Active / inactive.
- Shareholding mode.
- KYC status.
- Default status.
- Crop.
- Land area range.
- Producer institution.
- Subsidiary-linked borrower.

### Actions

- View profile.
- Start loan application.
- Update member details, where authorised.
- Export member list.

### Validations

- Start loan application should be blocked or warn if:
  - Member is inactive.
  - KYC is missing.
  - Existing default exists.
  - Member has no shareholding data.

---

## S06 — Member Profile

### Purpose

Show the complete member record used for eligibility and loan processing.

### Tabs

1. Overview.
2. Shareholding.
3. Produce Supply History.
4. Services Availed.
5. KYC.
6. Land and Crop Evidence.
7. Loans.
8. Nominee.
9. Communications.
10. Audit Trail.

### Overview Fields

| Field | Description |
|---|---|
| Member name | Full legal name |
| Member type | Individual / FPC / Producer Institution |
| Folio number | Required for loan application |
| Date of membership | Membership start date |
| Active status | Derived from AoA active member rules |
| Active status reason | Explanation of qualification or failure |
| Share count | Number of shares held |
| Share valuation applied | Latest valuation used for loan limit |
| Current loan exposure | Outstanding principal and interest |
| Default flag | Current default status |
| Contact details | Mobile, email, address |

### Shareholding Tab

Fields:

- Number of shares.
- Folio number.
- Physical shares count.
- Demat shares count.
- Share certificate copies.
- Demat BO account details, if available.
- Latest valuation per share.
- Board-approved loan percentage.
- Derived per-share loan value.
- Future share pledge flag.

### Produce Supply History Tab

Fields:

- Financial year.
- Crop supplied.
- Quantity.
- Supplied to SFPCL / subsidiary / step-down subsidiary / through Producer Institution.
- Invoice or procurement reference.
- Counts toward active member status: Yes / No.

### Services Availed Tab

Fields:

- Service type.
- Crop production.
- Procurement.
- Purchase / sale of agricultural inputs.
- Agronomy service.
- Date.
- Entity providing service.

### Land and Crop Evidence Tab

Fields:

- 7/12 extract document.
- Land area under cultivation.
- Crop plan.
- Crop type.
- Season.
- Per-acre scale of finance.
- Land-based eligible amount.

### Actions

- Start application.
- Update KYC.
- Upload document.
- Mark active status verified.
- View all loans.
- View audit trail.

---

## S07 — Borrower 360

### Purpose

Provide a consolidated view of a borrower across membership, loan applications, documents, repayments, defaults and communications.

### Header

- Borrower name.
- Member type.
- Folio number.
- Active member status.
- KYC status.
- Default status.
- Total outstanding.
- Open application count.
- SAP customer code.

### Sections

1. Borrower profile summary.
2. Current applications.
3. Active loans.
4. Historical loans.
5. Repayment history.
6. Outstanding interest.
7. Security instruments held.
8. Documentation status.
9. Communications log.
10. Risk and exceptions.

### Key Actions

- Open latest application.
- Open loan account.
- Initiate new application.
- Generate statement.
- Add borrower communication.
- View security custody.

### Use Cases

- Sanction Committee reviews borrowing history.
- Credit Manager checks defaults before appraisal.
- Accounts verifies repayment patterns.
- Compliance checks document completeness.

---

## S08 — Nominee Detail Panel

### Purpose

Capture and validate nominee information required at application and documentation stages.

### Fields

| Field | Required | Validation |
|---|---:|---|
| Nominee full name | Yes | Text |
| Age | Yes | Must not indicate minor status; nominee should not be a minor |
| Date of birth | Recommended | Used to calculate age |
| Gender | Yes | Configured values |
| Aadhaar number | Yes | Masked display after entry |
| PAN | Yes | PAN format validation |
| Relationship to borrower | Recommended | Dropdown |
| Mobile number | Recommended | Mobile format |
| Address | Recommended | Text |
| PAN document | Yes | Upload and self-attested flag |
| Aadhaar document | Yes | Upload and self-attested flag |
| Signature status | Yes for documents | Signed / Pending / Not applicable |

### Validations

- Nominee cannot be a minor.
- PAN and Aadhaar copies must be uploaded.
- Nominee must sign application, PoA and Term Sheet where required.
- Missing nominee data blocks application submission or documentation completion depending on stage.

---

## S09 — Witness Detail Panel

### Purpose

Capture witness information for loan documentation.

### Fields

| Field | Required | Notes |
|---|---:|---|
| Witness name | Yes | Must be existing SFPCL shareholder |
| Witness member / folio number | Yes | Used to validate shareholder status |
| PAN copy | Yes | Upload |
| Aadhaar copy | Yes | Upload |
| Address | Recommended | Text |
| Mobile | Recommended | Text |
| Signature captured | Yes | Required for SH-4 / Loan Agreement as applicable |
| Witness verification status | Yes | Pending / Verified / Rejected |

### Validation

- Witness must be an existing shareholder of SFPCL.
- Documentation cannot complete until witness verification is marked complete.

---

## S10 — New Loan Application

### Purpose

Capture a new loan request from an eligible member / shareholder / FPC.

### Entry Points

- Member Directory -> Start Loan Application.
- Borrower 360 -> New Application.
- Applications -> New Application.
- Borrower portal, if enabled.

### Screen Sections

1. Applicant identification.
2. Shareholding details.
3. Requested loan details.
4. Nominee details.
5. Purpose of loan.
6. Documents upload.
7. Declarations.
8. Review and submit.

### Applicant Fields

| Field | Required | Notes |
|---|---:|---|
| Applicant type | Yes | Individual farmer / FPC / Producer Institution |
| Borrower name | Yes | Auto-populated if selected from member master |
| Folio number | Yes | Required by SOP |
| Member ID | Yes | System field |
| Contact number | Yes | For communications |
| Email | Recommended | Required for email notifications if available |
| Address | Yes | From member master; editable with permission |
| PAN | Yes | From KYC or entered |
| Aadhaar | Yes for individual | Masked after entry |

### Shareholding Fields

| Field | Required | Notes |
|---|---:|---|
| Number of shares held | Yes | Used for loan limit calculation |
| Shareholding mode | Yes | Physical / Demat / Mixed |
| Share certificate copy | Required for physical shares | Upload |
| Demat BO details | Required for demat shares | Used for CDSL pledge workflow |
| Latest valuation per share | System | From policy configuration |
| Current per-share loan value | System | Must reflect confirmed formula |

### Loan Request Fields

| Field | Required | Notes |
|---|---:|---|
| Required loan amount | Yes | Must be numeric and positive |
| Loan purpose | Yes | Must relate to crop production / agriculture activity only |
| Crop | Yes | Dropdown from configured crops |
| Season / cycle | Recommended | For crop plan alignment |
| Expected repayment date | Recommended | May be derived from product / schedule |
| Loan type requested | Optional | Short-term / long-term if known |
| Subsidiary repayment linkage | Optional / Conditional | Required if repayment via subsidiary expected |

### Nominee Fields

Include fields from S08.

### Required Documents Upload

| Document | Required For | Notes |
|---|---|---|
| Borrower PAN | All borrowers | Self-attested copy |
| Borrower Aadhaar | Individual borrowers | Self-attested copy |
| Nominee PAN | All applications with nominee | Self-attested copy |
| Nominee Aadhaar | All applications with nominee | Self-attested copy |
| Share certificates | Physical shareholding | Copy required |
| 7/12 extract | Agricultural land evidence | Land document |
| Crop plan | All agriculture loans | Purpose validation |
| Bank statement | All borrowers | Latest six months |

### Declarations

Borrower must confirm:

- Loan purpose is related to crop production and agriculture activity.
- Submitted documents are true and complete.
- Borrower agrees to loan sanction terms as per Term Sheet and Loan Agreement.
- Borrower is not in default with SFPCL, subsidiary or associate company.
- Borrower consents to KYC / CKYC checks and other verification where applicable.

### Actions

- Save draft.
- Submit application.
- Cancel.
- Upload documents.
- Validate member.
- Preview application.

### Submission Validations

- Applicant must be a member.
- Applicant must have folio number.
- Required loan amount must be present.
- Loan purpose must be agriculture / crop production.
- Nominee details must be complete and nominee must not be a minor.
- Mandatory KYC documents must be uploaded.
- Bank statement must cover six months or be flagged deficient.

### Output

- Draft application ID before formal reference generation.
- Submitted application pending completeness check.

---

## S11 — Application Draft Review

### Purpose

Allow the Deputy Manager - Finance or Credit Manager to review a draft application before it enters completeness check.

### Display

- Application summary.
- Borrower summary.
- Document checklist.
- Missing fields panel.
- Validation warnings.
- Duplicate application warning.

### Duplicate Checks

System should check:

- Existing open application for same borrower.
- Existing outstanding loan.
- Same requested amount and same purpose recently submitted.
- Same bank account used in other active borrower records.

### Actions

- Return to draft.
- Submit for completeness check.
- Delete draft, if not submitted and user has permission.

---

## S12 — Application Completeness Check

### Purpose

Verify that the submitted application is complete before generating the official loan application reference number.

### Primary Actor

Deputy Manager - Finance.

### Screen Sections

1. Application details.
2. Mandatory field checklist.
3. Mandatory document checklist.
4. Nominee validation.
5. Deficiencies panel.
6. Reference number generation.

### Checklist Items

| Item | Required Outcome |
|---|---|
| Loan Application Form present | Yes |
| Applicant signature present | Yes |
| Nominee signature present | Yes |
| Folio number present | Yes |
| Number of shares present | Yes |
| Required loan amount present | Yes |
| Nominee name, age, Aadhaar, PAN and gender present | Yes |
| Borrower PAN and Aadhaar uploaded | Yes |
| Nominee PAN and Aadhaar uploaded | Yes |
| Share certificate uploaded if physical | Yes |
| 7/12 extract uploaded | Yes |
| Crop plan uploaded | Yes |
| Six-month bank statement uploaded | Yes |

### Actions

- Mark item complete.
- Mark item deficient with reason.
- Generate reference number.
- Return application for deficiency.
- Add internal comment.

### Reference Number Behaviour

When all mandatory completeness checks pass, system generates the official reference number sequentially:

```text
LO00000001, LO00000002, LO00000003...
```

### Output

- Loan Request Register entry created.
- Application status changes to `Reference Generated`.
- Borrower notified of reference number where communication details exist.
- Application moves to appraisal stage.

### Deficiency Flow

If incomplete:

- User selects deficiency reasons.
- System generates deficiency / rejection communication.
- Application status becomes `Incomplete - Returned to Applicant` or `Rejected at Completeness`, depending on business decision.
- Borrower may resubmit after rectification.

---

## S13 — Loan Request Register

### Purpose

Digital replacement for the Excel Loan Request Register maintained by the Credit Manager.

### Columns

| Column | Description |
|---|---|
| Application Reference Number | `LO00000001` sequence |
| Date received | Application receipt date |
| Reference generated date | Completeness pass date |
| Borrower name | Farmer / FPC |
| Folio number | Shareholder folio |
| Member type | Individual / FPC / Producer Institution |
| Number of shares | Used for loan limit |
| Requested amount | Loan requested |
| Purpose | Agriculture / crop production description |
| Current stage | Lifecycle stage |
| Current owner | Role / user |
| Eligibility status | Pending / Eligible / Ineligible |
| Sanction status | Pending / Approved / Rejected |
| Documentation status | Pending / Complete |
| Disbursement status | Pending / Disbursed |
| Last updated | Timestamp |

### Filters

- Date range.
- Borrower type.
- Status.
- Amount range.
- Pending owner.
- Rejected applications.
- Applications exceeding limit.

### Actions

- Open application.
- Export to Excel / PDF.
- View audit trail.

### Permissions

- Credit Manager owns register.
- Auditors and CFO can view.
- Other roles see filtered view as authorised.

---

## S14 — Deficiency / Rejection Note Builder

### Purpose

Generate formal rejection or deficiency notes for incomplete or ineligible applications.

### Actors

Credit Manager primarily. Deputy Manager - Finance may initiate deficiency list for completeness stage.

### Fields

| Field | Description |
|---|---|
| Borrower name | Auto-populated |
| Application reference | Auto-populated if generated |
| Stage of rejection | Completeness / Credit Assessment / Sanction Committee |
| Reason category | Missing document, eligibility failure, default, purpose mismatch, limit issue, committee rejection, other |
| Detailed reason | Mandatory free text |
| Required corrective action | What borrower must do before reapplying |
| Reapply allowed | Yes / No / After condition |
| Communication mode | Email / courier / hard copy / SMS summary |
| Approver / sign-off | Credit Manager or applicable authority |

### Common Rejection Reasons

- Applicant is not an active member.
- Applicant is not a member.
- Applicant is in default with SFPCL / subsidiary / associate company.
- Missing PAN or Aadhaar.
- Missing nominee documents.
- Nominee is a minor.
- Missing land documents.
- Missing crop plan.
- Missing six-month bank statement.
- Loan purpose is not agriculture / crop production.
- Requested loan amount exceeds limit and exception is not approved.
- Sanction Committee rejected after scrutiny.

### Actions

- Save draft note.
- Preview note.
- Approve note.
- Send by email.
- Mark courier dispatched.
- Upload signed / scanned copy.

### Output

- PDF rejection / deficiency note.
- Communication log entry.
- Application status updated.

---

## S15 — Eligibility Assessment

### Purpose

Determine whether the applicant is eligible for a loan according to SOP criteria.

### Actors

Deputy Manager - Finance prepares; Credit Manager reviews.

### Sections

1. Member status.
2. Active member status.
3. Default status.
4. Documentation status.
5. Purpose validation.
6. Term acceptance.
7. Eligibility decision.

### Eligibility Checklist

| Criterion | System Behaviour |
|---|---|
| Applicant must be active member | Pull from active member verification screen; allow manual verification with evidence |
| Applicant must not be in default | Check active and historical loans across SFPCL, subsidiaries and associates where data exists |
| Land documents submitted | Check 7/12 extract upload |
| KYC submitted | Check borrower and nominee KYC completeness |
| Recent bank statement submitted | Check uploaded bank statement covers six months |
| Crop plan submitted | Check document upload and crop selection |
| Agrees to terms | Capture declaration |
| Purpose is agriculture / crop production only | Validate selected purpose category |

### Outcome Values

- Eligible.
- Ineligible.
- Eligible subject to deficiency resolution.
- Exception required.

### Actions

- Mark eligible.
- Mark ineligible.
- Create rejection note.
- Send to loan limit calculator.
- Add comments.

---

## S16 — Active Member Verification

### Purpose

Validate whether the applicant meets SFPCL active member criteria derived from the Articles of Association.

### Screen Sections

1. Member type selector.
2. Service availed evidence.
3. Produce supply history.
4. Relaxation eligibility.
5. Employment / service alternative for producer member.
6. Decision and reason.

### Individual Member Rules Display

An individual member must:

- Avail, directly or indirectly, services offered by SFPCL during membership.
- Supply primary produce for a continuous period of four financial years as on the last date of previous financial year to SFPCL, subsidiaries, step-down subsidiaries or through a Producer Institution member that supplies to these entities.

Relaxation:

- Four-year condition does not apply if member supplied produce for at least one year to eligible SFPCL-linked entities.
- Alternatively, Producer Member may qualify if they provided employment or other services for a continuous period of three years to SFPCL, subsidiaries or step-down subsidiaries.

### Producer Institution Rules Display

A Producer Company / institutional member must:

- Be a member of SFPCL.
- Avail services directly or indirectly.
- Supply primary produce for continuous period of four financial years to SFPCL, subsidiaries or step-down subsidiaries.

Relaxation:

- Four-year condition does not apply to member producer companies that supplied produce for at least one year to SFPCL, subsidiaries or step-down subsidiaries.

### Fields

| Field | Type | Notes |
|---|---|---|
| Member type | Dropdown | Individual / FPC / Producer Institution |
| Services availed | Yes / No / Unknown | Evidence link required if Yes |
| Produce supply years | Multi-year table | Financial-year-wise records |
| Continuous four-year condition met | System derived | Yes / No |
| One-year relaxation applicable | Yes / No | Requires evidence |
| Three-year service alternative applicable | Yes / No | Individual producer member only |
| Active member decision | Active / Inactive / Needs Review | Mandatory |
| Decision reason | Text | Mandatory if inactive or manual override |

### Actions

- Verify active status.
- Mark inactive.
- Request evidence.
- Add manual override request.
- View supporting records.

### Blocking Rule

Loan appraisal cannot be submitted as eligible unless active member status is verified or an approved exception exists.

---

## S17 — KYC Verification

### Purpose

Verify borrower, nominee and where applicable witness KYC documents.

### Sections

1. Borrower KYC.
2. Nominee KYC.
3. Witness KYC, when documentation stage begins.
4. CKYC consent.
5. Re-KYC status.
6. Risk rating.

### Borrower KYC Fields

| Field | Required | Notes |
|---|---:|---|
| PAN number | Yes | Format validation |
| PAN copy | Yes | Self-attested flag |
| Aadhaar number | Yes for individual | Masked display |
| Aadhaar copy | Yes for individual | Self-attested flag |
| Photo | Recommended / required if configured | Upload |
| Address | Yes | From OVD or application |
| CKYC consent | Required if CKYC implemented | Signed consent |
| KYC verification status | Yes | Pending / Verified / Rejected |
| Re-KYC due date | System | Every two years as per SOP controls |
| Risk category | Required if AML workflow active | Low / Medium / High |

### Validations

- PAN and Aadhaar required before appraisal completion.
- Re-KYC overdue should block new disbursement or require update depending on policy configuration.
- Missing CKYC consent should appear as high-priority deficiency if CKYC is enabled.

### Actions

- Mark verified.
- Reject document.
- Request re-upload.
- Create KYC deficiency.
- Schedule re-KYC.

---

## S18 — Loan Limit Calculator

### Purpose

Calculate the maximum eligible loan amount based on shareholding and land-based scale of finance.

### Inputs

| Input | Source | Notes |
|---|---|---|
| Number of shares held | Member profile / application | Required |
| Latest valuation per share | Policy configuration | Based on latest audited financials approved at AGM |
| Applicable percentage | Policy configuration | SOP inconsistency requires confirmation: 30% vs 10% |
| Current per-share result | Policy configuration | SOP references ₹200 per share based on 10% valuation |
| Land area under cultivation | Land evidence | From 7/12 extract / application |
| Scale of finance per acre | Policy configuration | Currently capped at ₹20,000 per acre |
| Requested loan amount | Application | Borrower requested amount |

### Calculations

Shareholding-based limit:

```text
Shareholding-Based Loan Limit = Number of Shares × Applicable Percentage of Valuation per Share
```

Agricultural land-based limit:

```text
Land-Based Loan Limit = Per-Acre Cost of Cultivation × Land Area Under Cultivation
```

Final eligible amount:

```text
Final Eligible Loan Amount = Lower of Shareholding-Based Limit and Land-Based Limit
```

### SOP Inconsistency Warning

The screen must display a configuration warning until resolved:

> SOP references both 30% of valuation per share and 10% of valuation per share, and also refers to ₹200 per share as the current result. Confirm the operative rule before production use.

### Output Fields

| Field | Description |
|---|---|
| Shareholding-based limit | Calculated amount |
| Land-based limit | Calculated amount |
| Final eligible amount | Lower of both limits |
| Requested amount | From application |
| Amount within limit | Yes / No |
| Excess amount | Requested minus eligible, if applicable |
| Exception required | Yes if requested exceeds eligible limit |
| Approval path | CFO + one Director / CFO + two Directors / Exception route |

### Actions

- Recalculate.
- Save calculation.
- Attach to appraisal note.
- Request exception approval.
- View calculation history.

### Validations

- Cannot calculate without share count.
- Cannot calculate without valuation configuration.
- Cannot calculate land-based limit without land area or configured scale of finance.
- Exception required if requested amount exceeds final eligible amount.

---

## S19 — Loan Appraisal Note

### Purpose

Prepare the Loan Appraisal Note required before submission to Sanction Committee.

### Actors

Deputy Manager - Finance prepares. Credit Manager reviews before submission.

### TAT

The system must track a two-day TAT from receipt of application to submission of Loan Appraisal Note to Sanction Committee.

### Sections

1. Borrower details.
2. Membership and active status.
3. KYC and document status.
4. Loan details.
5. Loan limit calculation.
6. Purpose and crop plan.
7. Past borrowing and default history.
8. Repayment capacity / bank statement observations.
9. Risk assessment.
10. Recommended loan amount.
11. Recommended tenure.
12. Recommended security.
13. Conditions precedent.
14. Credit Manager review.

### Fields

| Field | Description |
|---|---|
| Application reference | Auto-populated |
| Borrower name | Auto-populated |
| Member type | Auto-populated |
| Folio number | Auto-populated |
| Share count | Auto-populated |
| Active member status | From S16 |
| Existing default status | From loan history |
| Requested amount | From application |
| Eligible amount | From loan limit calculator |
| Recommended amount | Entered by Deputy Manager - Finance |
| Purpose | Agriculture / crop production details |
| Crop plan summary | From uploaded crop plan |
| Land details | From 7/12 extract |
| Bank statement observations | Manual summary |
| Risk rating | Low / Medium / High or configured scale |
| Risk rationale | Mandatory |
| Security proposed | SH-4 / CDSL pledge / blank-dated cheque / PoA / other |
| Recommendation | Approve / reject / approve with conditions / exception required |

### Actions

- Save draft.
- Validate appraisal.
- Submit to Credit Manager.
- Return for correction.
- Generate appraisal PDF.
- Submit to Sanction Committee.

### Validation Rules

- Eligibility status must be complete.
- Loan limit calculation must be saved.
- Recommended amount must not exceed eligible amount unless exception is flagged.
- Purpose must be agriculture / crop production.
- Risk rating and rationale are mandatory.
- Missing KYC or document deficiencies must be resolved or listed as conditions.

---

## S20 — Credit Manager Review

### Purpose

Allow Credit Manager to review the Loan Appraisal Note and decide whether to submit to Sanction Committee or reject at credit assessment stage.

### Sections

1. Appraisal summary.
2. Eligibility checklist.
3. Loan limit summary.
4. Risk and borrower history.
5. Deficiencies and exceptions.
6. Credit Manager decision.

### Decision Options

- Submit to Sanction Committee.
- Return to Deputy Manager - Finance for correction.
- Reject application.
- Request additional documents.
- Mark exception required and route accordingly.

### Required Comments

Mandatory comment if:

- Rejecting.
- Returning for correction.
- Recommending exception.
- Recommended amount differs from system eligible amount.

### Output

- Application routed to Sanction Committee.
- Rejection Note generated.
- Audit trail updated.

---

## S21 — Sanction Committee Workbench

### Purpose

Provide Sanction Committee members with a queue of cases pending credit scrutiny and approval.

### Primary Users

CFO and two Executive Directors designated in Board Meeting.

### Columns

| Column | Description |
|---|---|
| Application reference | Loan application ID |
| Borrower | Name |
| Member type | Individual / FPC / Producer Institution |
| Requested amount | Borrower requested amount |
| Recommended amount | Credit recommendation |
| Eligible amount | System calculated |
| Approval path | CFO + 1 Director / CFO + 2 Directors / Special approval |
| Exception flag | Yes / No |
| Director / relative flag | Yes / No |
| Risk rating | From appraisal |
| Current decision status | Pending / Partially approved / Approved / Rejected |
| Submitted date | Date sent by Credit Manager |
| TAT | Time pending |

### Filters

- Up to ₹5 lakh.
- Above ₹5 lakh.
- Exceeds borrower limit.
- Special case.
- High risk.
- Pending my approval.
- Rejected.
- Approved.

### Actions

- Open case.
- Bulk view only; no bulk approval for controlled loans.
- Export pending list.

---

## S22 — Sanction Case Detail

### Purpose

Allow Sanction Committee to perform detailed credit scrutiny and record decision.

### Sections

1. Borrower summary.
2. Application details.
3. Loan Appraisal Note.
4. Loan limit calculation.
5. KYC and document status.
6. Past borrowing history.
7. Risk assessment.
8. Compliance checks.
9. Approval matrix.
10. Committee comments and decisions.

### Sanction Committee Checklist

| Check | Required Review |
|---|---|
| Eligibility verification | Confirm member, shareholding and eligibility criteria |
| Loan amount assessment | Verify amount within permissible limit |
| Purpose of loan | Confirm agriculture / crop production and company objective alignment |
| Compliance checks | Internal policy, Companies Act, Producer Company provisions and guidelines |
| Past borrowing history | Repayment discipline and default history |
| Risk assessment | Market, operational and borrower-specific risks |
| Documentation completeness | Required documents submitted and authenticated |

### Decision Options

- Approve.
- Approve with conditions.
- Reject.
- Return to Credit Assessment Team.
- Request exception documentation.
- Route to special case approval.

### Approval Matrix Behaviour

| Scenario | Required Approval |
|---|---|
| Loan up to ₹5,00,000 | CFO + one Director |
| Loan above ₹5,00,000 | CFO + two Directors |
| Loan exceeding maximum permissible borrower limit | CFO + two Directors, reason in Exception Register |
| Director / Sanction Committee member / relative borrower | Remaining Sanction Committee members excluding applicant, plus general meeting approval as applicable |

### Required Fields for Each Approver

- Decision.
- Date and time.
- Comment.
- Digital signature / approval confirmation.
- Abstention reason if applicable.

### Output

- Credit Sanction Register entry.
- Approval / rejection communication to Credit Assessment Team.
- Status update.

---

## S23 — Credit Sanction Register

### Purpose

Maintain the formal record of Sanction Committee decisions.

### Columns

| Column | Description |
|---|---|
| Sanction register entry number | System generated |
| Application reference | Linked loan application |
| Borrower name | Farmer / FPC |
| Folio number | Member folio |
| Requested amount | Amount requested |
| Eligible amount | System calculated |
| Sanctioned amount | Approved amount |
| Loan type | Short-term / long-term |
| Purpose | Agriculture / crop production |
| Decision | Approved / rejected / returned |
| Approval authority | CFO + one Director / CFO + two Directors / special route |
| Approver names | List |
| Approval dates | Per approver |
| Rejection reason | Mandatory if rejected |
| Exception flag | Yes / No |
| Exception reference | Link to Exception Register |
| Conditions | Any conditions precedent |
| Communication date | Date sent to Credit Assessment Team |

### Actions

- View linked case.
- Export register.
- Print register.
- View audit trail.

### Permissions

- Editable only through sanction workflow.
- Read-only to auditors.

---

## S24 — Special Case Approval

### Purpose

Handle cases where the borrower is a Sanction Committee member, director or relative.

### Trigger

Triggered when borrower relationship declaration indicates:

- Sanction Committee member as borrower.
- Director as borrower.
- Relative of Sanction Committee member or director as borrower.

### Fields

| Field | Description |
|---|---|
| Related person name | Director / committee member / relative |
| Relationship type | Self / relative / other related party |
| Related committee member | Name |
| Exclusion required | Yes / No |
| Excluded approver | User who cannot approve |
| Remaining approvers | Eligible approvers |
| General meeting approval required | Yes |
| General meeting approval date | Date |
| Resolution reference | Upload / link |
| Special approval status | Pending / Approved / Rejected |

### Rules

- Applicant or related committee member must be excluded from approval.
- General meeting approval must be captured before loan can be disbursed.
- System must block sanction completion if required approval evidence is missing.

### Actions

- Mark conflict.
- Upload general meeting resolution.
- Route to remaining committee members.
- Approve special route.
- Reject special route.

---

## S25 — Exception Register

### Purpose

Record deviations from normal policy, especially loans exceeding maximum permissible limit.

### Exception Types

- Requested amount exceeds eligible loan amount.
- Loan amount above standard approval threshold.
- Documentation waiver request.
- Re-KYC overdue but processing requested.
- Delayed documentation.
- Manual loan limit override.
- Special case borrower.
- Any stage bypass approved by CFO.

### Columns

| Column | Description |
|---|---|
| Exception ID | System generated |
| Application / loan reference | Linked record |
| Borrower | Name |
| Exception type | Dropdown |
| Description | Detailed reason |
| Financial impact | Amount involved if any |
| Risk rating | Low / Medium / High |
| Requested by | User |
| Required approval | CFO / CFO + two Directors / Board |
| Decision | Pending / Approved / Rejected |
| Approver comments | Mandatory |
| Date | Decision date |
| Supporting documents | Uploads |

### Controls

- Exception approvals require mandatory reason.
- Exceptions must be visible on all relevant screens.
- Disbursement cannot proceed if open blocking exception exists.

---

## S26 — Documentation Workspace

### Purpose

Provide Compliance Team and Company Secretary a single workspace to manage all post-sanction documents.

### Trigger

Sanction Committee approval.

### Queue Columns

| Column | Description |
|---|---|
| Application reference | Loan ID |
| Borrower | Name |
| Sanctioned amount | Amount approved |
| Shareholding mode | Physical / Demat / Mixed |
| Required document set | Auto-derived |
| PoA status | Pending / Generated / Signed / Notarised |
| Tri-party status | Pending / Signed / Not applicable |
| SH-4 status | Pending / Received / Not applicable |
| CDSL pledge status | Pending / Created / Not applicable |
| Term Sheet status | Pending / Signed |
| Loan Agreement status | Pending / Stamped / Notarised / Signed |
| Bank verification status | Not required / Pending / Complete |
| Checklist status | Pending / Complete |
| Current owner | Compliance / CS / Borrower / Credit |

### Actions

- Open documentation file.
- Generate document pack.
- Upload signed document.
- Mark stamped.
- Mark notarised.
- Request missing signature.
- Submit to Company Secretary.

---

## S27 — Document Checklist

### Purpose

Track all documents required for disbursement and record sign-offs.

### Checklist Items

| Document / Item | Required When | Owner | Required Status Before Disbursement |
|---|---|---|---|
| Borrower PAN and Aadhaar | All individual borrowers | Credit / Compliance | Verified |
| Nominee PAN and Aadhaar | All applications | Credit / Compliance | Verified |
| Witness PAN and Aadhaar | Documentation stage | Compliance | Verified |
| Cancelled cheque | All disbursements | Compliance / Finance | Verified |
| Blank-dated cheque | Security | Compliance / CS | Received and logged |
| Power of Attorney | All loan documentation per SOP | Compliance / CS | Signed, ₹500 stamp, notarised |
| Tri-party agreement | Repayment through subsidiary | Compliance / CS | Signed |
| SH-4 | Physical shares | Compliance / CS | Signed by borrower and witness, held in custody |
| CDSL pledge | Demat shares | Compliance / CS | Pledge created and PSN captured |
| Term Sheet | All loans | Compliance | Signed by borrower and nominee; CFO / directors as required |
| Loan Agreement | All loans | Compliance / CS | ₹500 stamp, notarised, signed by borrower and witness |
| Bank Verification Letter | Signature mismatch | Credit / Compliance | Bank signed / stamped or declaration obtained |
| Final checklist signatures | All loans | CS, Credit Manager, Sanction Committee, Senior Manager - Finance | Complete |

### Final Sign-Off Sequence

1. Company Secretary signs that all documents are verified and attached.
2. Credit Manager signs that loan disbursement limits are reviewed and confirmed.
3. Sanction Committee signs final disbursement approval as per authority matrix.
4. Senior Manager - Finance signs after actual disbursement is completed.

### Actions

- Mark checklist item complete.
- Attach document.
- Reject checklist item.
- Request correction.
- Submit to CS.
- Submit to Credit Manager.
- Submit to Sanction Committee.
- Submit to Finance.

### Blocking Rule

Disbursement readiness cannot be achieved unless all mandatory checklist items are complete or an approved exception exists.

---

## S28 — Power of Attorney Screen

### Purpose

Generate and track PoA in favour of Company Secretary.

### Fields

| Field | Description |
|---|---|
| Borrower name | Auto-populated |
| Nominee name | Auto-populated |
| Company Secretary name | Configured authorised person |
| Loan application reference | Auto-populated |
| Share details | Auto-populated |
| Stamp value | ₹500 |
| Stamp paper number | Entered |
| Notary details | Name, registration, date |
| Borrower signature status | Pending / Signed |
| Nominee signature status | Pending / Signed |
| CS verification status | Pending / Verified |

### Actions

- Generate PoA.
- Upload signed copy.
- Mark stamped.
- Mark notarised.
- Send for correction.

### Validation

- Must be signed by farmer and nominee.
- Must be on ₹500 stamp paper.
- Must be notarised.
- Required before final documentation approval.

---

## S29 — Tri-Party Agreement Screen

### Purpose

Generate and track agreement between borrower, SFPCL and relevant subsidiary for loan repayment deductions from produce payments.

### Fields

| Field | Description |
|---|---|
| Borrower | Name |
| SFPCL entity | Auto-populated |
| Subsidiary company | Select from entity master |
| Produce / crop linkage | Crop and transaction basis |
| Deduction scope | Principal, interest and other dues |
| Payment transfer obligation | Subsidiary to SFPCL |
| Borrower signature | Pending / Signed |
| Nominee signature | Pending / Signed if required by template |
| Subsidiary authorised signatory | Name and signature status |
| SFPCL signatory | Name and signature status |

### Actions

- Generate agreement.
- Upload signed agreement.
- Mark active.
- Link to subsidiary deduction reconciliation.

### Validations

- Required if repayment is to be made through subsidiary deductions.
- Subsidiary must be selected.
- Signed agreement required before disbursement if this repayment channel is selected.

---

## S30 — SH-4 Physical Share Security Screen

### Purpose

Track Share Transfer Form SH-4 used as security for loans where shares are physically held.

### Fields

| Field | Description |
|---|---|
| Shareholder name | Borrower |
| Folio number | Auto-populated |
| Share certificate numbers | Entered / linked |
| Number of shares covered | Entered |
| SH-4 form generated | Yes / No |
| Borrower signature | Pending / Signed |
| Witness name | Linked from S09 |
| Witness signature | Pending / Signed |
| Witness shareholder validation | Verified / Not verified |
| Physical custody location | Cabinet / file reference |
| Received by | Compliance / CS user |
| Received date | Date |
| Return status | Held / Returned / Invoked |

### Actions

- Generate SH-4 checklist.
- Upload scanned SH-4.
- Mark original received.
- Assign custody location.
- Return on closure.
- Invoke after approved recovery action.

### Validations

- Required if shares are not in demat form.
- Witness must be existing SFPCL shareholder.
- Form must be signed by borrower and witness.

---

## S31 — CDSL Pledge Screen

### Purpose

Track demat share pledge process through CDSL where borrower shares are in demat form.

### Fields

| Field | Description |
|---|---|
| Pledgor BO account | Borrower BO account |
| Pledgee BO account | SFPCL / pledgee BO account |
| Depository Participant details | Pledgor and pledgee DP |
| Securities in approved list | Yes / No |
| Pledge Request Form uploaded | Yes / No |
| PRF submission date | Date |
| Pledge Sequence Number | PSN generated by depository |
| Pledge request status | Created / Accepted / Rejected |
| Pledge acceptance date | Date |
| Agreement number informed | Yes / No |
| Future shares pledge flag | Yes / No |
| Invocation status | Not invoked / Invoked |
| Unpledge status | Not applicable / Requested / Complete |

### Workflow Steps Display

1. Confirm pledgor and pledgee have CDSL BO accounts.
2. Confirm securities are in pledgee approved list.
3. Upload duplicate Pledge Request Form.
4. Record pledge request created by pledgor DP.
5. Capture Pledge Sequence Number.
6. Capture pledgee DP acceptance or rejection.
7. Mark pledge created.
8. Link pledge to loan agreement.

### Actions

- Create pledge task.
- Upload PRF.
- Enter PSN.
- Mark accepted.
- Mark rejected.
- Start invocation request, only after approved recovery action.
- Start unpledge request after closure.

### Validations

- Required for demat shares.
- Disbursement blocked until pledge is accepted or approved exception exists.

---

## S32 — Term Sheet Screen

### Purpose

Prepare and track Term Sheet for the loan.

### Required Term Sheet Fields

| Field | Description |
|---|---|
| Borrower details | Name, member type, contact |
| Nominee details | Name, age, Aadhaar, PAN, gender |
| Shares held | Folio, count, mode |
| Loan facility type | Long-term / short-term |
| Loan amount | Sanctioned amount |
| Purpose | Agriculture / crop production |
| Rate of interest | Floating rate; current configured rate |
| Tenure of interest | As per loan terms |
| Repayment date | Scheduled repayment date |
| Penalty interest | Configured / pending confirmation |
| Other charges / fees | Configured / pending confirmation |
| Security | PoA, SH-4 / CDSL pledge, blank cheque, others |
| Dispute resolution | Template clause |

### Signature Rules

- Borrower must sign.
- Nominee must sign.
- If loan is below ₹5 lakh, CFO signs Term Sheet.
- If loan exceeds ₹5 lakh, CFO and two Directors sign Term Sheet.

### Actions

- Generate Term Sheet.
- Preview.
- Send for borrower / nominee signature.
- Upload signed copy.
- Route to CFO / Directors.
- Mark complete.

### Validation

- Interest rate must be available or explicitly marked pending configuration.
- Penal charges and fees should be captured if applicable.
- Term Sheet cannot complete without correct approval signatures.

---

## S33 — Loan Agreement Screen

### Purpose

Prepare and track the formal Loan Agreement.

### Fields

| Field | Description |
|---|---|
| Borrower | Auto-populated |
| SFPCL authorised signatory | Configured |
| Loan amount | Sanctioned amount |
| Tenure | From sanction / term sheet |
| Interest rate | From term sheet |
| Repayment schedule | Linked |
| Security instruments | Linked PoA, SH-4 / CDSL, cheque |
| Covenants | Template |
| Events of default | Template |
| Remedies | Template |
| Stamp value | ₹500 |
| Stamp paper number | Entered |
| Notary details | Entered |
| Borrower signature | Pending / Signed |
| Witness signature | Pending / Signed |
| Agreement status | Draft / Generated / Signed / Stamped / Notarised / Complete |

### Actions

- Generate agreement.
- Upload signed copy.
- Mark stamped.
- Mark notarised.
- Link witness.
- Send to checklist.

### Validation

- Must be executed on ₹500 stamp paper.
- Must be notarised.
- Must be signed by loan applicant and witness.

---

## S34 — Bank Verification / Signature Mismatch Screen

### Purpose

Resolve cases where borrower signature differs across PAN, cheque, KYC documents or other submitted documents.

### Trigger

Credit Assessment Team or Compliance Team marks signature mismatch.

### Fields

| Field | Description |
|---|---|
| Mismatch detected by | User |
| Documents compared | PAN / cheque / Aadhaar / agreement / other |
| Mismatch description | Mandatory |
| Resolution option | Bank Verification Letter / Borrower Declaration |
| Bank name | Required for bank letter |
| Account number | Masked |
| IFSC | From cancelled cheque |
| Bank letter status | Pending / Received / Verified |
| Declaration status | Pending / Received / Verified |
| Verifier | User who accepted resolution |

### Resolution Options

Option 1: Bank Verification Letter.

- Must be signed and stamped by concerned bank.
- Confirms cheque signature belongs to account holder.
- Confirms signature is valid for transaction purposes.

Option 2: Borrower Declaration.

- Declaration on non-judicial stamp paper.
- Affirms the signature belongs to loan applicant.

### Actions

- Generate bank verification letter.
- Upload bank-signed letter.
- Upload borrower declaration.
- Mark resolved.
- Mark unresolved and block disbursement.

### Blocking Rule

If signature mismatch is open, final documentation approval and disbursement must be blocked.

---

## S35 — Final Documentation Approval Screen

### Purpose

Route the completed documentation file through final approvals before disbursement.

### Approval Sequence

1. Compliance Team submits file to Company Secretary.
2. Company Secretary verifies all required documents.
3. Credit Manager verifies loan limits.
4. Sanction Committee gives final approval for disbursement as per authority matrix.
5. Treasury receives file for disbursement.
6. Senior Manager - Finance signs after actual disbursement.

### Screen Layout

- Checklist summary.
- Missing / blocked items.
- Approval timeline.
- Approver comments.
- Final readiness status.

### Sign-Off Meanings

| Signatory | Meaning |
|---|---|
| Company Secretary | All documents required for loan disbursement have been verified and attached. |
| Credit Manager | Loan disbursement limits have been reviewed and confirmed. |
| Sanction Committee | Final approval for loan disbursement according to authority matrix. |
| Senior Manager - Finance | Loan has been disbursed to applicant account. |

### Actions

- Approve documentation.
- Return for correction.
- Add condition.
- Submit to next approver.
- Mark ready for SAP setup / disbursement.

### Validation

- No missing mandatory documents.
- No unresolved signature mismatch.
- No incomplete security document.
- Sanction must be approved.
- Term Sheet and Loan Agreement must be correctly signed.

---

## S36 — SAP Customer Code Request

### Purpose

Create or confirm SAP customer code for borrower before loan disbursement.

### Actors

Credit Manager initiates. Senior Manager - Finance processes.

### Rules

- New borrower: create new Customer ID in SAP.
- Borrower with existing outstanding loan: reuse existing Customer ID.
- Customer ID is created after Sanction Committee approval.

### Request Fields

| Field | Required | Notes |
|---|---:|---|
| Farmer / borrower full name | Yes | Excel template field |
| Aadhaar number | Yes for individual | Masked display in UI |
| PAN number | Yes | Excel template field |
| Address | Yes | From application |
| Email ID | Recommended | If available |
| Loan application number | Yes | `LO...` |
| Existing SAP customer code | Conditional | Required if reuse |
| Request email generated | System | Tracks official email to Senior Manager - Finance |

### Actions

- Create SAP request.
- Generate Excel template.
- Send email to Senior Manager - Finance.
- Mark existing SAP code reused.
- Upload SAP confirmation.

### Output

- SAP request status becomes `Requested`.
- Finance task created for Senior Manager - Finance.

---

## S37 — SAP Customer Code Confirmation

### Purpose

Allow Senior Manager - Finance to confirm creation or reuse of SAP Customer Code.

### Fields

| Field | Description |
|---|---|
| SAP request reference | System |
| Borrower name | Auto-populated |
| Application reference | Auto-populated |
| SAP customer code | Entered |
| Created / reused | Dropdown |
| SAP creation date | Date |
| Confirmation email date | Date |
| Confirmation attachment | Optional upload |
| Finance comments | Text |

### Actions

- Confirm code created.
- Confirm existing code reused.
- Return request for missing data.
- Mark SAP error.

### Validations

- Disbursement readiness requires SAP customer code.
- SAP code format should be validated if format is configured.

---

## S38 — Disbursement Readiness Review

### Purpose

Senior Manager - Finance verifies that all documentation, SAP setup and approvals are complete before initiating payment.

### Readiness Checklist

| Item | Required Status |
|---|---|
| Sanction approved | Yes |
| Documentation checklist complete | Yes |
| Company Secretary sign-off | Complete |
| Credit Manager sign-off | Complete |
| Sanction Committee final approval | Complete |
| SAP customer code created / reused | Complete |
| Cancelled cheque verified | Complete |
| Borrower bank details entered | Complete |
| Bank verification letter resolved if mismatch | Complete |
| No blocking exceptions | Yes |
| Disbursement amount equals sanctioned amount or approved lesser amount | Yes |

### Actions

- Mark ready for payment.
- Return to documentation.
- Return to SAP setup.
- Add finance blocker.

### Blocking Rule

Payment initiation is disabled until readiness status is `Ready`.

---

## S39 — Payment Initiation Screen

### Purpose

Initiate online transfer through SFPCL’s RBL Bank account.

### Actor

Senior Manager - Finance.

### Fields

| Field | Description |
|---|---|
| Borrower name | Auto-populated |
| Application reference | Auto-populated |
| SAP customer code | Auto-populated |
| Sanctioned amount | Auto-populated |
| Disbursement amount | Editable within sanction limits |
| Bank account holder name | From cancelled cheque |
| Account number | Masked except last four digits |
| IFSC | From cancelled cheque |
| Bank branch | From cancelled cheque |
| Payment mode | Online transfer / NEFT / RTGS as configured |
| Bank account | RBL Bank account |
| Payment narration | Includes borrower name and application number |
| Initiation date | System |
| Initiated by | User |

### Actions

- Initiate payment.
- Save payment draft.
- Cancel initiation.
- Send to Chief Financial Controller.

### Validations

- Disbursement amount cannot exceed sanctioned amount.
- Bank details must match cancelled cheque.
- Payment narration should include application number for reconciliation.
- Payment cannot be initiated if documentation not complete.

---

## S40 — CFC Payment Authorisation Screen

### Purpose

Allow Chief Financial Controller, as authorised signatory, to provide final approval and execute the bank transfer.

### Fields

| Field | Description |
|---|---|
| Payment request ID | System |
| Borrower | Name |
| Application reference | ID |
| Amount | Disbursement amount |
| Bank details | Masked |
| Initiated by | Senior Manager - Finance |
| Initiated date | Date |
| Readiness status | Complete / blocked |
| Supporting documents | Checklist, sanction, bank details |
| Authorisation decision | Approve / reject / return |
| Comment | Mandatory if reject / return |

### Actions

- Approve and mark transferred.
- Reject payment request.
- Return to Senior Manager - Finance.
- Upload bank confirmation.

### Output

- Payment status becomes `Disbursed` after confirmation.
- Loan account is activated.
- Loan register updated.
- Disbursement advice task created.

---

## S41 — Disbursement Advice Screen

### Purpose

Generate and send disbursement advice to borrower after successful payment.

### Fields

| Field | Description |
|---|---|
| Borrower name | Auto-populated |
| Application reference | Auto-populated |
| Loan account number | Generated / linked |
| Disbursement amount | Paid amount |
| Disbursement date | Payment confirmation date |
| Bank reference number | Entered / uploaded |
| Repayment terms summary | From Term Sheet |
| Interest rate | Current rate |
| Repayment date | From schedule |
| Communication mode | Email / SMS / hard copy |

### Actions

- Generate advice.
- Send email.
- Send SMS summary.
- Mark hard copy dispatched.
- Download PDF.

### Output

- Loan status becomes `Active`.
- Monitoring schedule begins.
- Senior Manager - Finance checklist signature recorded.

---

## S42 — Loan Account 360

### Purpose

Provide complete view of active or historical loan after disbursement.

### Header Fields

| Field | Description |
|---|---|
| Loan account number | System generated |
| Application reference | Linked |
| Borrower | Name |
| SAP customer code | Code |
| Sanctioned amount | Amount |
| Disbursed amount | Amount |
| Outstanding principal | Current amount |
| Outstanding interest | Current amount |
| Loan type | Short-term / long-term |
| Interest rate | Floating current rate |
| Repayment due date | Next due |
| DPD status | Current bucket |
| Loan status | Active / Overdue / Closed / Default review |
| Security status | Held / pledged / released / invoked |

### Tabs

1. Overview.
2. Repayment schedule.
3. Ledger.
4. Interest invoices.
5. Documents.
6. Security.
7. Monitoring.
8. Default history.
9. Communications.
10. Closure.
11. Audit trail.

### Actions

- Record repayment.
- Generate statement.
- View documents.
- Send reminder.
- Open default case.
- Initiate closure if fully repaid.

---

## S43 — Repayment Schedule Screen

### Purpose

Display and maintain repayment schedule based on loan agreement and term sheet.

### Fields

| Field | Description |
|---|---|
| Schedule line number | System |
| Due date | Repayment date |
| Principal due | Amount |
| Interest due | Amount if scheduled |
| Other charges due | Amount if applicable |
| Total due | Calculated |
| Amount received | Payment received |
| Status | Pending / Partially paid / Paid / Overdue |
| DPD | Days past due |
| Grace period end date | If applicable |
| Extension end date | If applicable |

### Rules

- Short-term loan means one-year period.
- Long-term loan means all other tenures.
- Repayment dates come from Term Sheet / Loan Agreement.
- Partial repayments are adjusted first against principal before interest as per SOP.

### Actions

- Add schedule item, where permitted.
- View repayment allocation.
- Record reminder.
- Open overdue workflow.

---

## S44 — Direct Repayment Entry

### Purpose

Record repayment made directly by farmer through RTGS / NEFT.

### Actors

Accounts Team / Credit Manager depending on operating model.

### Fields

| Field | Description |
|---|---|
| Loan account | Selected |
| Borrower | Auto-populated |
| Payment date | Date received |
| Amount received | Amount |
| Payment mode | RTGS / NEFT |
| Bank reference number | Required |
| Bank account credited | SFPCL account |
| Principal allocation | System calculated first |
| Interest allocation | After principal as per SOP |
| Other dues allocation | If configured |
| Unallocated amount | If any |
| SAP entry status | Pending / Posted |
| SAP posting date | Next working day target |

### Actions

- Record receipt.
- Allocate payment.
- Mark SAP posted.
- Upload bank statement evidence.
- Reverse entry, with permission and reason.

### Validations

- Payment amount must be positive.
- Loan account must be active or overdue, not closed.
- Principal-first allocation should be default.
- SAP posting should be due next working day after payment confirmation.

---

## S45 — Subsidiary Deduction Reconciliation

### Purpose

Track repayment amounts deducted by subsidiary companies from produce payments and transferred to SFPCL.

### Fields

| Field | Description |
|---|---|
| Subsidiary company | Selected |
| Bank transaction date | Date |
| Amount received | Amount |
| Borrower name in statement | Text |
| Loan application number in statement | Text |
| Matched loan account | System / manual match |
| Deducted principal | Amount |
| Deducted interest | Amount |
| Other dues | Amount |
| Reconciliation status | Unmatched / Matched / Partially matched / Exception |
| Tri-party agreement linked | Yes / No |
| SAP receipt entry status | Pending / Posted |

### Matching Rules

- Bank statement transaction should clearly reflect borrower name and loan application number.
- If borrower name or application number is missing, transaction should be flagged for manual reconciliation.
- Tri-party agreement must exist for subsidiary repayment route.

### Actions

- Upload bank statement.
- Match transaction.
- Split transaction across loans if permitted.
- Mark SAP posted.
- Create reconciliation exception.

---

## S46 — Loan Ledger

### Purpose

Show all financial movements for a loan.

### Ledger Columns

| Column | Description |
|---|---|
| Date | Transaction date |
| Transaction type | Disbursement, repayment, interest accrual, interest invoice, capitalisation, adjustment, reversal |
| Reference | Bank / SAP / invoice reference |
| Debit | Amount increasing outstanding |
| Credit | Amount reducing outstanding |
| Principal balance | Running principal |
| Interest balance | Running interest |
| Total outstanding | Running total |
| Posted by | User |
| SAP status | Posted / pending / failed |
| Remarks | Notes |

### Actions

- Export ledger.
- Download statement.
- View transaction details.
- Open SAP evidence.

### Controls

- Financial reversals require elevated permission and mandatory reason.
- Ledger must remain immutable except through reversal entries.

---

## S47 — Interest Accrual Screen

### Purpose

Support monthly SAP accrual entries for loan interest.

### Actors

Accounts Team / Credit Manager.

### Fields

| Field | Description |
|---|---|
| Accrual month | Month / year |
| Loan account | Selected / batch |
| Principal balance | Amount |
| Interest rate | Current floating rate |
| Days basis | Configured |
| Accrued interest | Calculated |
| SAP posting status | Pending / Posted |
| Posted date | Date |
| Posted by | User |

### Actions

- Calculate accrual.
- Review batch.
- Post / mark posted in SAP.
- Export accrual file.
- Approve accrual batch if configured.

### Validations

- Interest rate must be configured.
- Accrual should not duplicate for same loan and month.
- Closed loans should not accrue after closure date.

---

## S48 — Yearly Interest Invoice Screen

### Purpose

Generate yearly interest invoices for farmers who have availed loans.

### Actors

Sales Team prepares and issues invoices at financial year-end; Accounts / Credit Manager tracks.

### Fields

| Field | Description |
|---|---|
| Financial year | Year |
| Borrower | Name |
| Loan account | ID |
| Interest accrued | Amount |
| Interest paid | Amount |
| Interest invoice amount | Amount |
| Invoice number | Generated / entered |
| Invoice date | Date |
| Due date | Up to 30 April of next financial year, based on SOP handling |
| Invoice status | Draft / issued / paid / unpaid |
| Communication mode | Email / hard copy |

### Actions

- Generate invoice.
- Issue invoice.
- Download invoice.
- Mark paid.
- Send reminder.
- Route to capitalisation if unpaid after 30 April.

---

## S49 — Interest Capitalisation Screen

### Purpose

Capitalise unpaid interest into principal at the beginning of the next financial year if farmer cannot pay interest up to 30 April.

### Trigger

Interest invoice remains unpaid after 30 April.

### Fields

| Field | Description |
|---|---|
| Loan account | ID |
| Original principal | Amount |
| Outstanding interest | Amount |
| Capitalisation date | Beginning of next financial year |
| Revised principal | Principal + outstanding interest |
| New interest calculation basis | Revised principal |
| Borrower intimation status | Email sent / hard copy sent / pending |
| Approval status | If approval required by policy |

### Calculation

```text
Revised Principal = Original Principal + Outstanding Interest Carried Forward
```

### Actions

- Preview capitalisation.
- Approve capitalisation, if configured.
- Post to ledger.
- Generate borrower intimation email.
- Generate hard-copy intimation letter.

### Validations

- Capitalisation should happen only after 30 April where interest remains unpaid.
- Capitalisation should not duplicate.
- Borrower must be informed by official email and hard copy intimation letter.

---

## S50 — Monitoring Dashboard

### Purpose

Monitor active loan portfolio, repayments, ageing, reminders and risk.

### Users

Credit Manager, CFO, Accounts Team.

### Metrics

| Metric | Description |
|---|---|
| Total active loans | Count |
| Total outstanding principal | Amount |
| Total outstanding interest | Amount |
| Loans due in next 30 days | Count and amount |
| Loans overdue | Count and amount |
| Loans in 1-2 year DPD bucket | Count and amount |
| Loans in 2-3 year DPD bucket | Count and amount |
| Loans over 3 years | Count and amount |
| Loans in grace period | Count |
| Loans in one-year extension | Count |
| Loans pending non-payment note | Count |
| Reminders due | Count |

### Charts / Tables

- DPD bucket table.
- Loan ageing by crop.
- Loan ageing by borrower type.
- Repayments received this month.
- Interest unpaid.
- Exceptions by ageing.

### Actions

- Generate quarterly CFO MIS.
- Send reminder batch.
- Open DPD screen.
- Export report.

---

## S51 — DPD / Portfolio at Risk Screen

### Purpose

Classify and track loans by overdue age.

### SOP Buckets

The SOP monitoring buckets are:

- 1 year to 2 years.
- 2 years to 3 years.
- More than 3 years.

The glossary also references delinquency buckets such as 0-30, 31-60, 61-90 and >90 days. The screen should support configurable buckets while preserving SOP-required quarterly buckets.

### Columns

| Column | Description |
|---|---|
| Loan account | ID |
| Borrower | Name |
| Due date | Repayment due date |
| Days past due | Number |
| SOP bucket | 1-2 years / 2-3 years / 3+ years |
| Operational bucket | 0-30 / 31-60 / 61-90 / >90 if configured |
| Outstanding principal | Amount |
| Outstanding interest | Amount |
| Last repayment date | Date |
| Last reminder date | Date |
| Current default stage | Normal / Grace / Extension / Recovery review |
| Owner | Credit Manager / assigned user |

### Actions

- Send reminder.
- Open default case.
- Add monitoring note.
- Export for CFO.

---

## S52 — Reminder Management Screen

### Purpose

Manage borrower reminders by SMS, phone, email or hard-copy tracking.

### Trigger

Credit Manager sends reminders by SMS / phone when loan remains outstanding beyond one year at the end of each quarter.

### Fields

| Field | Description |
|---|---|
| Loan account | ID |
| Borrower | Name |
| Reminder reason | Overdue / interest unpaid / documents / other |
| Reminder channel | SMS / phone / email / hard copy |
| Reminder date | Date |
| Contacted person | Borrower / nominee / representative |
| Response | Text |
| Next follow-up date | Date |
| Created by | User |

### Actions

- Send SMS.
- Log phone call.
- Send email.
- Generate hard-copy letter.
- Schedule follow-up.

---

## S53 — Default Case Detail

### Purpose

Manage loans that miss scheduled principal repayment.

### Trigger

Borrower unable to repay principal amount for one scheduled repayment.

### Default Flow Display

```text
Missed scheduled principal repayment
-> 3-month grace period
-> reason assessment
-> intentional or non-intentional classification
-> if non-intentional: 1-year extension
-> if still unpaid: non-payment note
-> Sanction Committee decision
-> recovery action / further action
```

### Fields

| Field | Description |
|---|---|
| Default case ID | System |
| Loan account | ID |
| Borrower | Name |
| Missed due date | Date |
| Principal due | Amount |
| Amount unpaid | Amount |
| Grace period start | Due date |
| Grace period end | Due date + 3 months |
| Reason assessment status | Pending / Complete |
| Default nature | Intentional / Non-intentional / Undetermined |
| Evidence | Uploads and notes |
| Current stage | Grace / Extension / Non-payment review / Recovery |

### Actions

- Start default case.
- Record reason assessment.
- Start grace period.
- Recommend extension.
- Prepare non-payment note.
- Submit to Sanction Committee.

---

## S54 — Grace Period and Extension Screen

### Purpose

Track three-month grace period and one-year extension for non-intentional non-payment.

### Three-Month Grace Fields

| Field | Description |
|---|---|
| Grace period start date | Scheduled repayment due date |
| Grace period end date | Due date + 3 months |
| Amount due | Principal unpaid |
| Reminder schedule | Configured reminders |
| Repayment during grace | Payments received |
| Grace status | Active / Completed / Failed |

### Reason Assessment Fields

| Field | Description |
|---|---|
| Assessment date | Date |
| Assessed by | Credit Assessment Team |
| Borrower explanation | Text |
| Evidence | Uploads |
| Intentional / non-intentional decision | Dropdown |
| Rationale | Mandatory |

### One-Year Extension Fields

| Field | Description |
|---|---|
| Extension recommended | Yes / No |
| Extension start | Date after grace failure |
| Extension end | One year later |
| Extension note | Required document |
| Approved by | Configured authority if required |
| Extension status | Active / Completed / Failed |

### Actions

- Mark grace successful.
- Mark grace failed.
- Record non-intentional default.
- Create extension note.
- Approve extension.
- Move to non-payment review.

---

## S55 — Note for Non-Payment Screen

### Purpose

Prepare a formal note for Sanction Committee when borrower still cannot repay principal after one-year extension.

### Fields

| Field | Description |
|---|---|
| Loan account | ID |
| Borrower | Name |
| Original due date | Date |
| Grace period outcome | Summary |
| Extension outcome | Summary |
| Amount still unpaid | Amount |
| Reason for non-payment | Text |
| Intentional / non-intentional assessment | Dropdown |
| Evidence reviewed | Uploads |
| Credit Assessment Team recommendation | Recovery / further extension / write-off review / other |
| Prepared by | User |
| Reviewed by | Credit Manager |
| Submitted to Sanction Committee | Date |

### Actions

- Save draft.
- Generate PDF.
- Submit to Sanction Committee.
- Return for correction.

### Output

- Sanction Committee task for recovery decision.

---

## S56 — Recovery Action Approval Screen

### Purpose

Allow Sanction Committee to decide further recovery action based on Note for Non-Payment.

### Inputs

- Note for Non-Payment.
- Loan ledger.
- Security instruments.
- SH-4 / CDSL pledge status.
- Blank-dated cheque custody.
- Borrower communication log.
- Reason assessment.

### Decision Options

- Initiate sale / transfer of shares.
- Invoke CDSL pledge.
- Present blank-dated cheque.
- Continue follow-up.
- Reject recovery action and request further assessment.
- Other action as approved.

### Required Approvals

- Sanction Committee approval.
- CFO / Board approval if configured for SH-4 or cheque invocation.

### Mandatory Fields

| Field | Description |
|---|---|
| Recovery action selected | Dropdown |
| Reason | Mandatory |
| Amount to recover | Amount |
| Security to invoke | SH-4 / CDSL / cheque |
| Legal / compliance review | Required before execution |
| Approver comments | Mandatory |
| Decision date | Date |

### Control

Using SH-4 or undated cheque without proper approval is listed as a critical error to avoid. The system must enforce approval before execution screens are enabled.

---

## S57 — Security Invocation Screen

### Purpose

Execute approved recovery action against held securities.

### Separate Modes

1. SH-4 physical share transfer invocation.
2. CDSL pledge invocation.
3. Blank-dated cheque presentation.

### SH-4 Invocation Fields

- SH-4 custody reference.
- Share certificate details.
- Number of shares.
- Approved recovery action reference.
- Transfer initiation date.
- Execution status.
- Proceeds received.
- Ledger adjustment.

### CDSL Invocation Fields

- Pledge Sequence Number.
- Invocation Request Form status.
- DP submission date.
- Securities moved date.
- Pledgor notification status.
- Proceeds / value applied.

### Blank-Dated Cheque Fields

- Cheque number.
- Bank name.
- Amount inserted.
- Date inserted.
- Presentation date.
- Bank status.
- Recovery amount.

### Actions

- Generate invocation checklist.
- Upload forms.
- Mark submitted.
- Mark completed.
- Post recovery proceeds.

### Validations

- Recovery action approval must exist.
- Security must be in custody or pledged.
- Amount recovered must be posted to loan ledger.

---

## S58 — Loan Closure Screen

### Purpose

Close loan after full repayment.

### Closure Preconditions

- Outstanding principal is zero.
- Outstanding interest is zero or waived through approved process.
- Other charges are zero or waived.
- No unresolved ledger entries.
- No pending recovery action.

### Fields

| Field | Description |
|---|---|
| Loan account | ID |
| Borrower | Name |
| Full repayment date | Date |
| Principal outstanding | Must be zero |
| Interest outstanding | Must be zero or approved adjustment |
| Security release required | Yes / No |
| NOC required | Yes |
| Closure approved by | User |
| Closure date | Date |

### Actions

- Validate closure.
- Generate closure checklist.
- Initiate NOC.
- Initiate security return.
- Mark closed.

---

## S59 — NOC Generation Screen

### Purpose

Generate No Objection Certificate after full repayment.

### Fields

| Field | Description |
|---|---|
| Borrower name | Auto-populated |
| Loan account | Auto-populated |
| Application reference | Auto-populated |
| Original loan amount | Amount |
| Full repayment date | Date |
| NOC issue date | Date |
| Authorised signatory | Company Secretary / configured signatory |
| Delivery mode | Email / hard copy |
| Delivery status | Sent / dispatched / acknowledged |

### Actions

- Generate NOC.
- Download PDF.
- Send to borrower.
- Mark hard copy dispatched.
- Upload acknowledged copy.

### Validation

- NOC cannot be issued until full repayment is validated.

---

## S60 — Security Return / Unpledge Screen

### Purpose

Track return of SH-4, blank-dated cheque and unpledging of demat shares after loan closure.

### Fields

| Security | Required Closure Action |
|---|---|
| SH-4 | Return copy / original as per custody policy |
| Blank-dated cheque | Return to borrower and record acknowledgement |
| CDSL pledge | Complete unpledge request |
| PoA | Archive as closed loan document unless return policy says otherwise |

### SH-4 / Cheque Return Fields

- Security item.
- Custody location.
- Returned to.
- Return date.
- Acknowledgement uploaded.
- Returned by.

### CDSL Unpledge Fields

- Unpledge Request Form uploaded.
- PSN used.
- Pledgor DP submission date.
- Pledgee DP acceptance date.
- Auto-unpledge used: Yes / No.
- Unpledge complete date.

### Actions

- Generate return acknowledgement.
- Mark returned.
- Start unpledge.
- Mark unpledge complete.
- Upload evidence.

### Blocking Rule

Loan closure status should not be `Fully Closed and Archived` until NOC is issued and security return / unpledge is complete or formally waived.

---

## S61 — Archive Screen

### Purpose

Archive closed loan records for at least eight years.

### Fields

| Field | Description |
|---|---|
| Loan account | ID |
| Closure date | Date |
| Archive date | Date |
| Retention period | Minimum eight years |
| Archive location | Digital repository and physical file location |
| Physical file reference | Cabinet / box / file number |
| Digital archive checksum | If implemented |
| Archive status | Pending / Archived / Destroyed after retention |

### Actions

- Archive file.
- Download archive manifest.
- View archived documents.
- Record destruction after retention period, if applicable and approved.

---

## S62 — Compliance Dashboard

### Purpose

Show statutory compliance tasks and control status for SFPCL loan process.

### Compliance Areas

1. Producer Company member lending compliance.
2. Section 186 loan limit compliance.
3. NBFC principal business test.
4. KYC / AML and CKYC compliance.
5. Interest and charge disclosure.
6. Documentation and stamp duty.
7. State money-lending law review.
8. Accounting and reporting.
9. Recovery conduct and grievance redress.
10. Data protection and access controls.
11. Record retention and audit.

### Metrics

| Metric | Description |
|---|---|
| Loans to non-members | Must be zero |
| Loans exceeding limit without approval | Must be zero |
| KYC incomplete loans | Count |
| Re-KYC due | Count |
| Unstamped agreements | Count |
| Missing SH-4 / pledge | Count |
| Section 186 utilisation | Percentage |
| NBFC asset ratio | Percentage |
| NBFC income ratio | Percentage |
| Open grievances | Count |
| Records nearing retention review | Count |

### Actions

- Open compliance task.
- Export compliance report.
- Generate Board pack.
- Add compliance note.

---

## S63 — Section 186 Limit Tracker

### Purpose

Monitor loan limits under Section 186 thresholds as captured in the SOP compliance framework.

### Fields

| Field | Description |
|---|---|
| Paid-up capital | Amount |
| Free reserves | Amount |
| Securities premium | Amount |
| 60% threshold calculation | 60% of paid-up capital + free reserves + securities premium |
| 100% threshold calculation | 100% of free reserves + securities premium |
| Applicable limit | Higher of the two |
| Current loans / advances | Amount |
| Utilisation percentage | Current exposure / applicable limit |
| Prior approval required | Yes / No |
| Board / special resolution reference | Upload if exceeded |
| Quarter | Period |
| Prepared by | CFO / Accounts |
| Reviewed by | CFO / Board |

### Actions

- Calculate quarter.
- Upload evidence.
- Generate Board note.
- Mark reviewed.

---

## S64 — NBFC Principal Business Test

### Purpose

Monitor whether RBI NBFC registration threshold may be triggered.

### Fields

| Field | Description |
|---|---|
| Total assets | Amount |
| Financial assets | Amount |
| Financial assets ratio | Financial assets / total assets |
| Gross income | Amount |
| Income from financial assets | Amount |
| Financial income ratio | Financial income / gross income |
| Threshold breached | Yes if both ratios exceed 50% |
| Quarter | Period |
| Prepared by | CFO / Accounts |
| Board presentation status | Pending / Presented |
| Comments | Notes |

### Alerts

- Warning at configurable early-warning threshold, for example 40%.
- Critical when either ratio approaches 50%.
- Breach when both exceed 50%.

### Actions

- Save calculation.
- Upload supporting financials.
- Present to Board.
- Create compliance action.

---

## S65 — KYC / AML and Re-KYC Tracker

### Purpose

Monitor KYC completeness and periodic re-KYC obligations.

### Columns

| Column | Description |
|---|---|
| Borrower | Name |
| Member type | Individual / FPC |
| KYC status | Complete / incomplete |
| PAN status | Verified / missing |
| Aadhaar status | Verified / missing |
| CKYC consent | Available / missing / not applicable |
| Risk category | Low / Medium / High |
| Last KYC date | Date |
| Re-KYC due date | Date |
| Days overdue | Number |
| Open loans | Count |
| Action | Update KYC |

### Actions

- Send re-KYC request.
- Upload updated KYC.
- Mark verified.
- Export KYC audit report.

---

## S66 — Stamp Duty Register

### Purpose

Track stamp duty and notarisation for legal documents.

### Columns

| Column | Description |
|---|---|
| Document reference | PoA / Loan Agreement / declaration |
| Application reference | Loan ID |
| Borrower | Name |
| Stamp value | ₹500 for PoA and Loan Agreement as specified |
| Stamp paper number | Entered |
| Stamp purchase date | Date |
| Notary required | Yes / No |
| Notary completed | Yes / No |
| Notary date | Date |
| Custody location | Physical file reference |
| Verified by CS | Yes / No |

### Actions

- Add stamp record.
- Upload stamp proof.
- Mark notarised.
- Export register.

---

## S67 — Money-Lending Annual Review

### Purpose

Track annual legal / compliance confirmation of exemption or applicability under Maharashtra Money-Lending Regulation Act or other state laws.

### Fields

| Field | Description |
|---|---|
| Review year | Financial year |
| State | Maharashtra / other |
| Lending geography | Locations where loans are given |
| Exemption rationale | Text |
| Legal opinion obtained | Yes / No |
| Legal opinion document | Upload |
| Board note date | Date |
| Compliance status | Pending / compliant / action required |
| Owner | Company Secretary |

### Actions

- Create annual review.
- Upload legal opinion.
- Mark Board reviewed.

---

## S68 — Grievance Register

### Purpose

Capture borrower grievances and complaint handling.

### Fields

| Field | Description |
|---|---|
| Grievance ID | System generated |
| Borrower | Name |
| Loan account / application | Linked |
| Date received | Date |
| Mode | Form / phone / email / in-person |
| Issue category | Application, sanction, disbursement, repayment, recovery, documentation, other |
| Description | Borrower complaint |
| Assigned to | User / team |
| Target resolution date | TAT-based |
| Status | Open / in progress / resolved / closed |
| Resolution | Text |
| Closure date | Date |
| Borrower informed | Yes / No |

### Actions

- Create grievance.
- Assign.
- Add update.
- Resolve.
- Close.
- Export log.

---

## S69 — Reports and MIS Center

### Purpose

Provide reports for management, CFO, Board, audit and operations.

### Report Categories

| Category | Reports |
|---|---|
| Application | Loan Request Register, application status report, rejection report |
| Appraisal | Eligibility report, loan limit exception report, appraisal TAT report |
| Sanction | Credit Sanction Register, approval matrix report, special case report |
| Documentation | Checklist report, missing document report, stamp duty report, security custody report |
| Disbursement | Disbursement report, SAP pending report, payment failure report |
| Loan Account | Active loans, outstanding principal, outstanding interest, borrower statement |
| Repayment | Direct repayment report, subsidiary deduction report, reconciliation exceptions |
| Interest | Accrual report, yearly invoice report, unpaid interest and capitalisation report |
| Monitoring | DPD report, portfolio at risk, quarterly CFO MIS |
| Default | Grace period report, extension report, non-payment notes, recovery approvals |
| Closure | NOC issued report, security returned report, archive report |
| Compliance | Section 186, NBFC test, KYC / re-KYC, data access, grievance report |

### Report Actions

- Filter.
- Export Excel.
- Export PDF.
- Schedule email.
- Save report view.
- Drill down to records.

---

## S70 — Policy and Product Configuration

### Purpose

Configure values that drive loan calculation, eligibility, interest, charges, TATs and compliance controls.

### Configuration Sections

1. Loan product settings.
2. Share valuation settings.
3. Scale of finance settings.
4. Interest settings.
5. Penal charge settings.
6. Approval thresholds.
7. TAT settings.
8. DPD bucket settings.
9. Re-KYC frequency.
10. Document requirements.

### Key Fields

| Field | Description |
|---|---|
| Share valuation date | Latest valuation based on audited financials |
| Share valuation per share | Amount |
| Applicable loan percentage | Confirmed percentage; must resolve 30% vs 10% inconsistency |
| Per-share cap | SOP references ₹200 per share currently |
| Scale of finance per acre | Currently capped at ₹20,000 per acre |
| Short-term definition | One year |
| Long-term definition | Other tenures |
| Approval threshold | ₹5,00,000 |
| Appraisal TAT | 2 days |
| Grace period | 3 months |
| Non-intentional extension | 1 year |
| Record retention | Minimum 8 years |
| Re-KYC frequency | Every 2 years |

### Actions

- Create new policy version.
- Submit for Board approval.
- Activate policy version.
- Deactivate old version.
- View policy change history.

### Controls

- Policy changes require Board approval where applicable.
- Historical loan calculations must retain the policy version used at sanction.

---

## S71 — Approval Matrix Settings

### Purpose

Maintain sanction and disbursement approval rules.

### Default Rules

| Scenario | Required Authority |
|---|---|
| Loan up to ₹5 lakh per member | CFO + one Director |
| Loan above ₹5 lakh per member | CFO + two Directors |
| Loan exceeding maximum permissible borrower limit | CFO + two Directors and Exception Register reason |
| Disbursement initiation | Senior Manager - Finance |
| Final bank transfer | Chief Financial Controller |
| Security document execution | Company Secretary under PoA |

### Fields

- Approval rule name.
- Amount threshold.
- Borrower condition.
- Required roles.
- Minimum approver count.
- Abstention rules.
- Special case handling.
- Effective date.
- Board approval reference.

### Actions

- Add approval rule.
- Edit draft rule.
- Submit for approval.
- Activate.
- Deactivate.

---

## S72 — Template Management

### Purpose

Manage document templates used across the workflow.

### Templates

- Loan Application Form.
- Loan Appraisal Note.
- Power of Attorney.
- Tri-party Agreement / Declaration.
- SH-4 checklist / reference.
- Term Sheet.
- Loan Agreement.
- Bank Verification Letter.
- Document Checklist.
- Customer Code Creation Excel Template.
- Credit Sanction Register export template.
- Grievance Form.
- Rejection Note.
- NOC.
- Extension Note.
- Note for Non-Payment.
- Borrower intimation letter for interest capitalisation.

### Fields

| Field | Description |
|---|---|
| Template name | Name |
| Annexure reference | Annexure A-L where applicable |
| Borrower type | Individual / FPO / all |
| Version | Template version |
| Effective date | Date |
| Status | Draft / active / retired |
| Approved by | CS / Board / authorised role |
| File | Upload template |

### Actions

- Upload template.
- Preview merge fields.
- Activate template.
- Retire template.
- View history.

### Important Note

The SOP has a possible annexure inconsistency: process text refers to Annexure K as Credit Sanction Register, while annexure list labels Annexure K as Grievance Form and Complaint-Handling Log. Template management should allow correction through versioning.

---

## S73 — User and Role Management

### Purpose

Manage internal users, roles, teams and access controls.

### Fields

| Field | Description |
|---|---|
| User name | Full name |
| Email | Login / communication |
| Mobile | Optional |
| Role | One or more roles |
| Team | Credit / Compliance / Treasury / Sanction / Accounts / IT / Audit |
| Active status | Active / inactive |
| Approval authority | Yes / No and limits |
| Delegation | Temporary delegation settings |
| Last login | System |

### Actions

- Create user.
- Assign role.
- Deactivate user.
- Delegate tasks.
- Reset password.
- View access log.

### Controls

- Sanction Committee composition should match Board-approved members.
- Approval authority changes should be auditable.
- Segregation of duties should be enforced where configured.

---

## S74 — Audit Log Explorer

### Purpose

Provide auditors and authorised compliance users a searchable audit log of all system events.

### Filters

- Date range.
- User.
- Role.
- Application reference.
- Loan account.
- Action type.
- Module.
- Before / after data changes.
- Exceptions.
- Approvals.

### Columns

| Column | Description |
|---|---|
| Timestamp | Event time |
| User | Actor |
| Role | Actor role |
| Module | Screen / module |
| Action | Create / update / approve / reject / upload / download / delete / login |
| Record | Linked ID |
| Before value | If applicable |
| After value | If applicable |
| Reason | Mandatory where applicable |
| IP / device | If captured |

### Actions

- Export audit log.
- Open linked record.
- Download evidence package.

---

# 9. Cross-Screen Validation Rules

## 9.1 Application Rules

1. Application must have borrower and nominee signatures.
2. Nominee must not be a minor.
3. Borrower must be member / shareholder.
4. Folio number and share count are mandatory.
5. Required loan amount must be present.
6. Loan purpose must be agriculture / crop production only.
7. Mandatory KYC and supporting documents must be uploaded.
8. Incomplete applications must be returned with deficiency list.

## 9.2 Eligibility Rules

1. Applicant must be active member under AoA criteria.
2. Applicant must not be in default with SFPCL, subsidiary or associate company.
3. Land documents, KYC, bank statement and crop plan are mandatory.
4. Borrower must agree to Term Sheet and Loan Agreement.
5. Ineligible applications require Rejection Note.

## 9.3 Loan Limit Rules

1. Calculate shareholding-based limit.
2. Calculate land-based limit.
3. Final eligible loan amount is lower of both.
4. Requested amount above eligible amount requires exception.
5. Percentage ambiguity must be resolved in configuration before production.

## 9.4 Approval Rules

1. Up to ₹5 lakh: CFO + one Director.
2. Above ₹5 lakh: CFO + two Directors.
3. Exceeding borrower limit: CFO + two Directors and Exception Register reason.
4. Director / committee member / relative borrower: exclude conflicted person and require general meeting approval.
5. Sanction decision must be recorded in Credit Sanction Register.

## 9.5 Documentation Rules

1. PoA must be signed by farmer and nominee, executed on ₹500 stamp paper and notarised.
2. Loan Agreement must be on ₹500 stamp paper and notarised.
3. SH-4 required for physical shares.
4. CDSL pledge required for demat shares.
5. Term Sheet must be signed by borrower and nominee.
6. CFO signs Term Sheet below ₹5 lakh.
7. CFO and two Directors sign Term Sheet above ₹5 lakh.
8. Witness must be existing SFPCL shareholder.
9. Cancelled cheque required for bank verification.
10. Blank-dated cheque held as security.
11. Signature mismatch must be resolved before disbursement.

## 9.6 Disbursement Rules

1. No disbursement before sanction approval.
2. No disbursement before documentation checklist completion.
3. No disbursement before SAP customer code created or reused.
4. No disbursement before bank details verified.
5. Senior Manager - Finance initiates payment.
6. Chief Financial Controller authorises final transfer.
7. Loan register updated after disbursement.
8. Disbursement advice sent to borrower.

## 9.7 Repayment Rules

1. Direct borrower repayment is through RTGS / NEFT.
2. Partial repayments adjust first to principal.
3. SAP entry should be posted on next working day after payment confirmation.
4. Subsidiary deduction must include borrower name and loan application number in bank statement.
5. Tri-party agreement governs subsidiary repayment.

## 9.8 Interest Rules

1. Floating interest rate must be communicated to borrower when revised.
2. Yearly interest invoices must be generated.
3. Monthly SAP accrual entries must be posted.
4. If interest unpaid up to 30 April, outstanding interest is added to principal at beginning of next financial year.
5. Borrower must be informed by official email and hard-copy letter.

## 9.9 Default Rules

1. Missed scheduled principal repayment triggers three-month grace period.
2. If still unpaid, Credit Assessment Team assesses intentional vs non-intentional default.
3. Non-intentional default may receive one-year extension.
4. Extension note must be documented.
5. If still unpaid after one-year extension, Note for Non-Payment goes to Sanction Committee.
6. Sanction Committee decides on share sale, cheque presentation or other recovery action.
7. SH-4 or undated cheque must not be used without approval.

## 9.10 Closure Rules

1. Full repayment triggers closure process.
2. NOC must be issued.
3. SH-4 and blank-dated cheque must be returned.
4. Demat shares must be unpledged.
5. Records must be archived for at least eight years.

---

# 10. Critical Error Prevention Requirements

The system should explicitly prevent or warn against the top SOP errors:

| Error to Avoid | Screen-Level Prevention |
|---|---|
| Processing loans for non-members | Member validation gate in New Application and Eligibility screens |
| Exceeding per-share cap / borrower limit | Loan Limit Calculator and Exception Register |
| Missing PAN / Aadhaar or CKYC consent | KYC Verification blockers |
| Incomplete appraisal note | Required fields and appraisal validation |
| Missing witness signatures | Documentation Checklist and Witness Panel |
| Disbursing before stamping completed | Disbursement Readiness blocker |
| Incorrect bank details in SAP / payment | Cancelled cheque verification and payment review |
| Failure to send year-end interest invoice | Interest Invoice dashboard and alerts |
| Not re-KYCing every two years | Re-KYC Tracker and alerts |
| Using SH-4 or undated cheque without approval | Recovery Action Approval gate |
| Delay in NOC after closure | Closure and NOC task automation |

---

# 11. Open Issues to Reflect in UI

The following unresolved items should be represented as configuration warnings or pending policy fields:

| Issue | Required UI Handling |
|---|---|
| 30% vs 10% share valuation inconsistency | Policy configuration warning and calculation rule selection required |
| Current ₹200 per-share cap | Store as configurable policy version |
| Annexure K inconsistency | Template management should allow corrected naming and versioning |
| Interest benchmark undefined | Interest configuration cannot be production-active without benchmark / rate |
| Penal charge values undefined | Term Sheet should show pending configuration until confirmed |
| NACH / ECS not confirmed | Show as optional until enabled by policy |
| Guarantor requirement not defined | Make guarantor conditional and configurable |
| Bureau check not defined | Make credit bureau workflow optional and configurable |
| Intentional default criteria undefined | Default assessment screen should require manual rationale and evidence |
| Money-lending exemption annual review | Compliance screen should require annual legal opinion / Board note |
| NBFC threshold monitoring details | Compliance configuration should define data source and reporting cadence |

---

# 12. Screen-Level Non-Functional Requirements

## 12.1 Accessibility

- All forms should be keyboard accessible.
- Required fields must not be indicated by colour only.
- Error messages must be readable and field-specific.
- Documents should have readable metadata even if scanned file content is not accessible.

## 12.2 Performance

- Dashboard should load summary metrics quickly, even if detailed counts load progressively.
- Search should return initial results within acceptable enterprise application response time.
- Large reports should run asynchronously with download notification.

## 12.3 Security

- KYC documents must be access-controlled.
- Aadhaar should be masked except to authorised users.
- PAN should be partially masked in list views.
- Downloading KYC documents should be logged.
- Role-based access must prevent unauthorised viewing of borrower personal data.

## 12.4 Data Retention

- Closed loan records must be retained for at least eight years.
- KYC records must be retained as per configured compliance policy.
- Audit logs should not be editable.

## 12.5 Data Quality

- Critical master data should use controlled values.
- Manual override should require reason.
- Duplicate borrower detection should be implemented using member ID, folio, PAN, Aadhaar and name matching.

---

# 13. Acceptance Checklist for UI / QA

A build can be considered functionally aligned with the screen specification if:

1. All six SOP stages are represented as screens or workflow states.
2. Loan Application Form captures folio, shares, requested amount and nominee details.
3. Required KYC and supporting documents are enforced.
4. Unique application number sequence starts from `LO00000001`.
5. Two-day appraisal TAT is tracked.
6. Active member verification supports individual and producer institution rules.
7. Loan limit calculator computes shareholding and land-based limits.
8. Approval matrix is enforced for ₹5 lakh threshold and exceptions.
9. Special director / relative borrower approval workflow exists.
10. Documentation workspace tracks PoA, tri-party agreement, SH-4, CDSL pledge, Term Sheet, Loan Agreement, bank verification and checklist.
11. PoA and Loan Agreement require ₹500 stamp and notarisation status.
12. Disbursement is blocked until documentation, SAP code and bank verification are complete.
13. Senior Manager - Finance and Chief Financial Controller roles are separated.
14. Direct repayment and subsidiary deduction repayment are both supported.
15. Principal-first partial repayment allocation is supported.
16. Yearly interest invoices and monthly accrual entries are supported.
17. Interest capitalisation after 30 April is supported.
18. DPD monitoring and quarterly CFO MIS are supported.
19. Three-month grace period and one-year non-intentional extension are supported.
20. Note for Non-Payment and recovery approval workflow are supported.
21. SH-4 / CDSL / blank cheque invocation cannot happen without approval.
22. NOC, security return and CDSL unpledge are tracked at closure.
23. Compliance dashboard covers statutory controls.
24. Audit logs capture all approvals, rejections, overrides and document status changes.
25. Open SOP inconsistencies are visible as configuration warnings.

---

# 14. Recommended Build Sequence by Screens

## Phase 1 — Foundation and Origination

- S00 Login.
- S01 Dashboard.
- S03 Task Inbox.
- S05 Member Directory.
- S06 Member Profile.
- S10 New Loan Application.
- S12 Application Completeness Check.
- S13 Loan Request Register.
- S14 Deficiency / Rejection Note.

## Phase 2 — Appraisal and Sanction

- S15 Eligibility Assessment.
- S16 Active Member Verification.
- S17 KYC Verification.
- S18 Loan Limit Calculator.
- S19 Loan Appraisal Note.
- S20 Credit Manager Review.
- S21 Sanction Committee Workbench.
- S22 Sanction Case Detail.
- S23 Credit Sanction Register.
- S24 Special Case Approval.
- S25 Exception Register.

## Phase 3 — Documentation and Disbursement

- S26 Documentation Workspace.
- S27 Document Checklist.
- S28 Power of Attorney.
- S29 Tri-party Agreement.
- S30 SH-4 Security.
- S31 CDSL Pledge.
- S32 Term Sheet.
- S33 Loan Agreement.
- S34 Bank Verification.
- S35 Final Documentation Approval.
- S36 SAP Customer Code Request.
- S37 SAP Confirmation.
- S38 Disbursement Readiness.
- S39 Payment Initiation.
- S40 CFC Authorisation.
- S41 Disbursement Advice.

## Phase 4 — Loan Servicing and Monitoring

- S42 Loan Account 360.
- S43 Repayment Schedule.
- S44 Direct Repayment Entry.
- S45 Subsidiary Deduction Reconciliation.
- S46 Loan Ledger.
- S47 Interest Accrual.
- S48 Yearly Interest Invoice.
- S49 Interest Capitalisation.
- S50 Monitoring Dashboard.
- S51 DPD / PAR.
- S52 Reminder Management.

## Phase 5 — Default, Closure and Compliance

- S53 Default Case Detail.
- S54 Grace Period and Extension.
- S55 Note for Non-Payment.
- S56 Recovery Action Approval.
- S57 Security Invocation.
- S58 Loan Closure.
- S59 NOC Generation.
- S60 Security Return / Unpledge.
- S61 Archive.
- S62 Compliance Dashboard.
- S63 Section 186 Tracker.
- S64 NBFC Test.
- S65 KYC / Re-KYC Tracker.
- S66 Stamp Duty Register.
- S67 Money-Lending Annual Review.
- S68 Grievance Register.
- S69 Reports.
- S70-S74 Settings and Audit.

---

# 15. Final Product Interpretation

The screen design should make the SOP operationally enforceable. The system should not simply store loan data; it should actively guide users through the required sequence, prevent bypassing mandatory gates and preserve evidence for audit.

The most important product behaviours are:

1. Clear status visibility at every stage.
2. Strong document and signature controls.
3. Automated loan limit calculations with exception routing.
4. Approval matrix enforcement.
5. Separation of maker, checker, sanction and disbursement roles.
6. SAP and bank process traceability.
7. Repayment and interest accounting visibility.
8. Default handling discipline.
9. Closure evidence, including NOC and security return.
10. Compliance reporting and long-term audit readiness.

The resulting system should replace fragmented Excel, email, paper checklist and manual follow-up processes with a structured workflow in which every application, approval, document, transaction and exception is traceable from the first loan inquiry through final archival.
