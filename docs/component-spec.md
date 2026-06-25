# component-spec.md

# SFPCL Member Credit Administration & Settlement — Detailed Component Specification

## 1. Document Control

| Field | Detail |
|---|---|
| Document name | `component-spec.md` |
| Product / System | SFPCL Member Credit Administration & Loan Management System |
| Client | Sahyadri Farmers Producer Company Limited (SFPCL) |
| Business process | Member credit administration, loan sanction, documentation, disbursement, monitoring, recovery and settlement |
| Source basis | Uploaded detailed SOP, WhatsLoan summary, client brief, user flows, functional specification, information architecture, screen specification and content specification prepared in the current analysis |
| Intended audience | Product managers, UX designers, UI designers, frontend engineers, backend engineers, QA engineers, compliance reviewers, implementation leads and client-side process owners |
| Document purpose | Define the reusable functional, UI, workflow, document, data, notification and control components required to build the loan management system in a consistent, auditable and SOP-aligned manner |
| Status | Detailed working specification |

---

## 2. Purpose of This Component Specification

This document defines the component layer for a digital system that implements SFPCL's member credit administration process.

The component layer sits between:

1. **Information architecture**, which defines the system structure, modules and navigation.
2. **Screen specification**, which defines each screen and layout.
3. **Functional specification**, which defines business behaviour, workflows, rules and integrations.
4. **Content specification**, which defines labels, copy, messages, templates and borrower-facing text.

The purpose of this document is to ensure that the product is built using a controlled set of reusable, role-aware and audit-friendly components instead of one-off screens. Each component must support the lending process described in the SOP: application, eligibility, appraisal, sanction, documentation, stamping, SAP setup, disbursement, repayment, monitoring, default handling, recovery, closure, compliance and audit.

---

## 3. Component Design Principles

Every component in the system must follow these design principles.

### 3.1 Compliance First

The system handles regulated lending-like activity by a Producer Company to its members. Components must not optimise for speed at the cost of control. Components should prevent unauthorised disbursement, incomplete documentation, missing KYC, unapproved exceptions, untracked recovery actions and informal use of security documents.

### 3.2 Role-Aware Behaviour

A component must show actions, fields and data according to the user's role. A Credit Manager, Deputy Manager - Finance, Company Secretary, Compliance Team member, Senior Manager - Finance, Chief Financial Controller, CFO, Director, Accounts user, IT admin and Auditor should not have identical actions.

### 3.3 Maker-Checker by Default

Wherever the SOP expects review or approval, the component must separate:

- Data entry.
- Review.
- Approval.
- Final execution.
- Audit evidence.

Examples include appraisal submission, sanction approval, document checklist approval, SAP customer code confirmation, disbursement execution, exception approval and recovery approval.

### 3.4 Traceable State Changes

Every important state transition must create an audit trail containing:

- Previous state.
- New state.
- User.
- Role.
- Timestamp.
- Reason, if required.
- Linked record.
- Attachments or evidence, if applicable.

### 3.5 No Invisible Business Logic

Where a component calculates eligibility, limits, DPD, interest, overdue status or approval authority, the formula and inputs must be visible to authorised users. Users should be able to explain how a system result was derived.

### 3.6 Document Completeness Before Money Movement

No disbursement-related component should allow bank transfer initiation unless prerequisite controls are completed:

- Application complete.
- Eligibility passed or approved exception exists.
- Appraisal approved.
- Sanction approved.
- Required documentation completed.
- Stamping / notarisation completed where required.
- Checklist signed by required authorities.
- SAP customer code created or confirmed.
- Bank details verified.

### 3.7 Consistent Data Capture

Components should use shared primitives for member selection, date selection, currency, document upload, signature status, approval decisions, reason capture, comments, audit logs and task assignment. This avoids duplicate logic across modules.

### 3.8 Borrower-Friendly Communication

Borrower-facing content components must use clear, simple and localisable language. They must communicate application status, deficiencies, rejection reasons, sanction details, document requirements, disbursement advice, interest changes, reminders, NOC issuance and grievance responses.

### 3.9 Accessibility and Field Usability

The system may be used by back-office staff and field officers. Components should support:

- Keyboard navigation.
- Clear validation messages.
- File upload progress.
- Save draft behaviour.
- Mobile-responsive views where field use is expected.
- Readable tables with filters and export.
- Low-bandwidth tolerance for document uploads.

### 3.10 Configurability for Policy Changes

Several business rules are subject to Board approval or periodic updates. Components must be configurable for:

- Share valuation.
- Shareholding-based percentage.
- Per-share cap.
- Scale of finance per acre.
- Interest rate and benchmark.
- Penal charges.
- Approval thresholds.
- Re-KYC frequency.
- Document retention period.
- Reminder schedule.

---

## 4. Component Taxonomy

The product should be built using the following component families.

| Component Family | Purpose |
|---|---|
| Application Shell Components | Global layout, navigation, search, notifications and user identity. |
| Workflow Components | Stage tracker, task queue, approvals, state transitions and comments. |
| Data Entry Components | Forms, field groups, selectors, calculations and validation. |
| Borrower and Member Components | Member profile, active status, shareholding, nominee, land and crop records. |
| Loan Application Components | Loan request, application form, reference number, deficiency and rejection handling. |
| Eligibility and Limit Components | Eligibility checklist, active member assessment, share limit, land limit and final eligible amount. |
| Appraisal Components | Appraisal note, risk assessment, recommended sanction, evidence and review. |
| Approval Components | Sanction committee decision, approval matrix, conflict handling, exception register. |
| Documentation Components | Document checklist, document generator, e-stamp tracker, notarisation, signatures, SH-4 and CDSL pledge. |
| SAP and Finance Components | SAP customer code request, confirmation, finance posting readiness and reconciliation. |
| Disbursement Components | Bank verification, payment initiation, CFC authorisation, disbursement advice and register update. |
| Repayment Components | Direct repayment, subsidiary repayment, allocation, interest invoice and accrual. |
| Monitoring Components | DPD buckets, quarterly MIS, reminders, overdue dashboard and portfolio risk. |
| Default and Recovery Components | Grace period, extension note, non-payment note, recovery approval, SH-4 invocation and cheque action. |
| Closure Components | Full repayment, NOC, security return, unpledge and archive. |
| Compliance Components | Section 186 tracker, NBFC test, KYC audit, money-lending review, stamp duty and record retention. |
| Communication Components | SMS, email, hard-copy letters, borrower notices and internal notifications. |
| Audit Components | Activity log, evidence timeline, approval log, file history and immutable event record. |
| Admin Components | Roles, permissions, master data, templates, policy parameters and numbering sequences. |
| Utility Components | Tables, filters, badges, alerts, modals, side panels, exports and attachments. |

---

## 5. Role Model and Component Permissions

### 5.1 Core Roles

| Role | Typical Component Access |
|---|---|
| Deputy Manager - Finance | Application completeness check, KYC/document review, appraisal note preparation, borrower data entry, deficiency marking. |
| Credit Manager | Loan Request Register, eligibility review, appraisal review, rejection note, loan register, reminders, extension notes, non-payment notes, DPD review. |
| Compliance Team Member | Document preparation, checklist, PoA, tri-party agreement, SH-4, term sheet, loan agreement, bank verification letter, stamping and notarisation status. |
| Company Secretary | Documentation approval, PoA handling, stamp duty compliance, security custody, statutory compliance, grievance log, recovery documentation review. |
| Senior Manager - Finance | SAP customer code creation request processing, SAP confirmation, disbursement readiness, online payment initiation, repayment posting coordination. |
| Chief Financial Controller | Final bank authorisation / disbursement approval, finance oversight, payment execution evidence. |
| CFO | Sanction committee member, approval authority, exception approval, quarterly MIS, Section 186 and NBFC monitoring review. |
| Director / Executive Director | Sanction approval, special case approval, high-value approval, Board-level visibility. |
| Accounts Head / Accounts User | Interest accrual, repayment posting, DPD reports, accounting MIS, interest invoice support. |
| Sales Team | Year-end interest invoice preparation where SOP assigns this responsibility. |
| IT Admin | Role management, access control, SAP interface configuration, master data settings. |
| Auditor / Internal Auditor | Read-only access to audit trail, loan files, registers, evidence and compliance reports. |
| Field Officer, if implemented | Application assistance, KYC collection, borrower communication, visit logs and borrower declarations. |

### 5.2 Permission Patterns

| Permission Pattern | Description |
|---|---|
| Create | User can create a new record or task. |
| Edit Draft | User can edit records not yet submitted. |
| Submit | User can move a draft into formal workflow. |
| Review | User can inspect, comment, ask for corrections or recommend. |
| Approve | User can approve according to authority matrix. |
| Reject | User can reject with mandatory reason. |
| Return for Correction | User can send back with deficiency reason. |
| Execute | User can execute operational step, such as disbursement initiation. |
| Confirm | User can mark an external process completed, such as SAP customer code creation. |
| View Sensitive | User can see KYC, bank and security documents. |
| Download Sensitive | User can download sensitive documents where permitted. |
| Audit View | User can see immutable logs but not change records. |
| Configure | User can change master data and policy parameters subject to approval. |

### 5.3 Role-Aware Component Behaviour

Every business component must support at least four access modes:

| Mode | Behaviour |
|---|---|
| Editable | Fields and actions enabled based on role and current state. |
| Review-only | Fields locked; comments and return / approve actions available. |
| Read-only | No edits or decisions; view information only. |
| Redacted | Sensitive fields masked or hidden, such as Aadhaar, PAN, bank account, cheque details and security document scans. |

---

## 6. Shared System Components

## 6.1 Application Shell

### Purpose

Provides the global container for the loan management system.

### Used By

All authenticated users.

### Contains

- Header.
- Sidebar navigation.
- Global search.
- Notification icon.
- User profile menu.
- Environment label, if staging / UAT / production.
- Breadcrumb area.
- Page title area.
- Main content region.
- Footer or version marker.

### Behaviour

- Sidebar items should be role-aware.
- Users should only see modules they can access.
- Active module should be highlighted.
- Header should remain consistent across all screens.
- Shell should support responsive collapse for tablet and smaller screens.
- Global search should search members, loan applications, loan accounts, document files and registers based on permissions.

### Required States

| State | Behaviour |
|---|---|
| Loading | Skeleton layout displays while profile and permissions load. |
| Authenticated | Shows full shell according to role. |
| Unauthorised | Redirects to access denied or login. |
| Session expiring | Shows warning and option to continue session. |
| Offline / network failure | Shows limited offline warning; disables write actions. |

---

## 6.2 Sidebar Navigation Component

### Purpose

Provides primary navigation aligned to the information architecture.

### Primary Sections

- Dashboard.
- Members.
- Loan Applications.
- Appraisal.
- Sanctions.
- Documentation.
- SAP & Disbursement.
- Repayments.
- Monitoring.
- Defaults & Recovery.
- Closure.
- Compliance.
- Reports.
- Grievances.
- Administration.

### Role-Based Examples

| Role | Visible Navigation Emphasis |
|---|---|
| Credit Manager | Dashboard, Loan Applications, Appraisal, Sanctions, Monitoring, Defaults, Reports. |
| Compliance Team | Documentation, Compliance, Grievances, Closure. |
| Senior Manager - Finance | SAP & Disbursement, Repayments, Reports. |
| CFO | Dashboard, Sanctions, Exceptions, Compliance, Reports, Monitoring. |
| Auditor | Reports, Compliance, Audit Trail, Loan File View. |

### Behaviour

- Navigation should support count badges, such as `12 pending approvals` or `4 overdue tasks`.
- Restricted sections must not be visible unless user has access.
- Deep links to restricted sections must show access denied.

---

## 6.3 Breadcrumb Component

### Purpose

Shows the user's location in the hierarchy.

### Example

```text
Loan Applications > LO00000043 > Documentation > Checklist
```

### Behaviour

- Each breadcrumb segment should be clickable where user has permission.
- Last segment should be plain text.
- For records, use stable identifiers such as loan application number, member ID or loan account number.

---

## 6.4 Page Header Component

### Purpose

Standardises top section of every page.

### Contains

- Page title.
- Subtitle or record context.
- Status badge.
- Primary action button.
- Secondary actions menu.
- Last updated timestamp.
- Assigned owner, where applicable.

### Example for Loan Application

| Element | Example |
|---|---|
| Title | Loan Application `LO00000043` |
| Subtitle | Member: Ramesh Patil · Farmer · Folio: F-00831 |
| Badge | `Pending Credit Manager Review` |
| Primary action | `Submit to Sanction Committee` |
| Secondary actions | Save Draft, Return for Correction, Generate Rejection Note, View Audit Trail |

---

## 6.5 Global Search Component

### Purpose

Allows authorised users to find core records quickly.

### Searchable Objects

- Member name.
- Member ID.
- Folio number.
- Loan application number.
- Loan account number.
- SAP customer code.
- PAN, if user has sensitive search permission.
- Aadhaar partial / masked, if permitted.
- Village / district.
- Subsidiary repayment reference.
- Document title.
- Checklist ID.

### Behaviour

- Search results grouped by object type.
- Sensitive fields masked in results.
- Search should honour role permissions.
- Results should show status and owner.

### Empty State

```text
No matching record found. Check the spelling, application number or member ID.
```

---

## 6.6 Notification Centre Component

### Purpose

Shows workflow tasks, approval requests, deficiencies, reminders and system notices.

### Notification Types

| Type | Example |
|---|---|
| Task | Loan Appraisal Note awaiting review. |
| Approval | Loan above ₹5,00,000 awaiting CFO + two Director approval. |
| Deficiency | Borrower Aadhaar copy missing. |
| Compliance | Re-KYC due within 30 days. |
| Disbursement | SAP customer code confirmed. |
| Repayment | Repayment received and pending allocation. |
| Overdue | Scheduled principal repayment missed. |
| Exception | Requested loan exceeds permissible limit. |
| Closure | NOC pending after full repayment. |

### Behaviour

- Clicking a notification opens relevant record.
- Notification should show due date, priority and assigned role.
- Completed tasks should be archived.
- Approval notifications should not expose sensitive document content in notification preview.

---

## 6.7 Task Queue Component

### Purpose

Provides users with actionable work lists.

### Required Filters

- Assigned to me.
- Assigned to my role.
- Overdue.
- Due today.
- Priority.
- Stage.
- Member type.
- Loan amount range.
- Pending approval.
- Returned for correction.
- Exception pending.

### Required Columns

| Column | Description |
|---|---|
| Task ID | System task identifier. |
| Record | Loan application / member / compliance record. |
| Stage | Current workflow stage. |
| Task type | Review, approve, correct, confirm, execute. |
| Assigned role | Role responsible. |
| Assigned user | Named user, if assigned. |
| Due date | TAT-driven due date. |
| Ageing | Time since task creation. |
| Priority | Normal / High / Critical. |
| Action | Open task. |

---

## 6.8 Status Badge Component

### Purpose

Shows current status of records consistently.

### Common Statuses

| Status | Meaning |
|---|---|
| Draft | Record created but not submitted. |
| Incomplete | Required fields or documents missing. |
| Under Review | Submitted for role review. |
| Returned for Correction | Reviewer requested changes. |
| Rejected | Application or request rejected. |
| Approved | Approved by required authority. |
| Pending Documentation | Sanction approved; documentation not complete. |
| Documentation Complete | All required documents complete. |
| Pending SAP Code | Awaiting SAP customer code creation. |
| Ready for Disbursement | All gates complete; finance can initiate payment. |
| Disbursement Initiated | Payment initiated by Senior Manager - Finance. |
| Disbursed | Bank transfer completed and confirmed. |
| Active | Loan is live and in repayment / monitoring. |
| Overdue | Repayment obligation missed. |
| In Grace Period | Three-month grace period active. |
| Extension Granted | One-year non-intentional default extension granted. |
| Recovery Under Review | Non-payment note sent for action approval. |
| Closed | Fully repaid and closure actions completed. |
| Archived | Retention archive state. |

### Behaviour

- Badge wording must match content-spec names.
- Badge state must be generated from workflow status, not manually typed.
- Badge should expose tooltip explaining the status.

---

## 6.9 Action Bar Component

### Purpose

Presents available actions for a record.

### Behaviour

- Primary action should be the next expected workflow action.
- Secondary actions should be placed in overflow menu.
- Disabled actions must show reason on hover / tap.
- Destructive actions require confirmation modal and reason.

### Example Disabled Action

Button: `Initiate Disbursement` disabled.

Tooltip:

```text
Disbursement cannot be initiated because the Loan Agreement is not notarised and SAP customer code is pending.
```

---

## 6.10 Comments and Internal Notes Component

### Purpose

Captures discussion, clarification and review remarks against records.

### Features

- Add comment.
- Mention user or role.
- Attach file.
- Mark as internal only.
- Mark as borrower-facing note, if allowed.
- Filter by stage.
- Sort newest / oldest.

### Audit Requirement

Comments should be immutable after a configurable edit window. Edits, if allowed, must retain version history.

---

## 6.11 Audit Timeline Component

### Purpose

Displays chronological history of all material events.

### Events to Capture

- Application created.
- Application submitted.
- Reference number generated.
- Document uploaded.
- Eligibility calculation run.
- Appraisal note created.
- Review completed.
- Approval / rejection.
- Exception raised.
- Exception approved / rejected.
- Document generated.
- Document signed.
- Stamp duty marked complete.
- Notarisation complete.
- SAP request sent.
- SAP customer code confirmed.
- Disbursement initiated.
- CFC approval complete.
- Payment completed.
- Repayment received.
- Interest invoice generated.
- DPD bucket changed.
- Reminder sent.
- Grace period started.
- Extension granted.
- Recovery action approved.
- NOC issued.
- Security returned.
- File archived.

### Required Fields Per Event

| Field | Description |
|---|---|
| Event type | Application, approval, document, repayment, recovery, closure, compliance. |
| Event description | Human-readable event message. |
| Actor | User who performed action. |
| Actor role | Role at time of action. |
| Timestamp | Date and time. |
| Previous value | Prior state, where applicable. |
| New value | New state, where applicable. |
| Reason | Mandatory for rejection, correction, exception, override and recovery action. |
| Evidence | Linked documents or attachments. |

---

## 7. Dashboard Components

## 7.1 Executive Dashboard KPI Cards

### Purpose

Provide CFO, Directors and senior management with portfolio summary.

### KPI Cards

| KPI | Description |
|---|---|
| Total applications received | Count of applications in selected period. |
| Applications pending completeness check | Stage 1 incomplete / pending review. |
| Appraisals pending | Applications awaiting appraisal or Credit Manager review. |
| Sanctions pending | Applications awaiting Sanction Committee decision. |
| Documentation pending | Approved loans with incomplete documentation. |
| Ready for disbursement | Loans passing all pre-disbursement gates. |
| Disbursed amount | Total amount disbursed in selected period. |
| Active loan book | Outstanding principal and interest, where configured. |
| Overdue loans | Loans past due by configured categories. |
| DPD ageing | 1-2 years, 2-3 years, more than 3 years as per SOP monitoring. |
| Exceptions pending | Loans over limit or policy deviation awaiting approval. |
| Re-KYC due | Members due for periodic KYC refresh. |
| NOC pending | Fully repaid loans with closure action pending. |

### Filters

- Date range.
- Crop.
- District / location.
- Member type.
- Loan status.
- Subsidiary repayment channel.
- Loan amount bucket.
- Approval authority.

---

## 7.2 Operational Dashboard Component

### Purpose

Shows daily work for operational teams.

### Sections

- My pending tasks.
- Overdue tasks.
- Recently returned applications.
- Applications approaching 2-day appraisal TAT.
- Documentation files pending CS review.
- SAP code requests pending.
- Disbursement files awaiting CFC approval.
- Repayments pending allocation.
- Borrower reminders due.

### Behaviour

- Each item links directly to the relevant screen.
- Users see only tasks they can act on.
- High-risk or SLA-breached tasks are visually prioritised.

---

## 7.3 Compliance Dashboard Component

### Purpose

Supports Company Secretary, CFO and auditors in compliance monitoring.

### Cards / Widgets

| Widget | Purpose |
|---|---|
| Section 186 limit tracker | Shows current loan exposure against statutory limit. |
| NBFC principal business test | Shows financial assets and financial income ratios. |
| KYC completeness | Shows KYC complete, incomplete and re-KYC due counts. |
| Stamp duty pending | Shows documents missing stamping / notarisation. |
| Money-lending law review | Tracks annual legal opinion / review. |
| Record retention | Shows records approaching archive or destruction milestone. |
| Grievance status | Shows open, overdue and resolved grievances. |
| Exceptions register | Shows open deviations and approvals. |

---

## 8. Borrower and Member Components

## 8.1 Member Search and Selector

### Purpose

Allows users to select an existing member before creating a loan application.

### Search Inputs

- Member name.
- Member ID.
- Folio number.
- PAN.
- Aadhaar partial / masked search, if permitted.
- Village.
- FPC name.
- Producer institution name.
- Mobile number.

### Result Display

| Field | Description |
|---|---|
| Member name | Individual or institutional name. |
| Member type | Individual farmer / FPC / producer institution. |
| Folio number | Share folio reference. |
| Active status | Active / inactive / needs verification. |
| Shareholding | Number of shares held. |
| Existing loan status | No active loan / active loan / default / closed. |
| KYC status | Complete / incomplete / expired. |

### Behaviour

- If member has default, the selector must show a warning.
- If member is inactive, creation of loan application should be blocked or require exception route, according to policy.
- If no member found, system must not allow direct loan application unless member onboarding workflow exists.

---

## 8.2 Member Summary Card

### Purpose

Displays compact borrower context across screens.

### Fields

- Member name.
- Member type.
- Member ID.
- Folio number.
- Number of shares.
- Active / inactive status.
- KYC status.
- Existing defaults.
- Land area.
- Primary crop.
- Mobile number.
- Email.
- Linked subsidiary / producer institution, where applicable.

### Usage

- Application detail.
- Appraisal note.
- Sanction review.
- Documentation checklist.
- Disbursement screen.
- Repayment ledger.
- Default review.

---

## 8.3 Member Profile Component

### Purpose

Provides full member record.

### Tabs

1. Overview.
2. Identity and KYC.
3. Shareholding.
4. Active member evidence.
5. Land and crop records.
6. Bank details.
7. Nominee details.
8. Loan history.
9. Produce supply history.
10. Documents.
11. Communications.
12. Audit trail.

### Key Validations

- PAN format.
- Aadhaar format and masking.
- Nominee age must not be minor.
- Bank IFSC format.
- Duplicate PAN / Aadhaar detection.
- Existing default warning.
- Re-KYC due date calculation.

---

## 8.4 Active Member Assessment Component

### Purpose

Determines whether borrower meets active member criteria defined in AoA and SOP.

### Inputs

| Input | Description |
|---|---|
| Member type | Individual or Producer Institution. |
| Service availed | Whether member has availed services of SFPCL / subsidiary / step-down subsidiary. |
| Produce supplied | Whether member supplied primary produce. |
| Supply duration | Continuous financial years of supply. |
| New member relaxation | Whether one-year supply relaxation applies. |
| Employment / service contribution | For Producer Member service route, if applicable. |
| Evidence | Procurement records, supply records, service records or declaration. |

### Rules for Individual Member

- Must avail services directly or indirectly during membership.
- Must supply primary produce for four continuous financial years to SFPCL, subsidiaries, step-down subsidiaries or through a Producer Institution member.
- New / recent members may qualify if they supplied produce for at least one year.
- Producer Member may also qualify if services were provided in employment or other capacity for three continuous years to SFPCL / subsidiaries / step-down subsidiaries.

### Rules for Producer Institution

- Must be a member of SFPCL.
- Must avail services directly or indirectly.
- Must supply primary produce for four continuous financial years.
- New / recent producer companies may qualify if they supplied produce for at least one year.

### Outputs

- Active.
- Inactive.
- Needs manual verification.
- Eligible under relaxation.
- Evidence missing.

### Required Audit

- Rule evaluated.
- Evidence used.
- User who confirmed.
- Date of confirmation.
- Override reason, if any.

---

## 8.5 Shareholding Component

### Purpose

Captures and displays shares held by borrower and supports loan limit calculation and security handling.

### Fields

- Folio number.
- Number of shares held.
- Share certificate numbers, if physical.
- Demat account / BO ID, if demat.
- Share status: physical / demat / mixed.
- Latest share valuation.
- Approved percentage for loan limit.
- Per-share cap, if applicable.
- Pledged status.
- SH-4 required flag.
- CDSL pledge required flag.

### Behaviour

- If shares are physical, SH-4 documentation component is required.
- If shares are demat, CDSL pledge component is required.
- Future shares to be pledged should be flagged for legal / compliance tracking.

---

## 8.6 Nominee Details Component

### Purpose

Captures nominee information required in application and documentation.

### Fields

- Nominee full name.
- Age.
- Date of birth, if implemented.
- Gender.
- Aadhaar number.
- PAN.
- Mobile number.
- Relationship with borrower.
- Address.
- KYC documents.
- Signature status.

### Validation

- Nominee must not be a minor.
- PAN and Aadhaar required as per SOP.
- Nominee signature required on application, PoA and Term Sheet where applicable.

---

## 8.7 Land and Crop Record Component

### Purpose

Captures agricultural eligibility evidence and supports land-based loan limit calculation.

### Fields

- 7/12 extract document.
- Land area under cultivation.
- Crop plan.
- Primary crop.
- Crop season.
- District / village.
- Land ownership / cultivation status.
- Per-acre scale of finance.
- Land-based loan limit.

### Behaviour

- Land area must be numeric and positive.
- Crop plan must be uploaded before credit assessment completion.
- Per-acre scale must be read from policy configuration for the relevant period.
- Current SOP cap is ₹20,000 per acre unless changed by Board-approved policy configuration.

---

## 8.8 KYC Document Status Component

### Purpose

Shows KYC completeness for borrower and nominee.

### Required Documents

| Person | Required Documents |
|---|---|
| Borrower | PAN, Aadhaar, share certificate, land documents, crop plan, six-month bank statement. |
| Nominee | PAN, Aadhaar and application / document signatures. |
| Witness | PAN and Aadhaar; must be existing SFPCL shareholder. |
| Guarantor, if required | ID, consent and details, subject to final policy clarification. |

### Statuses

- Not started.
- Uploaded.
- Under verification.
- Verified.
- Rejected.
- Expired.
- Re-KYC due.

### Behaviour

- Missing borrower PAN / Aadhaar blocks appraisal completion.
- Missing nominee KYC blocks documentation completion.
- Missing witness KYC blocks SH-4 / loan agreement completion.

---

## 9. Loan Application Components

## 9.1 Loan Application Form Component

### Purpose

Captures loan request from borrower.

### Sections

1. Borrower identification.
2. Shareholding details.
3. Loan amount requested.
4. Loan purpose.
5. Nominee details.
6. KYC upload.
7. Land and crop details.
8. Bank statement upload.
9. Borrower declarations and consents.
10. Applicant and nominee signatures.

### Required Fields

- Borrower member ID / folio number.
- Number of shares.
- Required loan amount.
- Loan purpose.
- Nominee name.
- Nominee age.
- Nominee Aadhaar.
- Nominee PAN.
- Nominee gender.
- PAN copy.
- Aadhaar copy.
- Share certificate copy.
- 7/12 extract.
- Crop plan.
- Six-month bank statement.

### Validation

- Required loan amount must be greater than zero.
- Loan purpose must be crop production or agriculture-related activity only.
- Nominee must not be minor.
- Mandatory documents must be uploaded or deficiency must be recorded.
- Borrower and nominee signatures must be captured before application is considered complete.

### Outputs

- Draft application.
- Submitted application.
- Loan application number.
- Loan Request Register entry.

---

## 9.2 Application Reference Number Component

### Purpose

Generates unique loan application number.

### Format

```text
LO00000001
```

### Behaviour

- Sequential numbering.
- No duplication.
- Number generated after completeness acceptance or at first formal registration, depending on final business decision.
- Number written to Loan Request Register.
- Number displayed on application original copy equivalent in digital system.

### Admin Configuration

- Prefix: `LO`.
- Numeric length: 8 digits.
- Next sequence number.
- Financial-year reset flag, if future policy requires.

---

## 9.3 Loan Request Register Component

### Purpose

Digital version of the Excel Loan Request Register maintained by Credit Manager.

### Columns

- Application reference number.
- Date of receipt.
- Borrower name.
- Member ID / folio number.
- Member type.
- Loan amount requested.
- Application channel.
- Application completeness status.
- Deputy Manager - Finance reviewer.
- Credit Manager owner.
- Current stage.
- Rejection / deficiency status.
- TAT status.

### Actions

- Create application.
- Open application.
- Mark incomplete.
- Generate deficiency note.
- Submit for appraisal.
- Export register.

---

## 9.4 Completeness Check Component

### Purpose

Allows Deputy Manager - Finance to verify whether the application package is complete.

### Checklist Items

- Loan Application Form filled.
- Applicant signature present.
- Nominee signature present.
- Folio number provided.
- Number of shares provided.
- Required loan amount provided.
- Nominee details complete.
- Borrower PAN uploaded.
- Borrower Aadhaar uploaded.
- Nominee PAN uploaded.
- Nominee Aadhaar uploaded.
- Share certificates uploaded.
- Land documents / 7/12 extract uploaded.
- Crop plan uploaded.
- Six-month bank statement uploaded.

### Actions

- Mark complete.
- Return for deficiency.
- Generate deficiency / rejection note.
- Save internal comment.

### Completion Rule

Application cannot proceed to appraisal unless completeness is confirmed or a documented exception exists.

---

## 9.5 Deficiency Note Component

### Purpose

Communicates missing or incorrect application details before resubmission.

### Fields

- Application number.
- Borrower name.
- Deficiency category.
- Specific deficiency.
- Required correction.
- Submission deadline, if applicable.
- Communication mode: email / courier / SMS / in person.
- Prepared by.
- Date.

### Common Deficiencies

- Missing PAN.
- Missing Aadhaar.
- Missing share certificate.
- Missing 7/12 extract.
- Missing crop plan.
- Missing six-month bank statement.
- Nominee minor.
- Signature missing.
- Loan purpose not agriculture-related.

---

## 9.6 Rejection Note Component

### Purpose

Generates formal rejection communication when the application is rejected at credit assessment or Sanction Committee stage.

### Required Fields

- Application number.
- Borrower name.
- Rejection stage.
- Rejection reason.
- Corrective criteria, if reapplication is allowed.
- Reapplication statement.
- Communication mode.
- Prepared by.
- Approved by, if required.
- Date.

### Behaviour

- Rejection reason is mandatory.
- Rejection must be linked to application stage.
- Borrower should be allowed to reapply after fulfilling criteria, unless a policy block exists.

---

## 10. Eligibility and Loan Limit Components

## 10.1 Eligibility Checklist Component

### Purpose

Confirms borrower eligibility before appraisal is submitted to Sanction Committee.

### Checklist Rules

| Rule | Required Result |
|---|---|
| Active member | Must be active or approved under relaxation. |
| No existing default | Must not be in default for any SFPCL, subsidiary or associate company loan. |
| KYC complete | Required KYC documents submitted. |
| Land documents submitted | 7/12 extract required. |
| Bank statement submitted | Six-month statement required. |
| Crop plan submitted | Required. |
| Loan purpose valid | Crop production / agricultural activity only. |
| Borrower agrees to terms | Term Sheet and Loan Agreement acceptance required later. |

### Outputs

- Eligible.
- Not eligible.
- Eligible with exception.
- Pending information.

### Behaviour

- Failed eligibility should trigger rejection or deficiency flow.
- Exceptions require authority capture and Exception Register entry.

---

## 10.2 Existing Default Check Component

### Purpose

Checks whether borrower is in default with SFPCL, subsidiary or associate company.

### Data Sources

- SFPCL loan ledger.
- Subsidiary repayment records.
- Associate company loan records, if integrated.
- Manual confirmation, if external data not integrated.

### Outputs

- No default found.
- Default found.
- Data unavailable / manual verification required.

### Behaviour

- If default is found, application should be blocked unless policy exception is approved.
- Default evidence should be visible to Credit Manager and approvers.

---

## 10.3 Loan Purpose Validator Component

### Purpose

Ensures requested loan purpose is related to crop production and agricultural activity only.

### Allowed Categories

- Crop production.
- Farm inputs.
- Agricultural activity.
- Crop-specific production requirement.
- Other productive agriculture purpose approved by policy.

### Blocked / Warning Categories

- Personal consumption.
- Non-agricultural business.
- Loan repayment to another lender, unless explicitly approved.
- Non-productive use.
- Unknown / vague purpose.

### Behaviour

- Loan purpose must be selected from structured list and described in free text.
- Invalid purpose should block appraisal submission.

---

## 10.4 Shareholding-Based Limit Calculator

### Purpose

Calculates loan entitlement based on shareholding.

### Formula from SOP

```text
Loan Limit = Number of shares held × 30% of valuation per share
```

### Configuration Caveat

The SOP also refers to 10% of share valuation and a current result of ₹200 per share. Because the SOP contains this inconsistency, the component must be configurable and display the active Board-approved rule.

### Inputs

- Number of shares held.
- Latest approved share valuation.
- Board-approved percentage.
- Per-share cap, if configured.
- Effective date of policy.

### Outputs

- Shareholding-based limit.
- Formula shown to user.
- Policy version used.
- Warning if current rule is flagged unresolved.

### Required Display

```text
Shareholding limit was calculated using Policy Version [X], effective from [date].
```

---

## 10.5 Agricultural Land-Based Limit Calculator

### Purpose

Calculates loan entitlement based on cultivated land area and scale of finance.

### Formula

```text
Loan Limit = Per-acre cost of cultivation × Farmer's land area under cultivation
```

### Current SOP Cap

```text
₹20,000 per acre
```

### Inputs

- Land area under cultivation.
- Crop.
- Scale of finance per acre.
- Applicable financial year.
- Current cap.

### Outputs

- Land-based limit.
- Formula shown to user.
- Scale of finance policy version.

---

## 10.6 Final Eligible Loan Amount Component

### Purpose

Compares shareholding-based and land-based limits.

### Formula

```text
Final Eligible Loan Amount = Lower of Shareholding-Based Limit and Agricultural Land-Based Limit
```

### Display Requirements

| Item | Display |
|---|---|
| Requested amount | Borrower requested amount. |
| Shareholding limit | Calculated amount. |
| Land-based limit | Calculated amount. |
| Final eligible amount | Lower amount. |
| Difference | Requested amount minus eligible amount, if requested exceeds eligible. |
| Exception required | Yes / No. |

### Behaviour

- If requested amount is less than or equal to final eligible amount, no limit exception required.
- If requested amount exceeds final eligible amount, exception route required with reason and CFO + two Director approval as per SOP.

---

## 10.7 Policy Rule Explainer Component

### Purpose

Explains why the system calculated or blocked a result.

### Example

```text
The borrower requested ₹6,50,000. The final eligible limit is ₹4,80,000 because the land-based limit is lower than the shareholding-based limit. Approval above the permissible limit requires CFO + two Directors and an Exception Register entry.
```

---

## 11. Appraisal Components

## 11.1 Loan Appraisal Note Component

### Purpose

Creates the formal appraisal note prepared by Deputy Manager - Finance and reviewed by Credit Manager.

### Sections

1. Application summary.
2. Borrower profile.
3. Membership and active status.
4. KYC status.
5. Shareholding details.
6. Land and crop details.
7. Requested loan amount.
8. Loan limit calculation.
9. Purpose of loan.
10. Existing loan / default check.
11. Repayment capacity assessment.
12. Risk assessment.
13. Recommended amount.
14. Recommended tenure.
15. Recommended interest and charges, if available.
16. Recommended security.
17. Exceptions / deviations.
18. Final recommendation.
19. Prepared by.
20. Reviewed by.

### TAT

The appraisal note must be prepared and submitted to Sanction Committee within two days from receipt of application.

### Actions

- Save draft.
- Submit to Credit Manager.
- Return to Deputy Manager - Finance.
- Submit to Sanction Committee.
- Generate PDF / document version.
- View audit trail.

### Validations

- Cannot submit if eligibility incomplete.
- Cannot submit if loan limit calculation missing.
- Cannot submit if risk assessment missing.
- Cannot submit if recommended amount exceeds eligible amount without exception flag.

---

## 11.2 Risk Assessment Component

### Purpose

Records borrower-specific, market and operational risks considered by Sanction Committee.

### Risk Categories

- Borrower default risk.
- Crop risk.
- Market price risk.
- Operational risk.
- Documentation risk.
- KYC risk.
- Subsidiary repayment dependency risk.
- Security enforceability risk.

### Fields

- Risk category.
- Risk description.
- Risk rating: Low / Medium / High / Critical.
- Mitigation measure.
- Residual risk.
- Reviewer comments.

### Behaviour

- High or critical risk should require additional remarks from Credit Manager.
- Risk assessment summary should appear in Sanction Committee view.

---

## 11.3 Repayment Capacity Component

### Purpose

Captures evidence that borrower can repay the loan.

### Inputs

- Six-month bank statement.
- Land area.
- Crop plan.
- Produce supply history.
- Expected crop proceeds.
- Existing liabilities, if captured.
- Past repayment history.

### Outputs

- Repayment capacity summary.
- Supporting evidence list.
- Appraisal remarks.

### Notes

The SOP requires due diligence and risk evaluation but does not define a formal Debt Service Coverage Ratio. Therefore, any scoring model must be configurable and marked as internal policy if introduced.

---

## 11.4 Recommendation Summary Component

### Purpose

Provides final credit recommendation for approvers.

### Fields

- Recommended sanction amount.
- Recommended tenure.
- Short-term / long-term classification.
- Recommended interest rate.
- Repayment date.
- Security required.
- Exception required.
- Key conditions before disbursement.
- Recommendation: Approve / Reject / Approve with conditions.

---

## 12. Sanction and Approval Components

## 12.1 Sanction Committee Review Component

### Purpose

Allows authorised Sanction Committee members to review and approve / reject loan application.

### Review Checklist

- Eligibility verification.
- Loan amount assessment.
- Purpose of loan.
- Compliance checks.
- Past borrowing history.
- Risk assessment.
- Documentation completeness at current stage.
- Exceptions.

### Actions

- Approve.
- Reject.
- Return for clarification.
- Request additional documents.
- Approve with conditions.
- Record abstention.

### Decision Requirements

- Decision reason mandatory for rejection.
- Approval comments mandatory for exceptions.
- Conditions must be recorded if approved conditionally.
- Decision must be written to Credit Sanction Register.

---

## 12.2 Approval Matrix Engine

### Purpose

Determines required approval authority.

### SOP Rules

| Scenario | Required Authority |
|---|---|
| Loan up to ₹5,00,000 per member | CFO + one Director. |
| Loan above ₹5,00,000 per member | CFO + two Directors. |
| Loan exceeding maximum permissible limit applicable to member | CFO + two Directors and Exception Register reason. |
| Director / Sanction Committee member / relative as borrower | Remaining Sanction Committee members and member approval in general meeting. |

### Inputs

- Requested amount.
- Recommended amount.
- Final eligible loan amount.
- Whether requested amount exceeds permissible limit.
- Borrower relationship to Director / Sanction Committee member.
- Borrower relationship to relative.

### Outputs

- Required approvers.
- Approval route.
- Exception flag.
- Conflict-of-interest flag.
- General meeting approval requirement.

---

## 12.3 Approval Decision Card

### Purpose

Captures individual approver decision.

### Fields

- Approver name.
- Role.
- Decision: Approve / Reject / Abstain / Return.
- Date and time.
- Comments.
- Digital signature / acknowledgement.

### Behaviour

- Approver cannot approve if they are marked as borrower or conflict party.
- Approver cannot change decision after final approval unless formal rollback is permitted by admin policy.
- All decisions remain visible in audit trail.

---

## 12.4 Credit Sanction Register Component

### Purpose

Records sanction decisions in structured register format.

### Fields

- Sanction entry number.
- Application number.
- Borrower name.
- Member ID / folio number.
- Loan amount requested.
- Loan amount sanctioned.
- Final eligible amount.
- Approval authority.
- Approvers.
- Decision.
- Decision date.
- Conditions.
- Rejection reasons.
- Exception reference, if any.
- Conflict-of-interest notes, if any.

### Actions

- View entry.
- Export register.
- Attach approval minutes.
- Link to Board / general meeting approval where required.

---

## 12.5 Exception Register Component

### Purpose

Records deviations from standard policy, especially loans exceeding borrower permissible limit.

### Required Fields

- Exception ID.
- Application number.
- Exception type.
- Policy rule breached.
- Standard value / limit.
- Proposed value / amount.
- Reason.
- Risk assessment.
- Mitigation.
- Requested by.
- Approved by.
- Approval date.
- Conditions.
- Status.

### Common Exception Types

- Loan amount exceeds final eligible amount.
- Loan amount exceeds configured per-share cap.
- Missing document temporarily accepted.
- KYC pending but conditional review requested.
- Active member evidence incomplete.
- Director / related party special case.

### Behaviour

- Exceptions should not silently bypass controls.
- Each exception must be linked to formal approval.
- Open exceptions should block disbursement unless explicitly permitted by approval condition.

---

## 12.6 Conflict-of-Interest Component

### Purpose

Handles cases where Sanction Committee member, Director or relative is borrower.

### Fields

- Borrower is Director: Yes / No.
- Borrower is Sanction Committee member: Yes / No.
- Borrower is relative of Director / committee member: Yes / No.
- Related person name.
- Relationship.
- Conflicted approvers.
- Remaining approvers.
- General meeting approval required: Yes / No.
- General meeting approval evidence.

### Behaviour

- Conflicted approver cannot approve.
- System must require approval of remaining eligible Sanction Committee members.
- System must require member approval in general meeting before final sanction, as specified by SOP.

---

## 13. Documentation and Stamping Components

## 13.1 Documentation Workspace Component

### Purpose

Central workspace for Compliance Team to prepare, upload, verify, approve and track loan documents.

### Layout

- Borrower summary.
- Sanction summary.
- Required documents checklist.
- Document generation panel.
- Upload panel.
- Signature tracker.
- Stamp / notarisation tracker.
- Approval checklist.
- Comments and audit timeline.

### Required Documents

- PAN and Aadhaar copy of witness.
- Cancelled cheque.
- Blank-dated cheque.
- Power of Attorney.
- Declaration / Tri-party Agreement.
- SH-4, if physical shares.
- CDSL pledge evidence, if demat shares.
- Term Sheet.
- Loan Agreement.
- Bank Verification Letter, if signature mismatch.
- Checklist.

---

## 13.2 Document Checklist Component

### Purpose

Acts as the digital index of all required documentation.

### Fields per Checklist Item

- Document name.
- Required: Yes / Conditional / No.
- Condition.
- Responsible role.
- Document status.
- Uploaded / generated file.
- Signature status.
- Stamp duty status.
- Notarisation status.
- Verification status.
- Verified by.
- Verification date.
- Deficiency notes.

### Checklist Statuses

- Not required.
- Pending.
- Draft prepared.
- Generated.
- Uploaded.
- Signed.
- Stamped.
- Notarised.
- Verified.
- Rejected.
- Waived by approved exception.

### Gating Rule

Documentation cannot be marked complete until all required checklist items are verified or waived under approved exception.

---

## 13.3 Document Generator Component

### Purpose

Generates standard legal and process documents from approved templates and loan data.

### Documents Generated

- Power of Attorney.
- Declaration / Tri-party Agreement.
- Term Sheet.
- Loan Agreement.
- Bank Verification Letter.
- Rejection Note.
- Disbursement Advice.
- Interest Rate Change Notice.
- Reminder Notice.
- Extension Note.
- Note for Non-Payment.
- NOC.

### Inputs

- Borrower data.
- Nominee data.
- Witness data.
- Loan sanction data.
- Interest terms.
- Security details.
- Repayment terms.
- Subsidiary details.
- Document template version.

### Behaviour

- Generated document must store template version.
- Any manual edit must be captured.
- Final generated PDF / file must be locked after execution.
- Document generation must respect individual vs FPO template variations.

---

## 13.4 Power of Attorney Component

### Purpose

Tracks creation and execution of PoA in favour of Company Secretary.

### Requirements

- Prepared by Compliance Team.
- In favour of Company Secretary.
- Authorises CS to initiate sale of shares in case of default.
- Signed by farmer and nominee.
- Executed on ₹500 stamp paper.
- Notarised.

### Fields

- PoA generated date.
- Stamp paper number.
- Stamp value.
- Notarisation date.
- Borrower signature status.
- Nominee signature status.
- CS verification status.
- Original custody location.

---

## 13.5 Tri-Party Agreement Component

### Purpose

Tracks borrower agreement with SFPCL and relevant subsidiary company for loan repayment deduction from produce proceeds.

### Parties

- Borrower.
- SFPCL.
- Relevant subsidiary company.

### Key Business Logic

- Borrower sells produce to subsidiary.
- Subsidiary deducts loan repayment amount from produce payment.
- Deducted amount may include principal, interest and other dues.
- Subsidiary transfers deducted amount to SFPCL.
- SFPCL adjusts amount toward loan obligation.

### Fields

- Subsidiary company name.
- Borrower consent captured.
- Nominee signature status, where applicable.
- Agreement generated date.
- Agreement signed date.
- Verification status.
- Effective date.

---

## 13.6 SH-4 Component

### Purpose

Tracks Share Transfer Form SH-4 where borrower holds physical shares.

### Required Conditions

- Required only for physical shareholding.
- Signed by borrower / shareholder.
- Signed by valid witness.
- Witness must be existing SFPCL shareholder.
- Held as security and returned on loan closure.

### Fields

- SH-4 required flag.
- Share certificate details.
- Borrower signature status.
- Witness signature status.
- Witness PAN / Aadhaar status.
- Physical custody location.
- Return status on closure.

### Important Control

SH-4 must not be used or invoked informally. Any invocation / share transfer action must be routed through recovery approval workflow.

---

## 13.7 CDSL Pledge Component

### Purpose

Tracks online pledge of demat shares through CDSL.

### Required Conditions

- Required where shares are in demat form.
- Pledgor and pledgee must have BO accounts with CDSL.
- Pledge Request Form must be submitted.
- Pledge Sequence Number must be recorded.
- Pledge acceptance must be confirmed by pledgee DP.

### Fields

- Demat / BO ID of pledgor.
- Pledgee BO / DP details.
- Approved securities list confirmation.
- Pledge Request Form date.
- Pledge Sequence Number.
- Pledge request status.
- Acceptance date.
- Pledge created date.
- Agreement number referenced.
- Future shares pledge flag.

### Statuses

- Not required.
- Required.
- PRF pending.
- PRF submitted.
- PSN generated.
- Awaiting pledgee acceptance.
- Pledge accepted.
- Pledge active.
- Invocation initiated.
- Invoked.
- Unpledge requested.
- Unpledged.

---

## 13.8 Term Sheet Component

### Purpose

Captures and tracks execution of loan Term Sheet.

### Required Fields

- Borrower details.
- Nominee details.
- Shares held by borrower.
- Long-term or short-term facility.
- Loan amount.
- Purpose of loan.
- Rate of interest.
- Tenure of interest.
- Repayment date.
- Penalty interest.
- Other charges / fees.
- Security.
- Dispute resolution.

### Signing Authority

- Below ₹5,00,000: CFO signs Term Sheet.
- Exceeding ₹5,00,000: CFO and two Directors sign Term Sheet.
- Applicant and nominee must sign.

### Behaviour

- Interest rate fields should support floating rate structure.
- Undefined values must be flagged for configuration.
- Term Sheet must match sanctioned amount and conditions.

---

## 13.9 Loan Agreement Component

### Purpose

Tracks formal legally binding loan agreement.

### Requirements

- Prepared after Term Sheet.
- Executed on ₹500 stamp paper.
- Notarised.
- Signed by loan applicant.
- Signed by witness.

### Fields

- Agreement number.
- Generated date.
- Stamp paper number.
- Stamp value.
- Notarisation date.
- Borrower signature status.
- Witness signature status.
- CS verification status.
- Original custody location.

---

## 13.10 Bank Verification Letter Component

### Purpose

Handles signature mismatch cases.

### Trigger

Signature mismatch between borrower PAN, cheque, KYC documents or other submitted documents.

### Options

| Option | Requirement |
|---|---|
| Bank Verification Letter | Signed and stamped by concerned bank; confirms signature belongs to account holder. |
| Borrower Declaration | Declaration on non-judicial stamp paper affirming signature belongs to loan applicant. |

### Fields

- Signature mismatch detected: Yes / No.
- Mismatch documents.
- Selected resolution option.
- Bank letter uploaded.
- Bank stamp verified.
- Borrower declaration uploaded.
- Compliance verification.

### Gating Rule

Disbursement cannot proceed until mismatch is resolved.

---

## 13.11 Cancelled Cheque Component

### Purpose

Captures bank account evidence for disbursement.

### Fields

- Cheque image upload.
- Account holder name.
- Account number.
- IFSC.
- Branch.
- Bank name.
- Verification status.
- Matched with borrower: Yes / No.

### Behaviour

- Account number and IFSC should be extracted if OCR / manual entry available.
- Bank details must be verified before disbursement.
- Mismatch with borrower name should trigger verification workflow.

---

## 13.12 Blank-Dated Cheque Security Component

### Purpose

Tracks one blank-dated cheque provided as security.

### Fields

- Cheque received: Yes / No.
- Cheque number.
- Bank name.
- Account number masked.
- Date field blank confirmation.
- Physical custody location.
- Received by.
- Received date.
- Return status.
- Recovery invocation status.

### Important Control

The blank-dated cheque can only be dated and presented in default recovery after proper approval as described in recovery workflow.

---

## 13.13 Final Documentation Approval Component

### Purpose

Captures final approvals before file moves to Treasury.

### Approval Chain

1. Company Secretary approves documentation completeness.
2. Credit Manager confirms loan limits reviewed.
3. Sanction Committee signs off final disbursement approval.
4. Senior Manager - Finance signs after actual disbursement.

### Signature Meaning

| Signatory | System Meaning |
|---|---|
| Company Secretary | All documents required for disbursement verified and attached. |
| Credit Manager | Loan disbursement limits reviewed and confirmed. |
| Sanction Committee | Final approval for loan disbursement as per authority matrix. |
| Senior Manager - Finance | Loan has been disbursed to applicant account. |

---

## 14. SAP and Disbursement Components

## 14.1 SAP Customer Code Request Component

### Purpose

Initiates creation of SAP customer profile after loan approval.

### Trigger

Sanction Committee approval and sufficient readiness for SAP setup.

### Required Data

- Farmer full name.
- Aadhaar number.
- PAN number.
- Address.
- Email ID.
- Assigned loan application number.

### Behaviour

- If borrower is first-time borrower, new SAP Customer ID is required.
- If borrower has outstanding loan and existing Customer ID, same ID continues.
- Request can generate Excel template equivalent to Annexure I.
- Request email / system task goes to Senior Manager - Finance.

---

## 14.2 SAP Customer Code Confirmation Component

### Purpose

Records completion of SAP customer code creation.

### Fields

- SAP customer code.
- Created by.
- Creation date.
- Existing or new code.
- Confirmation attachment / email reference.
- Linked loan application.

### Gating Rule

Disbursement cannot be marked ready unless SAP customer code is created or confirmed.

---

## 14.3 Disbursement Readiness Gate Component

### Purpose

Checks all conditions before finance can initiate payment.

### Readiness Checks

- Sanction approved.
- Approval authority satisfied.
- Exception approvals complete.
- Documentation checklist verified.
- PoA complete.
- Tri-party agreement complete.
- SH-4 or CDSL pledge complete, as applicable.
- Term Sheet signed by correct authority.
- Loan Agreement stamped and notarised.
- Signature mismatch resolved.
- Cancelled cheque verified.
- Blank-dated cheque received.
- SAP customer code confirmed.
- Bank details verified.

### Outputs

- Ready for disbursement.
- Not ready.
- Missing items list.
- Responsible owner for each missing item.

---

## 14.4 Payment Initiation Component

### Purpose

Allows Senior Manager - Finance to initiate online payment through SFPCL's RBL Bank account.

### Fields

- Loan application number.
- Loan account number, if generated.
- Borrower name.
- SAP customer code.
- Bank account details.
- Amount to disburse.
- Payment method.
- Bank reference.
- Initiated by.
- Initiated timestamp.
- Remarks.

### Behaviour

- Amount must match sanctioned amount or approved disbursement amount.
- Bank details must be locked after verification.
- Payment initiation creates task for Chief Financial Controller.

---

## 14.5 Chief Financial Controller Authorisation Component

### Purpose

Captures final bank transfer approval by Chief Financial Controller.

### Fields

- Payment request details.
- Supporting loan file link.
- Authorisation decision.
- Bank transaction reference.
- Authorised date and time.
- Comments.

### Actions

- Authorise transfer.
- Reject transfer.
- Return for correction.

### Behaviour

- Rejection reason mandatory.
- Authorisation should update disbursement status.

---

## 14.6 Disbursement Advice Component

### Purpose

Generates communication to borrower after disbursement.

### Content Elements

- Borrower name.
- Loan application number.
- Disbursed amount.
- Disbursement date.
- Bank account masked.
- Repayment terms summary.
- Contact details for queries.

### Delivery Channels

- Email.
- SMS summary.
- Printable hard copy.

---

## 14.7 Loan Register Component

### Purpose

Records disbursed loans and active loan accounts.

### Fields

- Loan account number.
- Application number.
- Borrower name.
- Member ID.
- Sanctioned amount.
- Disbursed amount.
- Disbursement date.
- Interest rate.
- Tenure.
- Repayment date.
- Security status.
- SAP customer code.
- Outstanding principal.
- Outstanding interest.
- Current status.
- Closure date.

---

## 15. Repayment Components

## 15.1 Repayment Ledger Component

### Purpose

Tracks all repayment transactions against loan account.

### Fields

- Receipt ID.
- Loan account number.
- Borrower name.
- Payment date.
- Value date.
- Amount received.
- Payment channel.
- Bank reference.
- Subsidiary reference, if applicable.
- Allocation to principal.
- Allocation to interest.
- Allocation to charges.
- Unallocated amount.
- Posted in SAP: Yes / No.
- Posted by.
- Posting date.

### Behaviour

- Partial repayment is adjusted first against principal before interest, as per SOP.
- System should allow configuration if allocation rule changes.
- Bank statement transactions should be matched using borrower name and loan application number.

---

## 15.2 Direct Repayment Component

### Purpose

Records direct RTGS / NEFT repayment by farmer.

### Inputs

- Payment amount.
- RTGS / NEFT reference.
- Payment date.
- Bank statement evidence.
- Loan account number.

### Behaviour

- Entry should be posted in SAP on next working day after payment receipt and confirmation.
- If loan application number missing from bank reference, system should mark transaction as needs matching.

---

## 15.3 Subsidiary Repayment Component

### Purpose

Records repayment deducted by subsidiary company from produce payment.

### Inputs

- Subsidiary company name.
- Borrower name.
- Loan application number.
- Produce transaction reference.
- Deducted amount.
- Transfer date to SFPCL.
- Bank statement reference.

### Behaviour

- System should verify tri-party agreement exists for selected subsidiary.
- Bank statement transaction must clearly reflect borrower name and loan application number.
- Treasury verifies and passes receipt entry in SAP.

---

## 15.4 Repayment Allocation Component

### Purpose

Allocates received amounts to outstanding balances.

### SOP Allocation Rule

```text
Partial repayment is adjusted first against principal before interest recovery.
```

### Allocation Order

1. Principal.
2. Interest.
3. Charges / fees, unless configured otherwise.

### Required Display

- Amount received.
- Principal before payment.
- Interest before payment.
- Principal allocation.
- Interest allocation.
- Balance after payment.

---

## 15.5 Interest Invoice Component

### Purpose

Generates yearly interest invoices for farmers who have availed loans.

### SOP Responsibility

The Sales Team prepares and issues interest invoices at financial year-end where subsidiary repayments are involved. The Credit Manager is also stated as responsible for generating yearly interest invoices in the monitoring section. This responsibility should be configured or clarified.

### Fields

- Financial year.
- Loan account.
- Borrower.
- Interest accrued.
- Interest paid.
- Interest outstanding.
- Invoice number.
- Invoice date.
- Issued by.
- Delivery status.

---

## 15.6 Interest Capitalisation Component

### Purpose

Handles unpaid interest after 30 April of next financial year.

### SOP Rule

If farmer cannot pay interest up to 30 April of the next financial year:

```text
Revised Principal = Original Principal + Outstanding Interest Carried Forward
```

Interest for the new financial year is calculated on revised principal.

### Required Actions

- Identify unpaid interest as of 30 April.
- Add unpaid interest to principal.
- Update principal balance.
- Notify borrower by official email and hard copy intimation letter.
- Record audit trail.

---

## 15.7 Monthly Interest Accrual Component

### Purpose

Supports monthly SAP accrual entries.

### Fields

- Loan account.
- Accrual month.
- Principal base.
- Interest rate.
- Accrued interest.
- SAP journal reference.
- Posted by.
- Posting date.
- Status.

---

## 16. Monitoring Components

## 16.1 DPD Bucket Component

### Purpose

Classifies overdue loans for monitoring and CFO MIS.

### SOP Buckets

- 1 year to 2 years.
- 2 years to 3 years.
- More than 3 years.

### Additional Optional Buckets

The glossary mentions delinquency buckets such as 0-30, 31-60, 61-90 and greater than 90 days. The monitoring process explicitly uses longer buckets. System should support configurable bucket schemes.

### Fields

- Due date.
- Days past due.
- Bucket.
- Previous bucket.
- Bucket change date.
- Reminder status.

---

## 16.2 Quarterly MIS Component

### Purpose

Provides quarterly loan monitoring report to CFO.

### Sections

- Active loans.
- Outstanding principal.
- Outstanding interest.
- Loans by DPD bucket.
- Loans with reminders sent.
- Loans in grace period.
- Loans with extension granted.
- Loans under recovery review.
- Exceptions.
- Pending NOCs.

### Behaviour

- Generated quarterly.
- Reviewed by CFO.
- Exportable to PDF / Excel.
- Preserved as audit evidence.

---

## 16.3 Reminder Component

### Purpose

Schedules and records borrower reminders.

### Trigger

Credit Manager sends SMS / phone reminders when loan remains outstanding beyond one year at the end of each quarter.

### Fields

- Loan account.
- Reminder date.
- Reminder type: SMS / phone / email / letter.
- Message template.
- Recipient.
- Contact number / email.
- Delivery status.
- Call outcome.
- Next follow-up date.

---

## 16.4 Portfolio Risk Summary Component

### Purpose

Aggregates portfolio-level exposure and risk indicators.

### Metrics

- Total outstanding.
- Overdue outstanding.
- Number of overdue loans.
- DPD bucket distribution.
- Loans by crop.
- Loans by district.
- Loans by member type.
- Loans by security type.
- Loans pending re-KYC.
- Loans with unresolved exceptions.

---

## 17. Default and Recovery Components

## 17.1 Missed Payment Detector Component

### Purpose

Detects missed scheduled principal repayment.

### Trigger

Scheduled repayment date passes and principal amount remains unpaid.

### Output

- Missed payment event.
- Grace period start.
- Borrower reminder task.
- Credit Manager review task.

---

## 17.2 Grace Period Component

### Purpose

Tracks the three-month additional tenure provided after missed scheduled principal repayment.

### Fields

- Original due date.
- Grace period start date.
- Grace period end date.
- Outstanding principal.
- Reminder schedule.
- Status.

### Behaviour

- Grace period is automatically calculated as three months from due date.
- If payment completed during grace period, default workflow stops.
- If unpaid after grace period, intentional / non-intentional assessment is triggered.

---

## 17.3 Intentional vs Non-Intentional Default Assessment Component

### Purpose

Allows Credit Assessment Team to analyse reason for non-payment.

### Fields

- Reason for non-payment.
- Evidence.
- Borrower explanation.
- Field visit note, if applicable.
- Assessment result: Intentional / Non-intentional / Inconclusive.
- Prepared by.
- Reviewed by.

### Note

The SOP requires this assessment but does not define detailed criteria. System should support configurable criteria and mandatory comments.

---

## 17.4 Extension Note Component

### Purpose

Documents one-year extension for non-intentional non-payment.

### Trigger

Borrower fails to repay within grace period and non-payment is assessed as non-intentional.

### Fields

- Loan account.
- Grace period end date.
- Assessment summary.
- Extension start date.
- Extension end date.
- Reason for extension.
- Prepared by Credit Manager.
- Approval / acknowledgement, if configured.
- Document stored in loan file.

---

## 17.5 Non-Payment Note Component

### Purpose

Prepared when borrower remains unable to repay even after one-year extension.

### Fields

- Loan account.
- Borrower name.
- Outstanding principal.
- Outstanding interest.
- Original due date.
- Grace period details.
- Extension details.
- Reason for continued non-payment.
- Intentional / non-intentional assessment.
- Recovery recommendation.
- Prepared by Credit Assessment Team.
- Submitted to Sanction Committee.

---

## 17.6 Recovery Decision Component

### Purpose

Allows Sanction Committee to decide recovery action based on Note for Non-Payment.

### Possible Decisions

- Initiate sale of shares.
- Invoke SH-4 process.
- Present blank-dated cheque after inserting date.
- Invoke CDSL pledge.
- Continue follow-up.
- Write-off / non-recoverable recommendation, if allowed by policy.
- Return for further assessment.

### Required Controls

- Decision reason mandatory.
- Approval authority mandatory.
- Board / Sanction Committee approval evidence required before using SH-4 or undated cheque.
- No recovery action can bypass audit log.

---

## 17.7 Security Invocation Component

### Purpose

Tracks recovery action through pledged or secured instruments.

### Security Types

- SH-4 for physical shares.
- CDSL pledge for demat shares.
- Blank-dated cheque.

### Fields

- Security type.
- Approval reference.
- Invocation date.
- Action owner.
- Result.
- Amount recovered.
- Remaining balance.
- Evidence documents.

---

## 17.8 Recovery Log Component

### Purpose

Maintains fair-practice and audit evidence for recovery interactions.

### Fields

- Interaction date.
- Interaction mode.
- Person contacted.
- Staff member.
- Summary.
- Next action.
- Borrower complaint raised: Yes / No.
- Attachment.

### Control

Recovery log must support non-harassment and grievance redress evidence.

---

## 18. Closure Components

## 18.1 Full Repayment Detector Component

### Purpose

Identifies loans where principal, interest and applicable dues are fully repaid.

### Outputs

- Eligible for closure.
- Closure task for Compliance Team.
- NOC generation trigger.
- Security return task.
- CDSL unpledge task, if applicable.

---

## 18.2 NOC Component

### Purpose

Generates No Objection Certificate after full repayment.

### Fields

- Borrower name.
- Loan account number.
- Application number.
- Disbursed amount.
- Full repayment date.
- Statement that no dues remain.
- Issued by.
- Issue date.
- Delivery mode.

### Behaviour

- NOC cannot be generated until full repayment confirmed.
- NOC issuance must be logged.

---

## 18.3 Security Return Component

### Purpose

Tracks return of borrower security after closure.

### Items

- SH-4 copy / original, as applicable.
- Blank-dated cheque.
- Other physical security documents.
- Confirmation of CDSL unpledge, if applicable.

### Fields

- Item returned.
- Return date.
- Returned by.
- Received by borrower / authorised person.
- Acknowledgement upload.
- Pending reason.

---

## 18.4 CDSL Unpledge Component

### Purpose

Tracks unpledging of demat shares after loan repayment.

### Process Support

- Pledgor fills Unpledge Request Form in duplicate.
- Pledgor's DP creates unpledge request using PSN.
- Request may be partial or full.
- Pledgee's DP accepts or rejects.
- Pledgee may also initiate Auto Unpledge.

### Fields

- PSN.
- URF date.
- Partial / full unpledge.
- Pledgee DP action.
- Acceptance / rejection date.
- Auto Unpledge used: Yes / No.
- Completion evidence.

---

## 18.5 Archive Component

### Purpose

Ensures loan files are retained for at least eight years.

### Fields

- Loan account.
- Closure date.
- Archive date.
- Retention end date.
- Physical file location.
- Digital archive location.
- Destruction eligibility date, if policy allows.
- Audit access status.

### Behaviour

- Archived records remain searchable to authorised users.
- Sensitive documents remain access-controlled.
- Destruction, if implemented, must require approval and certificate.

---

## 19. Compliance Components

## 19.1 Section 186 Tracker Component

### Purpose

Monitors statutory lending limit.

### SOP Requirement

Loan amount is limited to 60% of paid-up capital, free reserves and securities premium, or 100% of free reserves and securities premium, whichever is more. If exceeded, prior approval of Board with special resolution is required.

### Fields

- Paid-up capital.
- Free reserves.
- Securities premium.
- 60% calculation.
- 100% calculation.
- Higher permitted limit.
- Current exposure.
- Headroom.
- Breach flag.
- Board approval evidence, if exceeded.
- Review quarter.
- Prepared by.
- Reviewed by CFO.

---

## 19.2 NBFC Principal Business Test Component

### Purpose

Monitors whether SFPCL may trigger NBFC registration requirement.

### SOP Requirement

NBFC registration may be required if:

- Financial assets exceed 50% of total assets; and
- Income from financial assets exceeds 50% of gross income.

### Fields

- Total assets.
- Financial assets.
- Financial assets ratio.
- Gross income.
- Income from financial assets.
- Financial income ratio.
- Test result.
- Review quarter.
- Board note.
- CFO review status.

---

## 19.3 KYC / Re-KYC Compliance Component

### Purpose

Tracks KYC completeness and re-KYC every two years.

### Fields

- Member.
- Borrower KYC status.
- Nominee KYC status.
- CKYC consent status.
- Last KYC date.
- Re-KYC due date.
- Risk rating.
- KYC audit result.

### Alerts

- KYC missing.
- Re-KYC due within 30 days.
- Re-KYC overdue.

---

## 19.4 Stamp Duty Compliance Component

### Purpose

Tracks stamping and notarisation of legal documents.

### Documents Covered

- Loan Agreement.
- Power of Attorney.
- SH-4, where stamp duty applies.
- Other instruments as configured.

### Fields

- Document name.
- Stamp duty amount.
- Stamp paper / e-stamp number.
- Execution date.
- Notarisation required.
- Notarisation complete.
- Verified by CS.

---

## 19.5 Money-Lending Law Review Component

### Purpose

Tracks annual legal / compliance review of money-lending law applicability.

### Fields

- Review year.
- States covered.
- Maharashtra exemption rationale.
- Legal opinion uploaded.
- Board note uploaded.
- Reviewed by CS.
- Review date.
- Next due date.

---

## 19.6 Grievance Component

### Purpose

Captures borrower complaints and resolution tracking.

### Fields

- Grievance ID.
- Borrower name.
- Loan account.
- Complaint category.
- Description.
- Date received.
- Received through.
- Assigned owner.
- Target resolution date.
- Resolution summary.
- Closure date.
- Borrower acknowledgement.

### Categories

- Loan application issue.
- Documentation issue.
- Disbursement delay.
- Repayment posting issue.
- Interest / charge dispute.
- Recovery conduct complaint.
- NOC / closure delay.
- Data correction.

---

## 19.7 Record Retention Component

### Purpose

Ensures loan records are retained for statutory and internal audit period.

### SOP Requirement

Loan-related documents are archived for at least eight years.

### Fields

- Record category.
- Retention start date.
- Retention period.
- Retention end date.
- Archive location.
- Legal hold: Yes / No.
- Disposal status.

---

## 20. Reports and Export Components

## 20.1 Report Builder Component

### Purpose

Allows authorised users to generate standard and filtered reports.

### Standard Reports

- Loan Request Register.
- Credit Sanction Register.
- Exception Register.
- Loan Register.
- Documentation Pending Report.
- Disbursement Report.
- Repayment Report.
- DPD Report.
- Quarterly CFO MIS.
- KYC / Re-KYC Report.
- Stamp Duty Report.
- NBFC Test Report.
- Section 186 Report.
- Grievance Report.
- Closure / NOC Pending Report.

### Export Formats

- Excel.
- PDF.
- CSV, if required.

### Controls

- Sensitive exports should be permission-controlled.
- Export event should be audit-logged.
- Export should show generated by, generated date and filters applied.

---

## 20.2 Register Table Component

### Purpose

Reusable component for all statutory / process registers.

### Features

- Search.
- Filters.
- Sort.
- Column selection.
- Export.
- Row drill-down.
- Status badges.
- Date range.
- Saved views.

### Registers

- Loan Request Register.
- Credit Sanction Register.
- Exception Register.
- Loan Register.
- Security Register.
- Grievance Register.
- Compliance Register.

---

## 21. Communication Components

## 21.1 Borrower Communication Composer

### Purpose

Sends standard borrower communication through approved templates.

### Channels

- Email.
- SMS.
- Printable hard copy / courier.
- Phone call log.

### Template Types

- Application acknowledgement.
- Deficiency notice.
- Rejection note.
- Sanction communication.
- Documentation request.
- Disbursement advice.
- Interest rate change notice.
- Interest capitalisation notice.
- Repayment reminder.
- Grace period notice.
- Extension notice.
- Recovery notice.
- NOC issuance.
- Grievance acknowledgement.
- Grievance resolution.

### Controls

- Template version must be stored.
- Message content must be preserved.
- Delivery status must be logged.
- Sensitive data should be masked in SMS.

---

## 21.2 Internal Email / Task Generator

### Purpose

Creates internal workflow communications.

### Examples

- Credit Manager to Senior Manager - Finance for SAP code creation.
- Sanction Committee approval request.
- Compliance Team documentation correction request.
- CFC payment authorisation request.
- CFO quarterly MIS ready notification.

### Behaviour

- Prefer system task over free-form email where possible.
- Email copy may be generated for users if integration exists.

---

## 22. Admin and Configuration Components

## 22.1 Policy Configuration Component

### Purpose

Stores Board-approved lending policy parameters.

### Configurable Parameters

- Share valuation.
- Valuation method reference.
- Shareholding percentage.
- Per-share cap.
- Scale of finance per acre.
- Crop-wise scale of finance, if implemented.
- Approval threshold ₹5,00,000.
- Interest benchmark.
- Interest spread.
- Penal interest.
- Other charges / fees.
- Re-KYC frequency.
- DPD bucket definitions.
- Reminder schedule.
- Record retention period.

### Controls

- Changes require maker-checker approval.
- Board approval evidence must be attached where required.
- Effective date and version must be stored.
- Historical calculations must preserve the policy version used.

---

## 22.2 Template Management Component

### Purpose

Manages document and communication templates.

### Template Types

- Loan Application Form.
- Loan Appraisal Note.
- PoA.
- Tri-party Agreement.
- SH-4 reference template.
- Term Sheet.
- Loan Agreement.
- Bank Verification Letter.
- Checklist.
- Rejection Note.
- Disbursement Advice.
- NOC.
- Reminder messages.
- Grievance forms.

### Fields

- Template name.
- Template type.
- Version.
- Effective date.
- Language.
- Individual / FPO applicability.
- Approved by.
- Approval date.
- Active / inactive.

---

## 22.3 Role and Permission Management Component

### Purpose

Administers user access.

### Features

- Create role.
- Assign permissions.
- Map users to roles.
- Assign approval authority.
- Configure sensitive data access.
- Deactivate user.
- View permission audit.

### Controls

- Privileged role changes must be approved.
- Permission exports must be audit-logged.
- Segregation-of-duty conflicts should be warned.

---

## 22.4 Numbering Sequence Component

### Purpose

Controls numbering for application and other records.

### Sequences

- Loan application number: `LO00000001`.
- Loan account number.
- Sanction entry number.
- Exception ID.
- Grievance ID.
- NOC number.
- SAP request ID.
- Document checklist ID.

### Controls

- Sequence changes must be admin-only.
- Duplicates must be prevented.
- Gaps should be logged if records are cancelled.

---

## 23. Data Display and Input Primitives

## 23.1 Currency Input Component

### Requirements

- Indian rupee format.
- Comma grouping.
- Decimal support if needed.
- Negative values blocked except accounting adjustments.
- Must support validation against sanctioned and eligible amounts.

---

## 23.2 Date Input Component

### Requirements

- Indian date format display, if client prefers.
- ISO storage format.
- Business day awareness for next working day SAP posting.
- Financial year awareness for interest invoice and capitalisation.

---

## 23.3 File Upload Component

### Requirements

- Upload PDF, image and document formats.
- Show file size.
- Show upload progress.
- Version files if replaced.
- Categorise document.
- Capture uploaded by and timestamp.
- Virus scan / validation if available.
- Sensitive document flag.

---

## 23.4 Document Viewer Component

### Requirements

- In-browser preview for PDFs and images.
- Download based on permission.
- Mask sensitive data if redacted view required.
- Show document metadata.
- Show verification status.

---

## 23.5 Data Table Component

### Requirements

- Sort.
- Filter.
- Search.
- Pagination.
- Bulk actions, where permitted.
- Export.
- Column visibility.
- Sticky header.
- Empty state.
- Loading state.
- Row-level actions.

---

## 23.6 Confirmation Modal Component

### Used For

- Reject application.
- Approve exception.
- Initiate disbursement.
- Authorise transfer.
- Start recovery action.
- Invoke security.
- Close loan.
- Change policy configuration.

### Required Elements

- Action title.
- Consequence explanation.
- Mandatory reason field for high-risk actions.
- Confirm button.
- Cancel button.
- Link to audit policy if necessary.

---

## 23.7 Alert and Banner Component

### Types

- Information.
- Warning.
- Error.
- Success.
- Critical compliance alert.

### Examples

```text
Warning: The requested amount exceeds the final eligible loan amount. Exception approval is required.
```

```text
Error: Disbursement cannot proceed because the Loan Agreement is not notarised.
```

```text
Success: SAP customer code has been confirmed and the loan file is ready for disbursement review.
```

---

## 23.8 Empty State Component

### Purpose

Provides helpful guidance where no records exist.

### Examples

| Context | Message |
|---|---|
| No applications | No loan applications have been created yet. Start a new loan application after selecting an eligible member. |
| No tasks | You have no pending tasks. |
| No documents | No documents have been uploaded for this loan file. |
| No repayments | No repayment transactions have been recorded yet. |
| No exceptions | No exceptions are recorded for this loan. |

---

## 24. Component State Model

## 24.1 Record-Level States

### Loan Application States

1. Draft.
2. Submitted.
3. Completeness check pending.
4. Incomplete / deficiency raised.
5. Under credit assessment.
6. Appraisal prepared.
7. Credit Manager review pending.
8. Submitted to Sanction Committee.
9. Approved.
10. Rejected.
11. Pending documentation.
12. Documentation complete.
13. Pending SAP code.
14. Ready for disbursement.
15. Disbursement initiated.
16. Disbursed.
17. Active loan.
18. Overdue.
19. In grace period.
20. Extension granted.
21. Recovery under review.
22. Closed.
23. Archived.

### Document States

1. Not required.
2. Required.
3. Pending.
4. Draft generated.
5. Uploaded.
6. Signed.
7. Stamped.
8. Notarised.
9. Verified.
10. Rejected.
11. Returned.
12. Archived.

### Approval States

1. Not started.
2. Pending.
3. Partially approved.
4. Approved.
5. Rejected.
6. Returned for clarification.
7. Withdrawn.
8. Superseded.

---

## 25. Error Handling Components

## 25.1 Validation Summary Component

### Purpose

Shows all blocking issues at once.

### Example

```text
This application cannot be submitted because 4 required items are missing:
1. Nominee Aadhaar copy is missing.
2. Six-month bank statement is missing.
3. Crop plan is missing.
4. Loan purpose is not selected.
```

---

## 25.2 Field-Level Error Component

### Requirements

- Error message must be adjacent to field.
- Must be specific.
- Must tell user how to correct.

### Examples

| Field | Error |
|---|---|
| PAN | Enter a valid PAN in the format `ABCDE1234F`. |
| Aadhaar | Enter a valid 12-digit Aadhaar number. |
| Loan amount | Loan amount must be greater than ₹0. |
| Nominee age | Nominee must not be a minor. |
| IFSC | Enter a valid IFSC code. |

---

## 25.3 Blocking Gate Error Component

### Purpose

Explains why a workflow action cannot proceed.

### Examples

```text
Cannot submit to Sanction Committee because the Loan Appraisal Note is incomplete.
```

```text
Cannot mark documentation complete because SH-4 witness signature is missing.
```

```text
Cannot initiate disbursement because SAP customer code has not been confirmed.
```

---

## 26. Security and Privacy Requirements for Components

### 26.1 Sensitive Data Fields

The following data should be masked where full access is not required:

- Aadhaar number.
- PAN.
- Bank account number.
- Cheque number.
- Signature images.
- KYC document scans.
- Security documents.
- Personal address and mobile number, depending on role.

### 26.2 Masking Examples

| Field | Masked Format |
|---|---|
| Aadhaar | `XXXX XXXX 1234` |
| PAN | `ABCDE****F` or full PAN only for permitted users |
| Bank Account | `XXXXXX1234` |
| Mobile | `XXXXXX7890` |

### 26.3 Access Control

- KYC downloads should be restricted.
- Security documents should be visible only to authorised Compliance / CS / approver / auditor roles.
- Exports containing sensitive data should be logged.
- Role changes should be audited.

---

## 27. Integration-Ready Components

## 27.1 SAP Integration Adapter Component

### Purpose

Encapsulates all SAP-related requests and confirmations.

### Initial Manual Mode

- Generate Excel template.
- Create system task for Senior Manager - Finance.
- Record SAP customer code manually.
- Upload confirmation evidence.

### Future API Mode

- Push customer master request.
- Receive customer code.
- Push loan posting.
- Receive SAP journal reference.
- Reconcile status.

---

## 27.2 Bank Integration Adapter Component

### Purpose

Supports RBL Bank payment initiation and reconciliation.

### Initial Manual Mode

- Capture payment initiation details.
- Capture CFC authorisation.
- Upload bank transfer evidence.
- Enter bank reference.

### Future API Mode

- Validate beneficiary.
- Initiate payment request.
- Capture approval workflow.
- Receive transaction status.
- Auto-reconcile bank statement.

---

## 27.3 CDSL Tracking Adapter Component

### Purpose

Tracks CDSL pledge and unpledge process.

### Initial Manual Mode

- Capture PRF, PSN, acceptance and unpledge status manually.
- Upload evidence.

### Future Integration Mode

- Pull pledge status, if API / integration available.
- Validate PSN.
- Track invocation and unpledge state.

---

## 28. Component Traceability Matrix

| SOP / Analysis Requirement | Component(s) |
|---|---|
| Loan initiated by farmer / FPC | Member Selector, Loan Application Form, Application Reference Number. |
| Application signed by applicant and nominee | Loan Application Form, Signature Status Component. |
| KYC required for borrower and nominee | KYC Document Status, File Upload, Document Viewer. |
| Unique application number | Application Reference Number, Loan Request Register. |
| Incomplete applications returned | Completeness Check, Deficiency Note. |
| Appraisal note within 2 days | Loan Appraisal Note, Task Queue, TAT Tracker. |
| Active member criteria | Active Member Assessment. |
| No existing default | Existing Default Check. |
| Loan purpose agriculture only | Loan Purpose Validator. |
| Shareholding and land limit | Shareholding Limit Calculator, Land Limit Calculator, Final Eligible Amount. |
| Sanction approval matrix | Approval Matrix Engine, Sanction Committee Review. |
| Director / relative special case | Conflict-of-Interest Component. |
| Credit Sanction Register | Credit Sanction Register Component. |
| Power of Attorney | PoA Component. |
| Tri-party repayment agreement | Tri-Party Agreement Component. |
| Physical share security | SH-4 Component. |
| Demat share pledge | CDSL Pledge Component. |
| Term Sheet | Term Sheet Component. |
| Loan Agreement | Loan Agreement Component. |
| Signature mismatch | Bank Verification Letter Component. |
| Checklist approvals | Document Checklist, Final Documentation Approval. |
| SAP customer code | SAP Request and Confirmation Components. |
| Disbursement through RBL Bank | Payment Initiation, CFC Authorisation, Disbursement Advice. |
| Direct RTGS / NEFT repayment | Direct Repayment Component. |
| Subsidiary deduction | Subsidiary Repayment Component. |
| Principal-first partial repayment | Repayment Allocation Component. |
| Interest invoice and accrual | Interest Invoice, Monthly Interest Accrual. |
| Interest capitalisation after 30 April | Interest Capitalisation Component. |
| Quarterly DPD / MIS | DPD Bucket, Quarterly MIS. |
| Three-month grace period | Grace Period Component. |
| One-year extension | Extension Note Component. |
| Non-payment note | Non-Payment Note Component. |
| SH-4 / cheque recovery approval | Recovery Decision, Security Invocation. |
| NOC and security return | NOC, Security Return, CDSL Unpledge. |
| 8-year retention | Archive, Record Retention. |
| Section 186 | Section 186 Tracker. |
| NBFC test | NBFC Principal Business Test. |
| Re-KYC every two years | KYC / Re-KYC Compliance. |
| Stamp duty | Stamp Duty Compliance. |
| Grievance handling | Grievance Component. |

---

## 29. Component-Level Acceptance Criteria

### 29.1 General Acceptance Criteria

- Components must be reusable across screens where applicable.
- Components must respect user permissions.
- Components must support audit logging for all critical actions.
- Components must show validation before submission.
- Components must prevent workflow bypass where the SOP requires sequential processing.
- Components must preserve policy version used for calculations and templates.
- Components must support export and reporting where required.
- Components must gracefully handle missing data and integration failures.

### 29.2 Business Gate Acceptance Criteria

| Gate | Acceptance Criteria |
|---|---|
| Application submission | Mandatory fields, signatures and documents either complete or deficiency workflow active. |
| Appraisal submission | Eligibility, limits, loan purpose, default check and risk assessment complete. |
| Sanction approval | Correct approval matrix applied; decisions recorded in Credit Sanction Register. |
| Documentation completion | All required documents verified; stamping and notarisation complete where required. |
| Disbursement initiation | Documentation complete, SAP code confirmed, bank details verified and final approvals complete. |
| Repayment posting | Payment matched, allocated, SAP posting status captured. |
| Default escalation | Grace period, assessment, extension and non-payment note follow SOP sequence. |
| Recovery action | Sanction Committee / Board approval captured before invoking security. |
| Closure | Full repayment confirmed, NOC issued, security returned and file archived. |

---

## 30. Open Component Design Questions

The following items remain unresolved from current analysis and should be confirmed before final build.

| Topic | Open Question | Impacted Components |
|---|---|---|
| Loan limit percentage | Should operative formula use 30%, 10% or fixed ₹200 per share? | Shareholding Limit Calculator, Policy Configuration, Appraisal, Sanction. |
| Annexure numbering | Is Annexure K Credit Sanction Register or Grievance Form? | Template Management, Register Components. |
| Interest benchmark | What is the current floating interest benchmark, spread and reset frequency? | Term Sheet, Interest Accrual, Invoice, Rate Change Notice. |
| Penal interest | What is the exact penalty interest / fee structure? | Term Sheet, Repayment, Default, Content Templates. |
| NACH / ECS | Is NACH / ECS required in addition to RTGS / NEFT and subsidiary deduction? | Security Documents, Repayment Components. |
| Guarantor | When is guarantor required? | Application, Documentation, Appraisal. |
| Credit bureau | Are bureau checks mandatory? | Eligibility, Appraisal, Declarations. |
| Intentional default criteria | What criteria determine intentional vs non-intentional default? | Default Assessment, Extension Note, Recovery Decision. |
| Non-recoverable classification | Is classification automatic after extension failure or approval-based? | Non-Payment Note, Recovery Decision, Reports. |
| Money-lending law review | Are operations limited to Maharashtra or multi-state? | Compliance Dashboard, Money-Lending Review. |
| SAP integration | Will SAP be manual, email-based or API-integrated? | SAP Components, Disbursement. |
| Bank integration | Will RBL Bank payment be manual or API-integrated? | Payment Initiation, CFC Authorisation. |
| CDSL integration | Will pledge status be manually tracked or integrated? | CDSL Pledge, CDSL Unpledge. |

---

## 31. Recommended Build Sequencing by Component

### Phase 1: Core Loan Origination Components

- Application Shell.
- Role and Permission Management.
- Member Search and Selector.
- Member Summary Card.
- Loan Application Form.
- Application Reference Number.
- Loan Request Register.
- Completeness Check.
- KYC Document Status.
- Eligibility Checklist.
- Loan Limit Calculators.
- Loan Appraisal Note.

### Phase 2: Approval and Documentation Components

- Approval Matrix Engine.
- Sanction Committee Review.
- Approval Decision Card.
- Credit Sanction Register.
- Exception Register.
- Documentation Workspace.
- Document Checklist.
- Document Generator.
- PoA, Tri-Party Agreement, SH-4, CDSL Pledge, Term Sheet and Loan Agreement components.
- Bank Verification Letter.
- Final Documentation Approval.

### Phase 3: Disbursement and Finance Components

- SAP Customer Code Request.
- SAP Confirmation.
- Disbursement Readiness Gate.
- Payment Initiation.
- CFC Authorisation.
- Disbursement Advice.
- Loan Register.

### Phase 4: Repayment and Monitoring Components

- Repayment Ledger.
- Direct Repayment.
- Subsidiary Repayment.
- Repayment Allocation.
- Interest Invoice.
- Interest Capitalisation.
- Monthly Accrual.
- DPD Bucket.
- Quarterly MIS.
- Reminder Component.

### Phase 5: Default, Closure and Compliance Components

- Missed Payment Detector.
- Grace Period.
- Intentional / Non-Intentional Default Assessment.
- Extension Note.
- Non-Payment Note.
- Recovery Decision.
- Security Invocation.
- NOC.
- Security Return.
- CDSL Unpledge.
- Archive.
- Compliance Trackers.
- Grievance Component.

---

## 32. Summary

The component architecture for SFPCL's Member Credit Administration and Settlement system must support a highly controlled lending lifecycle. The critical design requirement is not only to capture forms and documents, but to enforce the sequence of controls embedded in the SOP.

The most important reusable components are:

1. Member and borrower context components.
2. Application, KYC and completeness components.
3. Eligibility and loan limit calculation components.
4. Appraisal and risk components.
5. Approval matrix and sanction register components.
6. Documentation, stamping, PoA, SH-4 and CDSL pledge components.
7. SAP and disbursement readiness components.
8. Repayment, interest, DPD and monitoring components.
9. Default, extension, recovery and security invocation components.
10. Closure, NOC, security return and archival components.
11. Compliance, reporting and audit components.

A successful implementation should allow every loan to be traced from application number `LO00000001` style registration through sanction, documentation, SAP setup, RBL bank disbursement, repayment, monitoring, default handling if needed, closure and eight-year archive. The system should prevent unauthorised lending, incomplete document execution, premature disbursement and undocumented recovery action while keeping operational work manageable for Credit, Compliance, Treasury, Finance, Sanction Committee and audit users.
