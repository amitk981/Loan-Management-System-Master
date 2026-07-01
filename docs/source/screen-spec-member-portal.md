# screen-spec.md — SFPCL Member Portal Screens

## 1. Document Control

| Item | Detail |
|---|---|
| Product / System | SFPCL Member Credit Administration & Loan Management System |
| Document Type | Member Portal Screen Specification |
| Output File | `screen-spec-member-portal.md` |
| Primary Role | Borrower / Member / Farmer / FPC / Producer Institution applicant |
| Primary Business Process | Member login, loan application submission, document upload, application tracking, sanction visibility, documentation response, disbursement notification, repayment visibility, grievance and closure support |
| Source Basis | Existing screen specification, user flows, functional specification, information architecture, component specification, design system and auth-permissions artifacts |
| Intended Readers | Product manager, UX designer, UI designer, frontend engineers, backend engineers, QA team, implementation team and business process owners |
| Status | Draft extension for borrower/member-facing portal screens |

---

## 2. Purpose

This document defines the borrower/member-facing screens for the SFPCL Member Portal. The portal allows an eligible member to log in, view member and loan status, apply for a loan, upload documents, respond to deficiencies, track approval and processing stages, receive disbursement and repayment information, and raise grievances.

The portal must not replace internal controls. It is the borrower-facing entry and visibility layer for the existing controlled loan workflow. After a member submits an application, the case is received by the Credit Assessment Team and proceeds through completeness check, appraisal, sanction, documentation, SAP setup, disbursement, active loan monitoring, repayment, closure and archival in the internal system.

---

## 3. Role Definition

## 3.1 Primary Role: Borrower / Member Portal User

The Member Portal user is an SFPCL member, farmer, FPC or Producer Institution representative who can access only their own profile, applications, loan accounts, documents, notices, repayments and grievances.

## 3.2 Role Goals

| Goal | Description |
|---|---|
| Apply for loan | Start and submit a member loan request for agriculture / crop-production purpose. |
| Complete requirements | Enter member, borrower, nominee, loan, land, crop, bank and document details. |
| Track processing | View where the application is in the lifecycle and what action is pending. |
| Respond to deficiencies | Upload missing documents or correct returned application details. |
| View sanction and documentation status | See approval outcome, term sheet availability and pending signatures. |
| Track disbursement | View whether disbursement is pending, approved or completed. |
| Track repayment | View repayment schedule, outstanding balance, direct repayment acknowledgements and subsidiary deductions. |
| Close loan | View NOC and security return / unpledge status after full repayment. |
| Raise grievance | Submit and track service requests, questions and complaints. |

## 3.3 Access Boundaries

| Area | Borrower Portal Access |
|---|---|
| Own member profile | View; edit only contact / allowed self-declared fields subject to verification. |
| Own loan applications | Create draft, edit draft, submit, view status, resubmit deficiencies. |
| Own documents | Upload required documents; view permitted documents and generated borrower copies. |
| Internal appraisal | View high-level status only; no access to internal scoring, risk comments or approval notes unless explicitly published. |
| Sanction decision | View approval / rejection outcome and borrower-facing reason or next step. |
| Documentation | View required signatures, downloadable borrower copies and pending document actions. |
| Disbursement | View status, amount, date and UTR / reference when completed. |
| Repayment | View schedule, outstanding balance, repayments received and acknowledgements. |
| Recovery and legal action | View notices addressed to the borrower; no access to internal recovery approvals. |
| Audit trail | View borrower-facing activity history only. |
| Other members | No access. |
| Internal users, registers, MIS, policy settings | No access. |

---

## 4. Member Portal Lifecycle

The portal should display the loan lifecycle using a borrower-friendly stage tracker.

```text
Draft -> Submitted -> Completeness Review -> Deficiency / Appraisal -> Sanction Review -> Approved / Rejected -> Documentation -> SAP & Disbursement Processing -> Disbursed -> Active Loan -> Closure
```

For repayment risk, the portal should show a separate borrower-facing repayment state:

```text
On Track -> Payment Due Soon -> Payment Overdue -> Grace Period -> Extension / Review -> Recovery Notice -> Closed
```

The borrower should never need to understand internal department names to know what to do next. Every status must show:

- Current stage.
- Plain-language meaning.
- Pending action by borrower or SFPCL.
- Expected next step.
- Relevant due date, where applicable.
- Contact / grievance option.

---

## 5. Global Member Portal Components

## 5.1 Portal Header

| Element | Behaviour |
|---|---|
| SFPCL / Sahyadri logo | Navigates to Member Portal Dashboard. |
| Application switcher | Shows current active application or loan account if multiple exist. |
| Notification icon | Shows document deficiencies, reminders, approval updates, repayment alerts and closure notices. |
| Language selector | Optional; supports English and local language when configured. |
| Help link | Opens FAQs, required document guide and contact details. |
| User menu | Profile, security settings, logout. |

## 5.2 Member Portal Navigation

Recommended navigation:

1. Dashboard
2. My Profile
3. New Loan Application
4. My Applications
5. My Documents
6. My Loans
7. Repayments
8. Notices & Letters
9. Grievances
10. Help & Support

Navigation must be responsive for mobile because members may access the portal from phones.

## 5.3 Status Card Pattern

Every application and loan status page should use a standard status card.

| Field | Description |
|---|---|
| Application / Loan number | `LO00000001` style application reference after completeness check; temporary draft number before that. |
| Borrower name | Member / FPC / Producer Institution name. |
| Current status | Draft, Submitted, Deficiency Raised, Under Appraisal, Under Sanction, Approved, Documentation Pending, Disbursement Processing, Disbursed, Active, Closed. |
| Pending with | Borrower / SFPCL Credit Team / Compliance Team / Finance / Accounts. |
| Action required | Specific next action, if any. |
| Due date | Borrower action deadline or repayment due date. |
| Alerts | Missing document, signature required, overdue payment, KYC due, approval pending. |
| Primary action | Continue application, upload document, view details, download letter, raise grievance. |

## 5.4 Document Upload Component

| Element | Behaviour |
|---|---|
| Required document label | Shows exact document name and whether mandatory / conditional. |
| Accepted format | PDF, JPG, PNG or configured file types. |
| Upload area | Drag-and-drop and file picker. |
| Self-attestation confirmation | Required for PAN, Aadhaar and KYC copies where applicable. |
| Status | Not uploaded, Uploaded, Under review, Accepted, Rejected, Re-upload required. |
| Rejection reason | Shown in plain language with re-upload action. |
| Preview | Available only for documents the borrower is permitted to view. |
| Version history | Shows upload date and status, not internal verifier notes. |

## 5.5 Borrower-Friendly Copy Rules

- Use plain, respectful language.
- Avoid internal terms such as “maker-checker”, “CFC queue” or “exception register” unless translated into borrower-facing copy.
- Always explain what the borrower needs to do next.
- Do not reveal internal risk assessment, committee comments, approver conflicts or sensitive internal control details.
- Show rejection / deficiency reasons clearly enough for borrower action.

---

## 6. Screen Inventory

| ID | Screen Name | Module | Primary Purpose |
|---|---|---|---|
| MP00 | Member Portal Login | Access | Secure borrower/member login. |
| MP01 | Account Activation / First-Time Access | Access | Verify member identity and activate portal account. |
| MP02 | Forgot Password / OTP Verification | Access | Recover access securely. |
| MP03 | Member Portal Dashboard | Dashboard | Show profile, applications, loans, pending actions and alerts. |
| MP04 | My Profile | Profile | View member, borrower, nominee and contact details. |
| MP05 | New Loan Application — Start | Loan Application | Start a loan request and validate membership. |
| MP06 | Loan Application Form | Loan Application | Capture member, loan, nominee, land, crop, bank and declaration details. |
| MP07 | Document Upload Checklist | Documents | Upload KYC and supporting documents. |
| MP08 | Application Review & Submission | Loan Application | Review, consent, sign / acknowledge and submit application. |
| MP09 | My Applications List | Applications | View all draft, submitted, active and historical applications. |
| MP10 | Application Status Detail | Applications | Track lifecycle stage, deficiencies, approval outcome and next steps. |
| MP11 | Deficiency Response | Applications | Correct returned details and re-upload rejected / missing documents. |
| MP12 | Sanction Outcome & Terms | Sanction | View approval / rejection outcome, sanctioned amount and borrower-facing terms. |
| MP13 | Documentation Actions | Documentation | View and complete borrower-side document and signature requirements. |
| MP14 | Disbursement Status | Disbursement | Track SAP / finance processing and completed disbursement advice. |
| MP15 | My Loans | Loan Account | View active and closed loan accounts. |
| MP16 | Loan Account Detail | Loan Account | View outstanding balance, repayment schedule, statements and loan documents. |
| MP17 | Repayments | Repayments | View payment due dates, repayment history and acknowledgements. |
| MP18 | Direct Repayment Information | Repayments | Show SFPCL bank transfer instructions and post-payment reference submission if enabled. |
| MP19 | Notices & Letters | Communications | View deficiency notes, sanction letters, repayment reminders, interest invoices and NOC. |
| MP20 | Closure & NOC | Closure | Track full repayment closure, NOC and security return / unpledge. |
| MP21 | Grievance Submission | Support | Raise query, complaint or service request. |
| MP22 | Grievance Detail & Tracking | Support | View response status and messages. |
| MP23 | Notifications Center | Notifications | View all portal alerts and notices. |
| MP24 | Help & Required Documents Guide | Support | Explain eligibility, required documents, process stages and contact points. |
| MP25 | Profile Security Settings | Account | Change password, manage sessions and optional MFA / OTP settings. |

---

# 7. Detailed Screen Specifications

## MP00 — Member Portal Login

### Purpose

Allow a registered member / borrower to securely access the Member Portal.

### Primary Users

- Borrower / Member.
- FPC / Producer Institution authorised representative.

### Layout

1. SFPCL logo and product name.
2. Login form card.
3. Help text for first-time users.
4. Links for account activation, forgot password and support.
5. Privacy and security notice.

### Fields

| Field | Type | Required | Validation |
|---|---|---:|---|
| Mobile number / email | Text | Yes | Must match registered portal account. |
| Password / OTP | Password / OTP | Yes | Configured authentication policy. |
| Remember device | Checkbox | No | Only if allowed by security policy. |

### Actions

| Action | Behaviour |
|---|---|
| Login | Authenticates user and opens MP03 Dashboard. |
| Login with OTP | Sends OTP to registered mobile / email if enabled. |
| Activate account | Opens MP01. |
| Forgot password | Opens MP02. |

### Validations and Errors

- Show generic invalid credential message without revealing whether the user exists.
- Lock or rate-limit after repeated failed attempts.
- Block inactive / suspended portal users.
- If member has no portal access, show support instructions.

### Security Notes

- No PAN, Aadhaar or bank data should appear on the login screen.
- Use secure session handling and logout.

---

## MP01 — Account Activation / First-Time Access

### Purpose

Allow an eligible member to activate portal access by verifying identity against member records.

### Layout

1. Stepper: Identify Member -> Verify OTP -> Set Password -> Confirm.
2. Identity verification form.
3. Support fallback for mismatched records.

### Fields

| Field | Type | Required | Notes |
|---|---|---:|---|
| Folio number / Member ID | Text | Yes | Primary membership lookup. |
| Registered mobile / email | Text | Yes | Must match SFPCL record or trigger assisted support. |
| PAN last 4 characters | Text | Conditional | Used only for verification; do not display full PAN. |
| Aadhaar last 4 digits | Text | Conditional | Used only for verification; do not display full Aadhaar. |
| OTP | Numeric | Yes | Sent to registered contact. |
| New password | Password | Yes | Must meet password rules. |
| Confirm password | Password | Yes | Must match. |

### Actions

| Action | Behaviour |
|---|---|
| Verify member | Checks member record and contact match. |
| Send OTP | Sends OTP to registered channel. |
| Set password | Activates portal account. |
| Contact support | Opens grievance / support request path if verification fails. |

### Validations

- Member must exist.
- User must be authorised for that member record.
- OTP must expire after configured time.
- Failed attempts must be rate-limited.

---

## MP02 — Forgot Password / OTP Verification

### Purpose

Allow portal users to regain account access securely.

### Fields

| Field | Type | Required |
|---|---|---:|
| Registered mobile / email | Text | Yes |
| OTP | Numeric | Yes |
| New password | Password | Yes |
| Confirm password | Password | Yes |

### Actions

- Send OTP.
- Verify OTP.
- Reset password.
- Return to login.

### Validations

- Do not reveal whether an entered account exists.
- Revoke active sessions after successful password reset.
- Audit the password reset event.

---

## MP03 — Member Portal Dashboard

### Purpose

Give the borrower a simple summary of applications, active loans, pending tasks and repayment alerts.

### Layout

1. Welcome header with member name.
2. Member summary card.
3. Pending actions card.
4. Active application / active loan card.
5. Repayment summary card.
6. Recent notifications.
7. Quick actions.

### Widgets

| Widget | Content |
|---|---|
| Member Summary | Member type, folio number, active status, shares held, contact status. |
| Pending Actions | Missing documents, deficiency response, signature pending, repayment due, KYC update due. |
| Application Status | Latest application number, stage, pending with, next step. |
| Active Loan | Loan account number, outstanding principal, accrued interest if shown, next due date. |
| Documents | Count of uploaded, pending, rejected and accepted documents. |
| Notices | Latest deficiency note, sanction update, reminder, repayment acknowledgement or NOC. |

### Primary Actions

| Action | Destination |
|---|---|
| Apply for loan | MP05 |
| Continue draft | MP06 / MP08 |
| Upload documents | MP07 |
| View application | MP10 |
| View loan | MP16 |
| View repayments | MP17 |
| Raise grievance | MP21 |

### Empty States

- If no application exists: “You have not applied for a loan yet. Start a new application.”
- If application is under internal review: “Your application is with SFPCL for review. No action is required from you right now.”
- If no active loan exists: “No active loan account is available.”

---

## MP04 — My Profile

### Purpose

Show borrower/member details used for loan applications and allow limited self-service updates.

### Layout

Tabs:

1. Member Details.
2. Contact Details.
3. Nominee Details.
4. Shareholding.
5. Land & Crop Details.
6. Bank Details.
7. KYC Status.

### Fields

#### Member Details

| Field | Behaviour |
|---|---|
| Member name | Read-only from member master. |
| Member type | Individual / FPC / Producer Institution. |
| Folio number | Read-only. |
| Active status | Read-only status with explanation. |
| Shares held | Read-only or verified display. |

#### Contact Details

| Field | Behaviour |
|---|---|
| Mobile number | Editable if verification workflow is enabled. |
| Email | Editable if verification workflow is enabled. |
| Address | Editable as self-declared update; requires SFPCL verification if used for legal documents. |

#### Nominee Details

| Field | Behaviour |
|---|---|
| Nominee name | Editable in draft application; profile-level update may require verification. |
| Nominee age / DOB | Must confirm nominee is not minor. |
| Nominee PAN | Masked display after upload / verification. |
| Nominee Aadhaar | Masked display after upload / verification. |

#### Land, Crop and Bank

| Field | Behaviour |
|---|---|
| Land record summary | Read-only from last application unless update allowed. |
| Crop plan summary | Editable in draft application. |
| Bank account last 4 digits | Masked display only. |
| IFSC and branch | Display after verification if allowed. |

### Actions

- Edit contact details.
- Add / update nominee in draft application.
- Upload KYC update.
- Request profile correction.

### Validations

- Full PAN / Aadhaar must not be shown after submission.
- Bank account number must be masked.
- Changes affecting legal records should be submitted as correction requests rather than directly changing approved data.

---

## MP05 — New Loan Application — Start

### Purpose

Start a new loan application and confirm that the member can proceed.

### Layout

1. Eligibility introduction.
2. Member validation summary.
3. Loan purpose selection.
4. Previous / active loan warning, if any.
5. Start application button.

### Fields

| Field | Type | Required | Validation |
|---|---|---:|---|
| Member / folio number | Auto-filled / read-only | Yes | Must match logged-in user. |
| Applying as | Individual / FPC / Producer Institution | Yes | Based on member type. |
| Loan purpose | Dropdown | Yes | Must be agriculture / crop-production related. |
| Requested amount estimate | Currency | Optional | Final amount captured in MP06. |
| Existing loan declaration | Checkbox | Conditional | Required if active loan rules apply. |

### Actions

| Action | Behaviour |
|---|---|
| Check eligibility to apply | Runs basic member and active status checks. |
| Start application | Creates draft and opens MP06. |
| Save and exit | Saves draft start state. |

### Blocking Conditions

- Logged-in user is not mapped to a valid member.
- Member status does not allow application.
- Loan purpose is non-agricultural.
- Existing unresolved disqualification exists.
- Portal self-application is disabled by configuration.

---

## MP06 — Loan Application Form

### Purpose

Capture the complete borrower loan request for submission to SFPCL.

### Layout

Use a multi-step form:

1. Borrower and Member Details.
2. Loan Request.
3. Nominee Details.
4. Land and Crop Details.
5. Bank Details.
6. Declarations.

### Fields

#### Borrower and Member Details

| Field | Required | Notes |
|---|---:|---|
| Borrower name | Yes | Auto-filled; editable only if correction process is enabled. |
| Member type | Yes | Auto-filled. |
| Folio number | Yes | Auto-filled. |
| Number of shares held | Yes | Display from member record or entered for verification. |
| PAN | Yes | Enter/upload; display masked after save. |
| Aadhaar / OVD | Yes for individuals | Enter/upload; display masked after save. |
| Contact details | Yes | Mobile and address required. |

#### Loan Request

| Field | Required | Notes |
|---|---:|---|
| Requested loan amount | Yes | Currency input. |
| Loan purpose | Yes | Must be agriculture / crop production / allied productive purpose. |
| Crop / activity financed | Yes | Controlled list + other with explanation. |
| Expected repayment date | Recommended | May be calculated from product configuration. |
| Repayment route | Yes | Direct RTGS / NEFT, subsidiary deduction, or both if allowed. |

#### Nominee Details

| Field | Required | Notes |
|---|---:|---|
| Nominee name | Yes | Required for individual borrower. |
| Nominee age / date of birth | Yes | Must not be minor. |
| Nominee gender | Yes | Controlled values. |
| Nominee Aadhaar | Yes | Upload / masked. |
| Nominee PAN | Yes | Upload / masked. |
| Nominee contact | Recommended | For communication. |

#### Land and Crop Details

| Field | Required | Notes |
|---|---:|---|
| Land area | Yes | Used for land-based eligibility. |
| Village / survey details | Yes | Based on 7/12 extract. |
| Crop plan | Yes | Uploaded document and structured summary. |
| Season / crop cycle | Recommended | Helps appraisal review. |

#### Bank Details

| Field | Required | Notes |
|---|---:|---|
| Account holder name | Yes | Must match borrower or require bank verification letter / declaration. |
| Bank name | Yes | From cancelled cheque / statement. |
| Account number | Yes | Mask after entry. |
| IFSC | Yes | Format validation. |
| Branch | Yes | Auto-fetch if IFSC lookup exists or manual entry. |

#### Declarations

| Declaration | Required |
|---|---:|
| Loan purpose is agriculture / crop-production related. | Yes |
| Information provided is true and complete. | Yes |
| Borrower consents to KYC / CKYC and verification checks. | Yes |
| Borrower agrees that final sanction depends on SFPCL review and approval. | Yes |
| Borrower understands disbursement requires document completion and SFPCL approval. | Yes |

### Actions

- Save draft.
- Continue to documents.
- Validate current step.
- Delete draft, if not submitted.

### Validations

- Required fields must be complete before moving to review.
- Requested amount must be positive and within configured input limits.
- Nominee must not be a minor.
- Loan purpose must be allowed.
- Bank account and IFSC must pass format validation.

---

## MP07 — Document Upload Checklist

### Purpose

Collect mandatory KYC and supporting documents before application submission.

### Required Documents

| Document | Required For | Notes |
|---|---|---|
| Borrower PAN card copy | All borrowers | Self-attested. |
| Borrower Aadhaar / OVD | Individual borrowers | Self-attested; masked after verification. |
| Nominee PAN card copy | Individual borrower nominee | Self-attested. |
| Nominee Aadhaar / OVD | Individual borrower nominee | Self-attested. |
| Share certificate copy | All borrowers where applicable | Required for shareholding validation. |
| Land document / 7/12 extract | Agricultural land-based eligibility | Required unless policy exception applies. |
| Crop plan | All loan applications | Must support loan purpose. |
| Six-month bank statement | All borrowers | Used for appraisal. |
| Cancelled cheque | Before disbursement | May be collected at application stage. |
| Additional documents | Conditional | Based on member type, FPC / Producer Institution rules, or deficiency request. |

### Document Status Values

```text
Not Uploaded -> Uploaded -> Under Review -> Accepted / Rejected / Re-upload Required
```

### Actions

- Upload document.
- Replace document before submission.
- Add remarks.
- View upload status.
- Continue to review.

### Validations

- Mandatory documents must be uploaded before final submission unless assisted/offline submission is allowed.
- File size and type must match configuration.
- Duplicate document types should create new version, not overwrite audit history.

---

## MP08 — Application Review & Submission

### Purpose

Allow the borrower to review the completed application, confirm declarations and submit it to SFPCL.

### Layout

1. Application summary.
2. Borrower details.
3. Loan request details.
4. Nominee details.
5. Land, crop and bank details.
6. Uploaded document checklist.
7. Declarations and consent.
8. Submission confirmation.

### Actions

| Action | Behaviour |
|---|---|
| Edit section | Returns to relevant MP06 / MP07 step. |
| Download draft application | Generates draft copy if enabled. |
| Submit application | Locks borrower-editable fields and sends case to SFPCL. |
| Confirm submission | Final confirmation modal. |

### Submission Confirmation Copy

> Your application has been submitted to SFPCL for completeness review. You will receive an application reference number after the submitted details and documents are checked.

### Post-Submission Behaviour

- Status becomes `Submitted`.
- Borrower cannot edit submitted fields unless application is returned for rectification.
- Internal task is created for Deputy Manager – Finance / Credit Assessment Team.
- Borrower receives notification.

---

## MP09 — My Applications List

### Purpose

Show all applications belonging to the logged-in member.

### Columns

| Column | Behaviour |
|---|---|
| Application ref | Temporary draft ID or generated `LO` reference. |
| Submitted date | Blank for draft. |
| Requested amount | Currency. |
| Status | Status badge. |
| Pending with | Borrower or SFPCL. |
| Last updated | Date / time. |
| Action | Continue, View, Respond, Download. |

### Filters

- Draft.
- Submitted.
- Deficiency raised.
- Under review.
- Approved.
- Rejected.
- Disbursed.
- Closed.

### Actions

- Start new application.
- Continue draft.
- View application detail.
- Respond to deficiency.
- Download acknowledgment / note where available.

---

## MP10 — Application Status Detail

### Purpose

Give a clear borrower-facing view of application progress after submission.

### Layout

1. Status stepper.
2. Current stage explanation.
3. Action required card.
4. Application summary.
5. Documents status.
6. Messages / notices.
7. Timeline.

### Stage Labels

| Internal Stage | Borrower-Facing Label |
|---|---|
| Submitted | Application submitted. |
| Completeness Check | SFPCL is checking your application. |
| Deficiency Raised | Action needed from you. |
| Appraisal In Progress | SFPCL is assessing eligibility and loan details. |
| Credit Manager Review | Internal review in progress. |
| Sanction Pending | Approval review in progress. |
| Approved | Loan approved subject to terms and documentation. |
| Rejected | Application not approved. |
| Documentation Pending | Documents / signatures pending. |
| SAP Setup | Finance processing in progress. |
| Disbursement Pending | Payment processing in progress. |
| Disbursed | Loan amount has been disbursed. |

### Borrower Actions by Stage

| Stage | Borrower Action |
|---|---|
| Submitted | No action unless contacted. |
| Deficiency Raised | Review note and upload / correct required items. |
| Approved | View sanction terms and complete documentation actions. |
| Documentation Pending | Download / sign / upload required documents as configured. |
| Disbursement Pending | No action unless bank verification issue is raised. |
| Rejected | View borrower-facing reason and reapply guidance. |

### Timeline Events

- Draft created.
- Application submitted.
- Completeness review started.
- Deficiency raised.
- Deficiency resolved.
- Reference number generated.
- Appraisal started.
- Sanction outcome recorded.
- Documentation started.
- Disbursement completed.

---

## MP11 — Deficiency Response

### Purpose

Allow the borrower to respond to missing / rejected documents or incorrect application details.

### Layout

1. Deficiency note summary.
2. List of required corrections.
3. Document re-upload controls.
4. Field correction controls, where allowed.
5. Borrower remarks.
6. Resubmit button.

### Fields

| Field | Type | Required |
|---|---|---:|
| Deficiency reason | Read-only | Yes |
| Requested correction | Read-only | Yes |
| Borrower response remark | Textarea | Recommended |
| Replacement document | File upload | Conditional |
| Corrected field value | Field-specific | Conditional |

### Actions

- Upload replacement document.
- Save response draft.
- Resubmit corrections.
- Download deficiency note.

### Validations

- All deficiency items must be responded to before resubmission unless marked not applicable by SFPCL.
- Re-upload must create new version.
- Resubmitted application returns to completeness check.

---

## MP12 — Sanction Outcome & Terms

### Purpose

Show borrower-facing approval or rejection outcome and sanctioned loan details.

### Approved State Content

| Field | Behaviour |
|---|---|
| Sanction status | Approved / Approved subject to documentation. |
| Sanctioned amount | Currency. |
| Approved purpose | Display approved loan purpose. |
| Interest rate / charges | Display if configured for borrower disclosure. |
| Repayment terms | Due date, repayment route and key obligations. |
| Documentation required | Link to MP13. |
| Term sheet | Download / view if generated and approved for borrower view. |

### Rejected State Content

| Field | Behaviour |
|---|---|
| Status | Not approved. |
| Borrower-facing reason | Plain-language reason. |
| Reapply guidance | Shows whether borrower can reapply after rectification. |
| Download rejection note | Available if configured. |

### Actions

- View term sheet.
- Accept terms, if digital acceptance is enabled.
- Continue to documentation.
- Raise question.

### Privacy Constraint

Do not show internal sanction committee comments, votes, approver names, authority logic or risk grading unless explicitly approved for borrower disclosure.

---

## MP13 — Documentation Actions

### Purpose

Guide the borrower through post-sanction document and signature requirements.

### Document Categories

| Document / Action | Borrower View |
|---|---|
| Term Sheet | View / download / acknowledge. |
| Loan Agreement | View / download / sign status. |
| Power of Attorney | View requirement and signing status. |
| Tri-party Agreement | Required if repayment through subsidiary deduction. |
| SH-4 | Required for physical shares; shows pending / submitted / accepted. |
| CDSL pledge | Required for demat shares; shows pledge pending / complete. |
| Cancelled cheque | Upload / accepted status. |
| Blank-dated cheque | Physical submission status only; do not display cheque details. |
| Bank verification letter / declaration | Required if signature mismatch or bank mismatch. |

### Actions

- Download document for signing.
- Upload signed document copy if digital upload is allowed.
- View physical submission instructions.
- Confirm appointment / office submission, if scheduling is enabled.
- View document status.

### Status Values

```text
Not Required / Required / Pending Borrower / Submitted / Under SFPCL Review / Accepted / Rejected / Completed
```

### Validations

- Borrower cannot mark legal documents as accepted; only internal authorised users can verify.
- Portal can record borrower submission but not final document approval.
- Missing mandatory documentation blocks disbursement.

---

## MP14 — Disbursement Status

### Purpose

Show where the approved loan is in finance processing and confirm disbursement once completed.

### Status Labels

| Internal State | Borrower-Facing Label |
|---|---|
| Documentation Complete | Documents completed. |
| SAP Customer Code Pending | Finance setup in progress. |
| Payment Initiated | Payment is being processed. |
| CFC Authorisation Pending | Payment approval in progress. |
| Disbursed | Loan amount transferred. |
| Disbursement Blocked | Action required / SFPCL review needed. |

### Fields

| Field | Behaviour |
|---|---|
| Sanctioned amount | Display. |
| Disbursement amount | Display after payment is finalised. |
| Bank account last 4 digits | Masked. |
| Disbursement date | Display after completed. |
| UTR / bank reference | Display if configured. |
| Disbursement advice | Downloadable borrower copy. |

### Actions

- View disbursement advice.
- Raise bank detail concern.
- Contact support.

### Rules

- Do not display internal bank authoriser details.
- Do not show complete bank account number.
- If payment fails or is returned, show borrower-friendly action required message only after internal review.

---

## MP15 — My Loans

### Purpose

List active and closed loan accounts for the member.

### Columns

| Column | Behaviour |
|---|---|
| Loan account number | Opens MP16. |
| Application reference | Link to application. |
| Disbursed amount | Currency. |
| Outstanding principal | Currency. |
| Repayment status | On track, due soon, overdue, closed. |
| Next due date | Date. |
| Closure status | Active / closed / NOC issued. |

### Actions

- View loan.
- View repayments.
- Download statement.
- View NOC, if issued.

---

## MP16 — Loan Account Detail

### Purpose

Provide a borrower-facing loan account view after disbursement.

### Layout

1. Loan summary.
2. Outstanding balance.
3. Repayment schedule.
4. Repayment history.
5. Interest and invoice summary.
6. Documents and notices.
7. Closure status.

### Fields

| Field | Behaviour |
|---|---|
| Loan account number | Display. |
| Disbursement date | Display. |
| Disbursed amount | Display. |
| Outstanding principal | Display. |
| Interest due / accrued | Display if approved for borrower view. |
| Next repayment date | Display. |
| Repayment route | Direct / subsidiary deduction / both. |
| Loan status | Active / overdue / closed. |

### Actions

- Download statement.
- View repayment schedule.
- View repayment history.
- View notices.
- Raise grievance.

---

## MP17 — Repayments

### Purpose

Show repayment schedule, received payments and outstanding amounts.

### Sections

1. Next payment due.
2. Repayment schedule.
3. Repayment history.
4. Direct transfer instructions.
5. Subsidiary deduction history.
6. Interest invoices.

### Repayment Schedule Columns

| Column | Behaviour |
|---|---|
| Due date | Scheduled repayment date. |
| Principal due | Currency. |
| Interest due | Currency, if disclosed. |
| Amount paid | Currency. |
| Status | Upcoming, paid, partly paid, overdue. |

### Repayment History Columns

| Column | Behaviour |
|---|---|
| Receipt date | Bank / SAP confirmation date. |
| Amount received | Currency. |
| Allocation | Principal / interest split where approved for borrower view. |
| Payment mode | Direct RTGS / NEFT, subsidiary deduction. |
| Reference | UTR / deduction reference if available. |
| Acknowledgement | Download. |

### Rules

- Payment shown only after SFPCL confirmation.
- Partial repayment must reflect principal-first allocation as per configured SOP rule.
- Unmatched payments should show “Under verification” only if borrower-submitted proof is enabled.

---

## MP18 — Direct Repayment Information

### Purpose

Provide borrower instructions for direct RTGS / NEFT repayment and optionally allow payment reference submission.

### Fields / Content

| Field | Behaviour |
|---|---|
| SFPCL bank account details | Display only approved repayment account details. |
| Required narration | Tell borrower to include loan application / loan account number. |
| Amount due | Display due amount. |
| Payment reference / UTR | Optional borrower-submitted field, if enabled. |
| Payment proof upload | Optional, subject to verification. |

### Actions

- Copy bank details.
- Submit UTR / reference.
- Upload proof, if enabled.
- View confirmation status.

### Disclaimer Copy

> Repayment will be updated in the portal after SFPCL verifies the bank receipt and posts the repayment in its records.

---

## MP19 — Notices & Letters

### Purpose

Provide a secure borrower-facing document center for notices, letters and downloadable outputs.

### Document Types

- Application acknowledgment.
- Deficiency / rejection note.
- Sanction communication.
- Term sheet.
- Loan agreement borrower copy.
- Disbursement advice.
- Repayment acknowledgement.
- Interest invoice.
- Reminder notice.
- Default / recovery notice addressed to borrower.
- NOC.

### Columns

| Column | Behaviour |
|---|---|
| Date | Date issued. |
| Type | Notice / letter type. |
| Related application / loan | Reference. |
| Status | New, viewed, acknowledged if required. |
| Action | View / download. |

### Rules

- Do not expose internal notes or registers.
- Documents must be watermarked / marked as borrower copy where applicable.
- Downloads must be audited.

---

## MP20 — Closure & NOC

### Purpose

Allow borrower to track closure after full repayment and download NOC when issued.

### Fields

| Field | Behaviour |
|---|---|
| Full repayment status | Pending / confirmed. |
| Closure review | Not started / in progress / complete. |
| NOC status | Pending / issued. |
| Security return status | SH-4 / cheque return pending / complete. |
| CDSL unpledge status | Not applicable / pending / completed. |
| Archive status | Internal only; show “loan closed” to borrower. |

### Actions

- Download NOC.
- View security return / unpledge status.
- Raise closure query.

### Rules

- NOC appears only after internal authorised issuance.
- Physical security details should be limited to status and return acknowledgement, not complete instrument details.

---

## MP21 — Grievance Submission

### Purpose

Allow the borrower to raise service requests, complaints or questions.

### Fields

| Field | Type | Required |
|---|---|---:|
| Related application / loan | Dropdown | Conditional |
| Category | Dropdown | Yes |
| Subject | Text | Yes |
| Description | Textarea | Yes |
| Attachment | File upload | Optional |
| Preferred contact channel | Dropdown | Optional |

### Categories

- Application help.
- Document issue.
- Loan status query.
- Disbursement query.
- Repayment query.
- Interest / invoice query.
- Closure / NOC query.
- Data correction request.
- Other complaint.

### Actions

- Submit grievance.
- Save draft, if enabled.
- View submitted grievance.

### Output

- Grievance reference number.
- Acknowledgment message.
- Internal task for grievance owner.

---

## MP22 — Grievance Detail & Tracking

### Purpose

Show status and responses for borrower grievances.

### Fields

| Field | Behaviour |
|---|---|
| Grievance reference | Display. |
| Category | Display. |
| Status | Submitted, Under review, Response provided, Closed, Reopened. |
| Assigned department | Optional borrower-friendly label, not individual user if not required. |
| Timeline | Submitted, response updates, closure. |
| Response | Borrower-facing response. |

### Actions

- Add reply.
- Upload additional information.
- Mark resolved, if enabled.
- Reopen within configured period.

---

## MP23 — Notifications Center

### Purpose

Show all borrower-facing notifications in one place.

### Notification Types

- Application submitted.
- Reference number generated.
- Deficiency raised.
- Deficiency response accepted / rejected.
- Sanction approved / rejected.
- Documentation pending.
- Disbursement completed.
- Repayment due soon.
- Payment received.
- Overdue reminder.
- Interest invoice issued.
- NOC issued.
- Grievance response received.

### Actions

- Mark as read.
- Open related application / loan / document.
- Download related letter.

---

## MP24 — Help & Required Documents Guide

### Purpose

Help borrowers understand the loan process, eligibility, required documents and next steps.

### Content Sections

1. Who can apply.
2. What loan purposes are allowed.
3. Required documents.
4. Application steps.
5. What happens after submission.
6. Documentation and signing guidance.
7. Disbursement process overview.
8. Repayment methods.
9. Closure and NOC.
10. Support and grievance contact.

### Rules

- Keep content borrower-friendly and localisable.
- Explain that final loan approval is subject to SFPCL review.
- Avoid disclosing internal approval thresholds or sensitive control details unless approved for public borrower guidance.

---

## MP25 — Profile Security Settings

### Purpose

Allow the portal user to manage account security.

### Fields / Actions

| Item | Behaviour |
|---|---|
| Change password | Requires current password / OTP. |
| Registered mobile / email | View masked; update through verification flow. |
| Active sessions | View current sessions if enabled. |
| Logout from all devices | Revokes sessions. |
| MFA / OTP preference | Optional if enabled. |

### Security Rules

- Sensitive profile changes require OTP.
- Password change revokes other sessions if configured.
- Security events must be audited.

---

# 8. Portal-to-Internal Workflow Handoff

## 8.1 Application Submission Handoff

When a borrower submits MP08:

1. System creates / updates loan application record.
2. Status becomes `Submitted`.
3. Borrower editing is locked.
4. Internal task is created for Deputy Manager – Finance completeness check.
5. Credit Manager can view application in internal Loan Request workflow.
6. Borrower receives application submission notification.

## 8.2 Deficiency Handoff

When internal team raises deficiency:

1. Borrower receives notification.
2. MP11 shows required corrections.
3. Borrower submits response.
4. Application status becomes `Resubmitted` / `Returned to SFPCL Review`.
5. Internal completeness task is reopened.

## 8.3 Sanction Handoff

When sanction decision is recorded internally:

- Approved cases publish borrower-facing approved state in MP12.
- Rejected cases publish borrower-facing rejection state and any approved reapply guidance.
- Internal notes and approval comments remain hidden.

## 8.4 Documentation Handoff

When documentation is required:

1. MP13 displays borrower-required documents and signatures.
2. Borrower uploads or acknowledges required items where enabled.
3. Internal Compliance / Company Secretary roles review and approve documentation.
4. Borrower sees accepted / rejected / pending status only.

## 8.5 Disbursement Handoff

After internal documentation approval, SAP setup and finance approval:

1. MP14 moves from processing to disbursed.
2. Borrower can view disbursement date, amount and reference if configured.
3. Disbursement advice becomes available in MP19.
4. Loan account appears in MP15 / MP16.

## 8.6 Repayment Handoff

When repayment is received and verified internally:

1. MP17 updates repayment history.
2. Outstanding balance updates.
3. Repayment acknowledgement appears in MP19.
4. If overdue, borrower receives reminder notifications.

---

# 9. Status, Validation and Error Rules

## 9.1 Key Status Values

| Object | Status Values |
|---|---|
| Portal account | Not activated, Active, Locked, Suspended. |
| Application | Draft, Submitted, Deficiency Raised, Resubmitted, Under Review, Approved, Rejected, Documentation Pending, Disbursement Processing, Disbursed. |
| Document | Not Uploaded, Uploaded, Under Review, Accepted, Rejected, Re-upload Required. |
| Loan account | Active, Due Soon, Overdue, Grace Period, Under Recovery Review, Closed. |
| Grievance | Submitted, Under Review, Response Provided, Closed, Reopened. |

## 9.2 Hard Validation Rules

- Portal user can access only own records.
- Loan purpose must be allowed under configured agricultural / crop-production categories.
- Nominee must not be a minor.
- Mandatory KYC and supporting documents must be uploaded before submission unless assisted/offline exception is configured.
- Full PAN, Aadhaar and bank account numbers must not be displayed after capture.
- Borrower cannot approve, verify or override internal checks.
- Borrower cannot self-mark documents as accepted.
- Borrower cannot edit submitted applications unless returned for rectification.
- Disbursement status cannot show as complete until internal disbursement completion is recorded.
- Repayment cannot show as received until SFPCL verifies and posts it.

## 9.3 Common Error Messages

| Scenario | Message |
|---|---|
| Invalid login | The login details are incorrect. Please try again or reset your password. |
| Member not found | We could not verify your member details. Please check the information or contact SFPCL support. |
| Non-agriculture purpose | This portal accepts loan requests only for eligible agriculture / crop-production purposes. |
| Missing document | Please upload the required document before submitting your application. |
| File upload failed | The document could not be uploaded. Please check the file type and size and try again. |
| Submitted application edit | This application has already been submitted. You can edit it only if SFPCL returns it for correction. |
| Internal review pending | Your application is under review. No action is required from you right now. |
| Repayment under verification | Your repayment reference has been received and will be updated after SFPCL verifies the bank receipt. |

---

# 10. Permissions Matrix for Member Portal Screens

| Screen | View | Create | Edit | Submit | Upload | Download |
|---|---:|---:|---:|---:|---:|---:|
| MP00 Login | Public | No | No | Yes | No | No |
| MP01 Account Activation | Public / invited member | Yes | Yes | Yes | No | No |
| MP03 Dashboard | Own only | No | No | No | No | No |
| MP04 My Profile | Own only | No | Limited | Correction request | KYC update | Limited |
| MP05 New Application Start | Own only | Yes | Yes | Yes | No | No |
| MP06 Application Form | Own draft only | Yes | Own draft / returned only | No | No | Draft copy |
| MP07 Documents | Own application only | No | Own pending docs | No | Yes | Own docs only |
| MP08 Review & Submission | Own draft only | No | No | Yes | No | Draft copy |
| MP09 Applications List | Own only | No | No | No | No | Acknowledgments / notes |
| MP10 Application Status | Own only | No | No | No | No | Published letters |
| MP11 Deficiency Response | Own returned application | No | Yes | Yes | Yes | Deficiency note |
| MP12 Sanction Outcome | Own only | No | No | Acknowledge if enabled | No | Sanction / rejection docs |
| MP13 Documentation Actions | Own approved application | No | Limited | Acknowledge / submit | Yes | Published docs |
| MP14 Disbursement Status | Own only | No | No | No | No | Disbursement advice |
| MP15 My Loans | Own only | No | No | No | No | Statement / NOC |
| MP16 Loan Detail | Own only | No | No | No | No | Statement |
| MP17 Repayments | Own only | No | No | No | Proof if enabled | Acknowledgment |
| MP18 Direct Repayment Info | Own loan only | No | UTR if enabled | Submit reference | Proof if enabled | Instructions |
| MP19 Notices & Letters | Own only | No | No | Acknowledge if enabled | No | Yes |
| MP20 Closure & NOC | Own closed / closing loan | No | No | No | No | NOC |
| MP21 Grievance Submission | Own only | Yes | Draft only | Yes | Yes | No |
| MP22 Grievance Detail | Own only | Reply | Reply | Yes | Yes | Attachments / response |
| MP23 Notifications | Own only | No | Mark read | No | No | Related docs |
| MP24 Help | Public / portal user | No | No | No | No | Guides if enabled |
| MP25 Security Settings | Own account | No | Yes | Yes | No | No |

---

# 11. Audit Events

The portal must record audit events for all critical actions.

| Event | Trigger |
|---|---|
| `portal.login.success` | Successful member login. |
| `portal.login.failed` | Failed login attempt. |
| `portal.account.activated` | First-time account activation completed. |
| `portal.application.draft_created` | New draft application created. |
| `portal.application.saved` | Draft application saved. |
| `portal.application.submitted` | Application submitted to SFPCL. |
| `portal.document.uploaded` | Borrower uploads document. |
| `portal.deficiency.responded` | Borrower responds to deficiency. |
| `portal.terms.acknowledged` | Borrower acknowledges sanction terms / term sheet if enabled. |
| `portal.document.downloaded` | Borrower downloads issued document. |
| `portal.repayment_reference.submitted` | Borrower submits UTR / payment proof if enabled. |
| `portal.grievance.created` | Borrower submits grievance. |
| `portal.grievance.replied` | Borrower replies to grievance. |
| `portal.password.changed` | User changes password. |
| `portal.logout` | User logs out. |

Audit records should include user ID, member ID, application / loan ID, timestamp, IP/device metadata where available, action, result and linked document/version ID where applicable.

---

# 12. Data Privacy and Masking

| Data Type | Portal Display Rule |
|---|---|
| PAN | Mask except last 4 characters after capture. |
| Aadhaar | Mask except last 4 digits after capture; do not store/display in plain text. |
| Bank account | Mask except last 4 digits. |
| Cancelled cheque | View/download restricted; borrower may see upload status. |
| Blank-dated cheque | Show physical submission / return status only; do not show cheque details. |
| Internal appraisal | Hidden. |
| Sanction committee comments | Hidden. |
| Internal audit logs | Hidden; borrower activity timeline only. |
| Other members' data | Never visible. |

---

# 13. Responsive and Accessibility Requirements

- Portal must support desktop, tablet and mobile layouts.
- Primary application flow must be usable on mobile.
- Forms must support save-and-resume.
- File upload must show progress and retry state.
- Required fields must be clearly marked.
- Error messages must be placed near the field and summarised at top of step.
- Buttons must have clear labels such as `Save Draft`, `Continue`, `Submit Application`, `Upload Document`.
- Screens must support keyboard navigation and sufficient contrast.
- Dates, currency and statuses must use consistent formatting.

---

# 14. Acceptance Criteria

## 14.1 Login and Access

- Borrower can activate account using verified member details and OTP.
- Borrower can log in and view only their own records.
- Inactive or unauthorised portal accounts are blocked.
- Password reset revokes existing sessions.

## 14.2 Application Submission

- Borrower can create, save and resume a draft loan application.
- Application captures member, loan, nominee, land, crop, bank and declaration details.
- Mandatory documents are uploaded before submission unless configuration allows assisted/offline completion.
- Submitted application is locked from direct editing.
- Internal completeness task is created after submission.

## 14.3 Application Tracking

- Borrower can view current application stage and next action.
- Deficiency notes show clear correction requirements.
- Borrower can respond to deficiencies and resubmit.
- Approval and rejection outcomes display borrower-facing information only.

## 14.4 Documentation and Disbursement

- Approved borrower can view required documentation actions.
- Borrower can download published term sheet / agreement copies where enabled.
- Disbursement status updates only after internal finance events are completed.
- Disbursement advice is available after successful disbursement.

## 14.5 Loan and Repayment

- Disbursed loan appears in My Loans.
- Borrower can view repayment schedule, outstanding amount and repayment history.
- Repayments appear only after verification/posting.
- Direct repayment reference submission, if enabled, is marked under verification until confirmed.

## 14.6 Closure and Support

- NOC appears only after authorised issuance.
- Security return / unpledge status is visible in borrower-safe language.
- Borrower can raise and track grievances.
- All critical borrower actions create audit events.

---

# 15. Out of Scope / Configuration Decisions

The following items require product or client confirmation before implementation:

1. Whether Member Portal is part of MVP or future release.
2. Whether account activation uses mobile OTP, email OTP, password, or both.
3. Whether digital signatures / eSign are enabled or only upload / physical signing is tracked.
4. Whether borrower can upload repayment proof or only view confirmed payments.
5. Whether full interest calculation details are borrower-facing.
6. Whether FPC / Producer Institution accounts support multiple authorised representatives.
7. Whether multilingual content is required at launch.
8. Whether external online payment collection is supported or repayment instructions only.
9. Whether portal exposes active-member evidence or only active status.
10. Which generated documents are downloadable by borrower and at what stage.

---

# 16. Final Product Interpretation

The Member Portal should make the SFPCL loan process understandable to members without weakening internal controls. The borrower should be able to apply, submit documents, respond to deficiencies, track the status, view sanctioned terms, follow documentation requirements, receive disbursement and repayment updates, and obtain closure documents. Internal credit appraisal, approval authority, compliance checks, SAP setup, finance authorisation and audit evidence remain controlled inside the internal platform.

The most important design principle is: **the member sees what they need to do and what has happened; internal teams retain authority over verification, approval, disbursement, repayment posting, recovery and closure.**
