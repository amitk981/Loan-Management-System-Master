# Product Requirements Document — SFPCL Member Credit Administration & Loan Disbursement Platform

## 1. Document Control

| Field | Value |
|---|---|
| Document name | `product-requirements.md` |
| Product / system | SFPCL Member Credit Administration & Loan Disbursement Platform |
| Client | Sahyadri Farmers Producer Company Limited |
| Backend | Python + Django + Django REST Framework |
| Frontend | React |
| Database | PostgreSQL |
| Authentication | JWT |
| Supporting services | Redis, Celery, Celery Beat, object storage / DMS, email gateway, SMS gateway, SAP adapter, bank adapter, CDSL tracking adapter and future CKYC / bureau / e-sign adapters |
| Product type | Internal compliance-controlled lending workflow platform |
| PRD method | Conversation/context synthesis, no further interview, Matt Pocock `to-prd` style |
| Issue-conversion method | PRD structured for vertical tracer-bullet issue slicing, Matt Pocock `to-issues` style |
| Source basis | Uploaded SOP PDFs and all current analysis artifacts created so far: client brief, user flows, functional spec, information architecture, screen spec, content spec, component spec, design system, domain model, data model, technical architecture, API contracts, auth-permissions, integrations, security/privacy, deployment/ops, implementation roadmap, codebase design and test plan |
| Intended audience | Product owners, engineering leads, implementation team, QA, DevOps, SFPCL business stakeholders, compliance, finance, credit team, Company Secretary, CFO, Directors and future issue-authoring agents |
| Status | Detailed PRD draft for issue breakdown and implementation planning |

---

## 2. How to Use This PRD

This PRD is designed to be directly usable as the parent product requirements document for converting the platform scope into independently grabbable engineering issues.

It deliberately includes:

1. A full problem statement.
2. A user-facing solution statement.
3. Detailed personas and operating context.
4. Exhaustive user stories.
5. Functional requirements grouped by product domain.
6. Implementation decisions.
7. Testing decisions.
8. Acceptance criteria.
9. Non-functional requirements.
10. Out-of-scope items.
11. Open decisions.
12. A suggested vertical-slice issue breakdown.

This document should be used as follows:

```text
product-requirements.md
  -> vertical-slice issue breakdown
  -> individually implementable issues
  -> TDD / behaviour-first development
  -> QA and UAT scripts
  -> release readiness
```

The issue breakdown should avoid horizontal tickets such as “build all backend models” or “build all frontend screens”. Instead, each issue should be a thin but complete vertical slice that cuts through schema, backend module, API, frontend screen or action, permissions, audit and tests.

---

# 3. Problem Statement

Sahyadri Farmers Producer Company Limited provides credit facilities and secured loans/advances to members to support crop production, agricultural activities and related productive purposes. The current SOP defines a detailed controlled process, but the operational workflow is document-heavy, multi-role, approval-sensitive and dependent on manual registers, physical files, SAP, bank transfers, compliance evidence and internal follow-up.

From the user’s perspective, the key problems are:

1. **Loan processing is complex and spread across teams.** Credit Assessment, Compliance, Treasury, Sanction Committee, Company Secretary, Accounts and senior finance roles all participate in different stages.

2. **Documents and approvals are gate-critical.** A loan should not be disbursed unless member eligibility, loan limit, sanction approval, document execution, security instruments, SAP customer code and finance approval are complete.

3. **Registers and evidence must be audit-ready.** Loan Request Register, Credit Sanction Register, Exception Register, Loan Register, security custody records, repayment records, DPD reports and compliance trackers must be accurate, complete and traceable.

4. **Sensitive data is handled throughout the process.** PAN, Aadhaar, bank details, cancelled cheques, blank-dated cheques, KYC documents, bank statements, SH-4, PoA and CDSL pledge evidence must be protected.

5. **Approval governance is strict.** Loans up to ₹5 lakh require CFO + one Director; loans above ₹5 lakh require CFO + two Directors; exceptions and related-party cases need special handling.

6. **Loan limit rules are nuanced and contain an unresolved policy ambiguity.** The SOP references shareholding-based limits using 30% of valuation, while another section references 10% of share value / ₹200 per share. The system must support versioned configuration and make the active rule explicit.

7. **Legal documentation is difficult to track.** The process involves PoA, Tri-party Agreement, SH-4, CDSL pledge, Term Sheet, Loan Agreement, Bank Verification Letter, stamp duty, notarisation, witnesses and final checklist approvals.

8. **Disbursement has high financial risk.** The system must prevent disbursement before SAP customer code creation, documentation completion, security readiness, Senior Manager Finance initiation and CFC authorisation.

9. **Repayment and interest handling need consistency.** Direct and subsidiary repayments must be reconciled, allocated principal-first, posted to SAP, invoiced for interest, accrued monthly and capitalised after 30 April when unpaid.

10. **Default and recovery actions carry legal and reputational risk.** Grace period, non-intentional extension, Non-Payment Note and recovery approval must be enforced before invoking shares or blank-dated cheques.

11. **Compliance obligations are ongoing.** Section 186, NBFC principal business test, KYC/re-KYC, stamp duty, money-lending law review, recovery conduct, grievance handling, record retention and audit evidence must be monitored.

12. **Manual external systems must still be controlled.** SAP, bank portal, CDSL, subsidiary deduction and physical custody processes may remain manual in MVP, but the platform must record requests, references, evidence and status.

The central problem is:

```text
SFPCL needs one secure, auditable, role-based digital platform that turns the SOP into enforceable workflow controls, so that member loans can be processed efficiently without bypassing legal, credit, documentation, disbursement, repayment, recovery or compliance safeguards.
```

---

# 4. Solution

Build a Django + React + PostgreSQL platform that becomes the internal system of record for SFPCL’s member credit administration and loan disbursement workflow.

The solution will provide:

1. **A role-based internal application** for Credit, Compliance, Company Secretary, Finance, CFC, CFO, Directors, Accounts, Auditors, Admins and future borrower-facing extensions.

2. **A controlled loan lifecycle** from application to closure, with explicit states and workflow gates.

3. **Member and borrower master data** for individual farmers, FPCs / Producer Institutions, nominees, witnesses, shareholding, landholding, crop plan and KYC.

4. **Application intake and completeness checks** with unique loan reference number, required documents, deficiencies, resubmission and rejection.

5. **Eligibility and loan limit assessment** with active member checks, default checks, required document checks, purpose validation and share/land limit calculation.

6. **Credit appraisal and sanction workflow** with maker-checker review, approval matrix, CFO/Director approvals, exception register and related-party safeguards.

7. **Legal documentation and security package workflow** with document generation, upload, signatures, stamp duty, notarisation, PoA, SH-4, CDSL pledge, blank-dated cheque, cancelled cheque and custody tracking.

8. **SAP customer code workflow** in manual-first mode, with API-ready adapter design for future direct integration.

9. **Disbursement readiness and payment workflow** with Senior Manager Finance initiation, CFC authorisation, UTR capture, bank evidence and disbursement advice.

10. **Loan account servicing** with repayment schedule, direct repayment, subsidiary deduction, repayment allocation, SAP posting reference, interest invoices, accruals and capitalisation.

11. **Monitoring and default handling** with DPD buckets, reminders, quarterly MIS, default cases, grace periods, extensions and recovery.

12. **Closure and archival** with zero-balance readiness, NOC, security return/unpledge, archive location and retention tracking.

13. **Compliance dashboards and trackers** for Section 186, NBFC principal business test, KYC/re-KYC, stamp duty, money-lending law review, grievance handling and evidence review.

14. **Security and privacy controls** including JWT auth, RBAC, object-level permissions, sensitive data encryption/masking, restricted document access, export controls and immutable audit logs.

15. **Manual-first integration adapters** for SAP, bank, CDSL and subsidiary deduction, with future API adapter seams.

16. **Operational readiness** through CI/CD, monitoring, backups, runbooks, job tracking, alerts and UAT/regression test strategy.

The solution should be control-first and automation-second:

```text
First make every SOP gate, approval, document, security instrument, disbursement, repayment and audit record reliable inside the platform; then replace manual external steps with API integrations where provider readiness and business value justify it.
```

---

# 5. Product Goals

## 5.1 Business Goals

| Goal | Description |
|---|---|
| G1 — Digitise SOP execution | Convert the loan SOP into system-enforced workflow stages and approvals. |
| G2 — Reduce disbursement risk | Prevent disbursement unless eligibility, sanction, documents, security, SAP and finance gates pass. |
| G3 — Improve processing visibility | Give every role a dashboard of pending tasks, blockers and ageing. |
| G4 — Strengthen audit readiness | Capture who did what, when, why, under which role and with which evidence. |
| G5 — Protect sensitive data | Encrypt, mask and restrict access to borrower and legal data. |
| G6 — Standardise records | Replace ad-hoc Excel/manual registers with generated system registers. |
| G7 — Support statutory compliance | Track Section 186, NBFC test, KYC/re-KYC, stamp duty, money-lending law review and retention. |
| G8 — Enable controlled future automation | Prepare integration seams for SAP, bank, CKYC, bureau, e-sign and CDSL APIs. |

## 5.2 User Goals

| User Goal | Description |
|---|---|
| UG1 | Credit users can create, assess and track loan applications without missing documents or eligibility rules. |
| UG2 | Approvers can quickly review complete sanction packages and approve/reject with reasons. |
| UG3 | Compliance users can prepare and verify all legal/security documents before disbursement. |
| UG4 | Finance users can confidently initiate and authorise disbursements only when all gates pass. |
| UG5 | Accounts/Credit users can capture repayments and interest consistently. |
| UG6 | CFO and management can monitor portfolio risk, DPD, disbursements and compliance. |
| UG7 | Auditors can inspect complete evidence and audit logs without altering records. |
| UG8 | Admins can safely manage users, roles, permissions and policy configuration. |

## 5.3 Engineering Goals

| Goal | Description |
|---|---|
| EG1 | Build modular Django apps around deep domain modules. |
| EG2 | Keep business rules out of React pages and DRF views. |
| EG3 | Use public module interfaces as test seams. |
| EG4 | Use adapter seams for true external systems. |
| EG5 | Use behaviour-first TDD for critical modules. |
| EG6 | Use versioned configuration for policies and calculations. |
| EG7 | Maintain idempotency for financial and communication operations. |
| EG8 | Maintain audit logs for critical state changes. |

---

# 6. Success Metrics

## 6.1 Product Success Metrics

| Metric | Target / Interpretation |
|---|---|
| Application completeness TAT | Reduced manual back-and-forth; deficiencies visible and resolved. |
| Appraisal TAT | Deputy Manager and Credit Manager can meet 2-day SOP expectation. |
| Approval ageing | CFO/Director pending cases visible and reduced. |
| Documentation blocker count | Reduced missed documents before disbursement. |
| Disbursement readiness failures | All blockers visible before finance action. |
| Disbursement without full readiness | Zero. |
| Duplicate UTR / repayment reference | Zero accepted duplicates. |
| Repayment allocation correctness | 100% principal-first allocation unless policy changes. |
| Interest capitalisation duplicates | Zero. |
| Default cases without assessment | Zero after grace expiry. |
| Recovery action without approval | Zero. |
| NOC issuance after closure | Track and reduce delay. |
| Security return pending after closure | Track and reduce delay. |
| Compliance overdue tasks | Reduced and visible. |
| Audit evidence completeness | Critical workflow events have audit records. |
| Sensitive data exposure incidents | Zero. |

## 6.2 Delivery Success Metrics

| Metric | Target |
|---|---|
| Critical MVP scope delivered | 100% of signed-off MVP controls. |
| Open Sev 1 defects at go-live | 0. |
| Open unaccepted Sev 2 defects at go-live | 0. |
| UAT critical scripts executed | 100%. |
| Security critical tests passed | 100%. |
| Backup/restore readiness | Verified before go-live. |
| Role-based training completion | All key roles trained. |
| Hypercare issue response | Meets agreed SLA. |

---

# 7. Personas and Roles

## 7.1 Primary Internal Personas

### 7.1.1 Field Officer / Intake User

Responsible for initial application capture and document upload where field-assisted intake is implemented.

Needs:

- Search/select member.
- Create draft application.
- Upload documents.
- View deficiencies.
- Cannot approve, disburse or reveal high-sensitive data by default.

### 7.1.2 Deputy Manager – Finance

Responsible for completeness checks and preparing Loan Appraisal Notes.

Needs:

- Review applications.
- Validate required documents.
- Run eligibility.
- Prepare appraisal.
- Submit appraisal for Credit Manager review.
- Track 2-day TAT.

### 7.1.3 Credit Manager

Responsible for credit review, rejection, sanction submission, monitoring, repayments and DPD.

Needs:

- Review applications and appraisals.
- Reject ineligible applications.
- Submit to Sanction Committee.
- Review loan limits.
- Update Loan Register.
- Monitor repayments and DPD.
- Prepare MIS and default notes.

### 7.1.4 Compliance Team Member

Responsible for documentation preparation and collection.

Needs:

- Generate legal documents.
- Upload executed documents.
- Record signatures.
- Track stamp duty and notarisation.
- Complete document checklist.
- Prepare security package records.

### 7.1.5 Company Secretary

Responsible for legal documentation, PoA, SH-4, custody, security release, NOC and compliance controls.

Needs:

- Review and approve legal file.
- Verify PoA, SH-4, CDSL pledge and blank cheque custody.
- Track stamp duty compliance.
- Execute security-related actions after approval.
- Issue NOC and security return.
- Monitor money-lending law review and grievance handling.

### 7.1.6 Senior Manager – Finance

Responsible for SAP customer code workflow and disbursement initiation.

Needs:

- Receive SAP customer profile requests.
- Confirm SAP customer code.
- Review disbursement readiness.
- Initiate online payment.
- Record final finance checklist signature after disbursement.

### 7.1.7 Chief Financial Controller

Responsible for final bank payment authorisation.

Needs:

- View disbursement request and readiness evidence.
- Authorise or reject payment.
- Ensure bank transfer evidence and UTR are captured.

### 7.1.8 CFO

Responsible for sanction approval, exceptions, portfolio oversight and statutory trackers.

Needs:

- Review sanction cases.
- Approve/reject according to matrix.
- Approve exceptions and special cases.
- Review Section 186 and NBFC trackers.
- Review quarterly MIS and portfolio risk.

### 7.1.9 Directors / Executive Directors

Responsible for sanction approval as Sanction Committee members.

Needs:

- Review assigned approval cases.
- Approve/reject/return cases.
- Be excluded from conflicted related-party cases.
- See only relevant approval context.

### 7.1.10 Accounts Head / Accounts User

Responsible for accounting postings, accruals, interest invoices and repayment support.

Needs:

- View repayments.
- Capture SAP posting references.
- Generate/review accruals.
- Generate interest invoices.
- Support reconciliation.

### 7.1.11 Sales Team

Responsible for interest invoice issuance in some SOP references.

Needs:

- View loans requiring annual interest invoice.
- Generate/issue invoice where configured.
- Coordinate with Credit/Accounts.

### 7.1.12 Internal Auditor

Responsible for independent audit review.

Needs:

- Read-only access to loan files, registers, compliance trackers and audit logs.
- Export audit evidence where authorised.
- Cannot modify workflow records.

### 7.1.13 System Administrator / IT Head

Responsible for users, roles, permissions, access review and technical administration.

Needs:

- Manage users and role assignments.
- Configure access review.
- Monitor security events.
- Cannot perform business approvals unless assigned business role.

### 7.1.14 Management Viewer

Responsible for high-level portfolio oversight.

Needs:

- View dashboards and reports.
- No operational edit rights.
- Sensitive details masked.

## 7.2 Future Personas

| Persona | Future Need |
|---|---|
| Borrower / Member | View own application status, upload documents, receive notices, download NOC, raise grievance. |
| Subsidiary Finance User | Confirm produce-payment deductions and transfer references. |
| External Legal/Audit Reviewer | Controlled read-only access to selected evidence. |

---

# 8. Domain Scope

## 8.1 Core Domain Objects

| Domain Object | Meaning |
|---|---|
| Member | SFPCL shareholder/member eligible for member-only credit if active and compliant. |
| Individual Member Profile | Individual farmer borrower profile. |
| Producer Institution Profile | FPC / Producer Institution borrower profile. |
| Nominee | Borrower-linked nominee, not minor. |
| Witness | Existing SFPCL shareholder witnessing documents. |
| KYC Profile | PAN/Aadhaar/OVD/CKYC and verification status. |
| Shareholding | Shares held, physical/demat mode, folio and certificate/demat details. |
| Land Holding | 7/12 extract and cultivation area. |
| Crop Plan | Crop and cultivation plan supporting purpose/limit. |
| Loan Application | Initial request and application record. |
| Loan Appraisal Note | Credit assessment and recommendation. |
| Eligibility Assessment | Pass/fail assessment against SOP criteria. |
| Loan Limit Assessment | Shareholding and land-based limit snapshot. |
| Approval Case | Sanction Committee workflow instance. |
| Sanction Decision | Approved/rejected loan terms and decision record. |
| Exception Record | Policy or limit exception with approvals. |
| Loan Document | Generated or uploaded legal/documentary file. |
| Document Checklist | Required document and approval readiness list. |
| Security Package | PoA, SH-4/CDSL, cheque and custody readiness. |
| SAP Customer Request | Request to create SAP profile/customer code. |
| SAP Customer Code | SAP code linked to member. |
| Loan Account | Active financial account created from sanction. |
| Disbursement | Payment initiation, CFC authorisation and UTR. |
| Repayment | Direct or subsidiary repayment receipt. |
| Repayment Allocation | Principal-first allocation details. |
| Interest Invoice | Annual interest invoice. |
| Accrual Entry | Monthly accrual entry. |
| Interest Capitalisation | Unpaid interest added to principal after 30 April. |
| DPD Status | Days-past-due and bucket. |
| Default Case | Missed repayment and grace/assessment/extension workflow. |
| Recovery Decision | Approval to invoke security/recovery action. |
| Loan Closure | Closure record after full repayment. |
| NOC | No Objection Certificate after closure. |
| Security Return | Return/release/unpledge record. |
| Archive Record | Loan file storage/retention record. |
| Compliance Task | Statutory/internal compliance work item. |
| Audit Log | Immutable action/evidence record. |

---

# 9. Product Scope

## 9.1 MVP In Scope

| Area | MVP Scope |
|---|---|
| Authentication | JWT login, refresh, logout, reset, session tracking. |
| User and role management | Users, roles, teams, permissions, approval authority. |
| Member master | Individual and FPC profiles, nominees, witnesses, shareholding, land/crop. |
| KYC | PAN/Aadhaar, CKYC consent, document upload, verification, re-KYC due. |
| Loan origination | Application form, reference number, completeness, deficiencies, rejection. |
| Credit assessment | Eligibility, active member, default check, loan limit, appraisal. |
| Approval | Approval matrix, CFO/Director approvals, exceptions, conflicts, registers. |
| Documentation | Templates, document generation/upload, signatures, stamp duty, notarisation. |
| Security package | PoA, SH-4, CDSL pledge, cancelled cheque, blank-dated cheque, custody. |
| SAP | Manual SAP request, Excel, customer code confirmation, reuse. |
| Disbursement | Readiness, Senior Manager initiation, CFC authorisation, UTR, advice. |
| Loan account | Account creation, terms, status, ledger summary. |
| Repayments | Direct repayment, subsidiary deduction, principal-first allocation, SAP posting reference. |
| Interest | Invoice, accrual, unpaid interest and capitalisation. |
| Monitoring | DPD, reminders, quarterly MIS. |
| Default | Default case, grace, assessment, one-year extension. |
| Recovery | Non-Payment Note, approval, action tracking. |
| Closure | Full repayment readiness, NOC, security return, archive. |
| Compliance | Section 186, NBFC test, KYC/re-KYC, stamp duty, money-lending, grievance. |
| Reports | Registers, operational reports, compliance reports, audit explorer. |
| Security | Encryption/masking, restricted downloads, export controls, audit. |
| Operations | Health checks, workers, jobs, monitoring, backup/restore support. |

## 9.2 Future / Non-MVP Scope

| Feature | Reason for Deferral |
|---|---|
| Borrower portal | Internal process should stabilise first. |
| Native mobile app | Not necessary for internal MVP. |
| Direct SAP API | Manual workflow should be digitised before API automation. |
| Bank payment API | Manual bank portal + CFC control sufficient for MVP. |
| CKYC API | Provider and consent process must be confirmed. |
| Credit bureau API | Policy not final. |
| E-sign / e-stamp | Legal acceptability must be confirmed. |
| CDSL API | Depends on DP/CDSL availability. |
| AI document extraction | Not required for MVP controls. |
| Advanced data warehouse | Future analytics after operational data matures. |
| Automated legal recovery case management | Recovery process details still require clarification. |
| Multi-language borrower portal | Future borrower-facing phase. |

---

# 10. End-to-End Lifecycle Requirements

## 10.1 Lifecycle State Overview

The platform must support the following high-level lifecycle:

```text
Member / Borrower Setup
  -> Loan Application Draft
  -> Application Submitted
  -> Completeness Check
  -> Eligibility Assessment
  -> Loan Limit Assessment
  -> Appraisal
  -> Credit Manager Review
  -> Sanction Approval
  -> Documentation and Security
  -> SAP Customer Code
  -> Disbursement Readiness
  -> Payment Initiation
  -> CFC Authorisation
  -> Bank Transfer Success
  -> Active Loan Account
  -> Repayment / Interest / Monitoring
  -> Default / Recovery if needed
  -> Full Repayment
  -> Closure
  -> NOC
  -> Security Return
  -> Archive
```

## 10.2 Hard Gate Requirements

The system must enforce these gates:

| Gate | Must Block If |
|---|---|
| Appraisal start | Application incomplete, required documents missing, borrower/member not valid. |
| Sanction submission | Appraisal not reviewed by Credit Manager. |
| Sanction approval | Required CFO/Director approvals incomplete or conflicted approver present. |
| Documentation start | Sanction decision not approved. |
| Checklist approval | Required documents/security/signatures/stamp/notary missing. |
| SAP request | Sanction not approved. |
| Disbursement initiation | Readiness checks fail. |
| Disbursement success | CFC not authorised or UTR missing. |
| Repayment allocation | Duplicate reference or invalid loan state. |
| Interest capitalisation | Before 30 April or duplicate for same FY. |
| Recovery action | Recovery decision not approved. |
| Closure | Outstanding balance exists. |
| NOC | Loan not closed. |
| Archive | Closure/security return requirements not met as configured. |

---

# 11. Detailed Functional Requirements

## 11.1 Authentication and Session Management

### Requirements

1. The system must allow authorised internal users to log in using username/email and password.
2. The system must issue JWT access and refresh tokens.
3. The system must support refresh token rotation or revocation.
4. The system must revoke sessions on logout.
5. The system must block inactive/suspended users.
6. The system must support password reset.
7. The system must rate-limit failed login attempts.
8. The system should support MFA for privileged users in MVP or phase 2.
9. The system must expose current user profile, roles, teams and permissions.
10. The system must invalidate or re-evaluate permissions after role changes.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| AUTH-AC-001 | Valid user can log in and receive tokens. |
| AUTH-AC-002 | Invalid credentials return generic error. |
| AUTH-AC-003 | Inactive user cannot access protected APIs. |
| AUTH-AC-004 | Logout revokes refresh token. |
| AUTH-AC-005 | Protected endpoints return 401 without token. |
| AUTH-AC-006 | Current user endpoint returns roles, teams and permissions. |

---

## 11.2 Roles, Permissions and Object Access

### Requirements

1. The system must support role-based access control.
2. The system must support object-level access for applications, loans, approvals and documents.
3. The system must support team membership.
4. The system must support approval authority assignment.
5. The system must support read-only auditor access.
6. The system must support sensitive reveal permissions separately from normal read permissions.
7. The system must support export permissions separately from screen view permissions.
8. The backend must enforce all permissions independent of frontend visibility.
9. The frontend must show available actions based on backend response.
10. Role and permission changes must be audit logged.

### Required Roles

| Role | Required |
|---|---|
| Field Officer | Yes if field intake is enabled |
| Deputy Manager – Finance | Yes |
| Credit Manager | Yes |
| Compliance Team Member | Yes |
| Company Secretary | Yes |
| Senior Manager – Finance | Yes |
| Chief Financial Controller | Yes |
| CFO | Yes |
| Director / Executive Director | Yes |
| Accounts User | Yes |
| Sales Team | Optional but useful for interest invoice workflow |
| Internal Auditor | Yes |
| IT Head / System Admin | Yes |
| Management Viewer | Yes |
| Borrower Portal User | Future |

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| RBAC-AC-001 | Field Officer cannot approve sanctions. |
| RBAC-AC-002 | Credit Manager cannot authorise disbursement. |
| RBAC-AC-003 | CFC cannot edit appraisal notes. |
| RBAC-AC-004 | Auditor cannot modify operational data. |
| RBAC-AC-005 | Director can view only assigned approval cases. |
| RBAC-AC-006 | Sensitive reveal requires explicit permission and reason. |
| RBAC-AC-007 | Role changes are audit logged. |

---

## 11.3 Member and Borrower Master

### Requirements

1. The system must store individual farmer member profiles.
2. The system must store Producer Institution / FPC profiles.
3. The system must support member folio number and shareholding details.
4. The system must support member status: active, inactive, suspended, etc.
5. The system must support PAN and Aadhaar storage with encryption and masked display.
6. The system must support contact details and address.
7. The system must support member search by safe fields and hashed identifiers where needed.
8. The system must track existing loan/default status.
9. The system must support subsidiaries/producer institution relationships where repayment deductions are made.
10. The system must show a Borrower 360 / Member 360 view.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| MEM-AC-001 | Individual farmer member can be created and viewed. |
| MEM-AC-002 | FPC / Producer Institution member can be created and viewed. |
| MEM-AC-003 | PAN and Aadhaar are masked by default. |
| MEM-AC-004 | Duplicate PAN can be detected using secure hash. |
| MEM-AC-005 | Member profile shows KYC, shares, land, crop, loans and defaults. |
| MEM-AC-006 | Non-member cannot proceed to loan application. |

---

## 11.4 Nominee and Witness

### Requirements

1. The system must capture nominee name, age/date of birth, Aadhaar, PAN, gender and contact details.
2. The system must block minor nominees.
3. The system must link nominee to borrower/application.
4. The system must capture witness KYC details for legal documents.
5. The system must verify witness is an existing SFPCL shareholder.
6. The system must block checklist completion if witness requirements are not met.
7. Witness and nominee KYC must be subject to sensitive data masking and access control.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| NOM-AC-001 | Adult nominee can be added. |
| NOM-AC-002 | Minor nominee is blocked. |
| NOM-AC-003 | Witness must be existing shareholder. |
| NOM-AC-004 | Witness KYC documents can be uploaded. |
| NOM-AC-005 | Missing witness blocks relevant legal documents. |

---

## 11.5 KYC and Re-KYC

### Requirements

1. The system must support KYC profiles for borrowers, nominees, witnesses and FPC authorised signatories.
2. The system must track PAN, Aadhaar/OVD, CKYC consent and KYC verification.
3. The system must allow upload of KYC documents.
4. The system must mark KYC as pending, verified, rejected or expired.
5. The system must track beneficial ownership where applicable for FPCs.
6. The system must calculate re-KYC due date, assumed every two years unless configured otherwise.
7. The system must create re-KYC compliance tasks.
8. The system must restrict KYC document download.
9. KYC verification actions must be audit logged.
10. KYC records must be retained according to retention policy.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| KYC-AC-001 | KYC documents can be uploaded and verified. |
| KYC-AC-002 | KYC cannot be marked verified if required fields are missing. |
| KYC-AC-003 | KYC download is restricted and audited. |
| KYC-AC-004 | Re-KYC due tasks are generated. |
| KYC-AC-005 | FPC beneficial ownership fields are required where configured. |

---

## 11.6 Shareholding, Landholding and Crop Plan

### Requirements

1. The system must store number of shares held.
2. The system must store folio number and share certificate details.
3. The system must support physical shares and demat shares.
4. The system must store demat BO account details securely where required.
5. The system must store share valuation configuration and historical versions.
6. The system must store landholding details, including 7/12 extract evidence.
7. The system must store crop plan details.
8. Land area under cultivation must be available for scale-of-finance calculation.
9. Shareholding and landholding records used in a loan limit assessment must be snapshotted.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| SH-AC-001 | Physical shareholding can be recorded. |
| SH-AC-002 | Demat shareholding can be recorded. |
| SH-AC-003 | Share certificate evidence can be uploaded. |
| LAND-AC-001 | Land 7/12 extract can be uploaded. |
| LAND-AC-002 | Crop plan can be stored. |
| LAND-AC-003 | Land area supports loan limit calculation. |

---

## 11.7 Loan Application Intake

### Requirements

1. The system must support creation of a draft loan application.
2. The system must assign a unique application reference number using the configured sequence format.
3. The system must capture required loan amount, purpose, borrower details, shareholding details and nominee details.
4. The system must support application submission.
5. The system must track application source/channel.
6. The system must support application acknowledgement.
7. The system must show application status and stage.
8. The system must prevent duplicate reference numbers.
9. The system must maintain application status history.
10. The system must support cancellation of drafts, but not disbursed applications.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| APP-AC-001 | Draft application can be created. |
| APP-AC-002 | Application reference is unique. |
| APP-AC-003 | Submitted application is visible in completeness queue. |
| APP-AC-004 | Application cannot be submitted with missing mandatory fields. |
| APP-AC-005 | Application acknowledgement is generated/logged. |

---

## 11.8 Application Completeness and Deficiencies

### Requirements

1. The system must define required documents for application stage.
2. Deputy Manager / authorised user must verify completeness.
3. Incomplete applications must be returned with a deficiency list.
4. Deficiency list must be communicated to borrower or internal owner.
5. Deficiencies must be individually resolvable.
6. Application cannot move to appraisal until deficiencies are resolved.
7. Deficiency history must remain visible.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| DEF-AC-001 | Missing required documents are flagged. |
| DEF-AC-002 | Incomplete application returns to deficiency status. |
| DEF-AC-003 | Deficiency communication is created. |
| DEF-AC-004 | Resolved deficiencies allow resubmission. |
| DEF-AC-005 | Appraisal is blocked while deficiency is open. |

---

## 11.9 Eligibility Assessment

### Requirements

1. The system must run eligibility assessment after application completeness.
2. Eligibility must check that applicant is a member.
3. Eligibility must check active member status.
4. Eligibility must check that borrower is not in default for SFPCL/subsidiary/associate loans.
5. Eligibility must check required land documents, KYC, bank statement and crop plan.
6. Eligibility must check that purpose relates to crop production/agriculture activity.
7. Eligibility must check agreement to Term Sheet and Loan Agreement where applicable.
8. Eligibility must produce pass/fail result per criterion.
9. Eligibility override, if allowed, must require permission, reason and audit.
10. Failed eligibility may lead to rejection note.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| ELIG-AC-001 | Eligible borrower passes all checks. |
| ELIG-AC-002 | Inactive member fails eligibility. |
| ELIG-AC-003 | Existing default fails eligibility. |
| ELIG-AC-004 | Missing crop plan fails or blocks eligibility. |
| ELIG-AC-005 | Non-agriculture purpose fails eligibility. |
| ELIG-AC-006 | Eligibility result is stored with explanation. |

---

## 11.10 Active Member Assessment

### Requirements

1. The system must support individual active member assessment.
2. Individual active member requires use of company services and primary produce supply continuously for four financial years, as described in SOP.
3. The system must support individual relaxation:
   - at least one year supply; or
   - services/employment/other capacity for continuous three years.
4. The system must support FPC/Producer Institution active member assessment.
5. FPC active member requires service use and produce supply continuously for four financial years.
6. FPC relaxation requires at least one year produce supply.
7. Active member status must be calculated as of the relevant financial year.
8. Manual verification or override must require reason and audit.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| ACTIVE-AC-001 | Individual with four-year supply is active. |
| ACTIVE-AC-002 | Individual under one-year supply relaxation is active. |
| ACTIVE-AC-003 | Individual under three-year service route is active. |
| ACTIVE-AC-004 | FPC with four-year supply is active. |
| ACTIVE-AC-005 | Inactive member is blocked from eligibility. |
| ACTIVE-AC-006 | Active member result is stored with explanation. |

---

## 11.11 Loan Limit Calculator

### Requirements

1. The system must calculate shareholding-based loan limit.
2. The system must calculate agricultural land-based / scale-of-finance loan limit.
3. The final eligible amount must be the lower of shareholding-based and land-based limits.
4. Shareholding-based limit must use configured policy rule:
   - formula may be valuation percentage; or
   - configured current cap such as ₹200/share.
5. The system must expose unresolved policy ambiguity until final decision is configured.
6. Land-based limit must use per-acre scale of finance, currently ₹20,000 per acre unless configured otherwise.
7. Calculation must snapshot:
   - share count;
   - share valuation;
   - share limit rule;
   - land area;
   - scale of finance;
   - final eligible amount;
   - requested amount;
   - exception flag.
8. Requested amount above eligible limit must require exception approval.
9. Historical calculations must not change when configuration changes later.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| LIMIT-AC-001 | Shareholding-based limit is calculated correctly. |
| LIMIT-AC-002 | Land-based limit is calculated correctly. |
| LIMIT-AC-003 | Final eligible amount is lower of both limits. |
| LIMIT-AC-004 | Requested amount above limit flags exception. |
| LIMIT-AC-005 | Calculation stores policy snapshot. |
| LIMIT-AC-006 | Existing calculation does not change after policy update. |
| LIMIT-AC-007 | Missing policy config blocks calculation. |

---

## 11.12 Appraisal and Credit Review

### Requirements

1. Deputy Manager – Finance must prepare Loan Appraisal Note.
2. Appraisal must include borrower details, loan details, eligibility, loan limit, repayment capacity, risk assessment and recommendation.
3. Credit Manager must review the appraisal before sanction submission.
4. Credit Manager may return appraisal for correction.
5. Credit Manager may reject application and generate Rejection Note.
6. Appraisal stage should track 2-day TAT from receipt.
7. Appraisal versions must be locked after sanction submission unless reopened with audit.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| APPRAISAL-AC-001 | Deputy Manager can prepare appraisal. |
| APPRAISAL-AC-002 | Appraisal cannot proceed before eligibility. |
| APPRAISAL-AC-003 | Credit Manager review is required. |
| APPRAISAL-AC-004 | Sanction submission is blocked without review. |
| APPRAISAL-AC-005 | Rejection Note can be generated and sent. |
| APPRAISAL-AC-006 | TAT due/overdue is visible. |

---

## 11.13 Sanction Approval

### Requirements

1. The system must create an Approval Case after Credit Manager submission.
2. Approval matrix must be configurable and versioned.
3. For loan sanction up to ₹5,00,000 per member, required approval is CFO + one Director.
4. For loan sanction above ₹5,00,000 per member, required approval is CFO + two Directors.
5. For loan exceeding maximum permissible limit, required approval is CFO + two Directors and Exception Register reason.
6. Approvers must be assigned to approval case.
7. Approval actions must be immutable.
8. Rejections must require reason.
9. Return for clarification must require reason.
10. Sanction decision must be created after all required approvals.
11. Credit Sanction Register must be generated from sanction decisions.
12. Exception Register must be generated from exception approvals.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| SANCTION-AC-001 | Below/at ₹5 lakh requires CFO + one Director. |
| SANCTION-AC-002 | Above ₹5 lakh requires CFO + two Directors. |
| SANCTION-AC-003 | Approval is incomplete until all required approvers act. |
| SANCTION-AC-004 | Rejection blocks documentation. |
| SANCTION-AC-005 | Exception reason is required when amount exceeds limit. |
| SANCTION-AC-006 | Approval actions are immutable and audited. |

---

## 11.14 Conflict and Related-Party Approval

### Requirements

1. The system must identify borrower as Sanction Committee member, Director or relative where data is available.
2. Conflicted approver must be excluded from approval.
3. Related-party/special cases must require general meeting approval evidence under the SOP.
4. Attempted conflicted approval must be blocked.
5. General meeting approval evidence must be attached before sanction finalisation where required.
6. Conflict status must appear on approval case and audit logs.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| CONFLICT-AC-001 | Director borrower is flagged as conflicted. |
| CONFLICT-AC-002 | Conflicted Director cannot approve own/relative case. |
| CONFLICT-AC-003 | General meeting evidence is required. |
| CONFLICT-AC-004 | Remaining approvers can complete approval. |
| CONFLICT-AC-005 | Conflict decision is audit logged. |

---

## 11.15 Legal Documentation

### Requirements

1. Documentation stage starts after sanction approval.
2. The system must support generation/upload of required legal documents.
3. Required documents include:
   - Loan Application Form;
   - Loan Appraisal Note;
   - Power of Attorney;
   - Declaration / Tri-party Agreement;
   - SH-4 where applicable;
   - Term Sheet;
   - Loan Agreement;
   - Bank Verification Letter where required;
   - Document Checklist;
   - Rejection Note;
   - Extension Note;
   - Non-Payment Note;
   - NOC;
   - Disbursement Advice;
   - Interest Invoice.
4. Generated documents must store template version.
5. Regeneration must require reason.
6. Executed documents must not be overwritten silently.
7. Document access must be restricted by sensitivity.
8. Documents must be linked to application/loan/security/compliance entities.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| DOC-AC-001 | Legal documents can be generated from approved templates. |
| DOC-AC-002 | Document template version is stored. |
| DOC-AC-003 | Signed/executed document upload is supported. |
| DOC-AC-004 | Regeneration requires reason. |
| DOC-AC-005 | Restricted documents require permission to download. |

---

## 11.16 Stamp Duty, Notarisation and Signatures

### Requirements

1. The system must record stamp duty details for documents where required.
2. The system must record notarisation details where required.
3. PoA and Loan Agreement must track execution on required stamp paper and notarisation according to configured rules.
4. Signature records must be captured for borrower, nominee, witness and internal signers where applicable.
5. Signature mismatch must be flaggable.
6. Signature mismatch must be resolved by:
   - Bank Verification Letter; or
   - borrower declaration on stamp paper, if accepted.
7. Unresolved signature mismatch blocks final checklist.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| SIGN-AC-001 | Stamp duty record can be added. |
| SIGN-AC-002 | Notarisation record can be added. |
| SIGN-AC-003 | Signature mismatch blocks checklist. |
| SIGN-AC-004 | Bank Verification Letter resolves mismatch. |
| SIGN-AC-005 | Missing stamp/notary blocks required document. |

---

## 11.17 Document Checklist

### Requirements

1. The system must generate required checklist items based on borrower type, loan type, security mode and policy configuration.
2. Checklist must track required, optional, not-applicable and completed items.
3. Checklist approvals must support sequence:
   - Company Secretary verifies all required docs attached;
   - Credit Manager confirms disbursement limits reviewed;
   - Sanction Committee signs final approval for disbursement;
   - Senior Manager Finance signs after actual disbursement.
4. Checklist must expose blocker reasons.
5. Disbursement readiness must consume checklist status.
6. Checklist approvals must be audit logged.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| CHECKLIST-AC-001 | Checklist generates required items. |
| CHECKLIST-AC-002 | Missing required item blocks approval. |
| CHECKLIST-AC-003 | CS approval requires all legal docs complete. |
| CHECKLIST-AC-004 | Credit Manager approval follows configured sequence. |
| CHECKLIST-AC-005 | Final checklist approval makes file eligible for disbursement readiness. |
| CHECKLIST-AC-006 | Senior Manager signature is recorded after disbursement. |

---

## 11.18 Security Package

### Requirements

1. The system must create a security package after sanction.
2. The security package must include PoA.
3. Physical shares must require SH-4.
4. Demat shares must require CDSL pledge tracking.
5. Blank-dated cheque must be collected and custody tracked.
6. Cancelled cheque must be collected for bank verification.
7. Witness must be verified as SFPCL shareholder.
8. Security package readiness must be consumed by disbursement readiness.
9. Security custody movements must be recorded.
10. Security instruments must be released/returned/unpledged after closure.
11. Security invocation must be blocked unless recovery approval exists.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| SEC-PKG-AC-001 | Physical share loan requires SH-4. |
| SEC-PKG-AC-002 | Demat share loan requires CDSL pledge. |
| SEC-PKG-AC-003 | Blank-dated cheque custody is restricted. |
| SEC-PKG-AC-004 | Cancelled cheque is required for disbursement readiness. |
| SEC-PKG-AC-005 | Security package incomplete blocks disbursement. |
| SEC-PKG-AC-006 | Security invocation requires approved recovery decision. |

---

## 11.19 CDSL Pledge

### Requirements

1. The system must track CDSL pledge for demat shares.
2. It must record PRF submission.
3. It must record PSN.
4. It must record pledgee acceptance/rejection.
5. It must mark pledge as created only after acceptance.
6. Disbursement must be blocked until pledge is created.
7. Invocation must require recovery approval.
8. Unpledge must be tracked after closure.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| CDSL-AC-001 | PRF submission can be recorded. |
| CDSL-AC-002 | PSN can be recorded. |
| CDSL-AC-003 | Pledge acceptance marks security complete. |
| CDSL-AC-004 | Rejected pledge blocks disbursement. |
| CDSL-AC-005 | Unpledge can be recorded after closure. |

---

## 11.20 SAP Customer Code Workflow

### Requirements

1. SAP customer code request must be created after sanction approval.
2. If borrower already has existing SAP customer code due to outstanding loan, code must be reused.
3. Credit Manager must be able to request SAP profile creation.
4. Request must include required borrower details.
5. System must support Excel generation for manual SAP creation.
6. Senior Manager Finance must confirm SAP customer code creation.
7. SAP code must be unique.
8. Disbursement readiness must fail if SAP code is missing.
9. SAP request and confirmation must be audit logged.
10. System must be API-ready for future direct SAP integration.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| SAP-AC-001 | SAP request can be created after sanction. |
| SAP-AC-002 | SAP request cannot be created before sanction. |
| SAP-AC-003 | SAP Excel is generated. |
| SAP-AC-004 | SAP customer code can be confirmed. |
| SAP-AC-005 | Duplicate SAP code is blocked. |
| SAP-AC-006 | Existing SAP code is reused. |
| SAP-AC-007 | Missing SAP code blocks disbursement. |

---

## 11.21 Loan Account Creation

### Requirements

1. Loan account must be created from approved sanction.
2. Loan account must snapshot sanctioned amount, tenure, interest terms, borrower and policy configuration.
3. Loan account number must be unique.
4. Loan account initially remains pending/disbursement-ready until transfer success.
5. Loan account becomes active after successful disbursement.
6. Loan account must show status history.
7. Loan Account 360 must show application, documents, security, disbursement, repayment, interest, default and closure tabs.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| LOAN-AC-001 | Loan account can be created after sanction. |
| LOAN-AC-002 | Duplicate loan account for same sanctioned application is blocked. |
| LOAN-AC-003 | Loan account captures sanction snapshot. |
| LOAN-AC-004 | Loan account becomes active after successful disbursement. |
| LOAN-AC-005 | Loan Account 360 shows lifecycle data. |

---

## 11.22 Disbursement Readiness and Payment

### Requirements

1. The system must evaluate disbursement readiness.
2. Readiness must check sanction, documentation, checklist, security package, SAP code, bank verification, signatures, amount and required approvals.
3. Readiness must return pass/fail per check with reasons.
4. Only Senior Manager Finance can initiate payment.
5. Only CFC can authorise payment.
6. Payment success requires UTR/reference and bank evidence.
7. Duplicate UTR must be blocked.
8. Loan becomes active only after successful transfer.
9. Disbursement advice must be generated/sent after transfer.
10. Initiation and success must be idempotent.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| DISB-AC-001 | Readiness returns all checks and blockers. |
| DISB-AC-002 | Disbursement cannot initiate if readiness fails. |
| DISB-AC-003 | Senior Manager Finance can initiate ready disbursement. |
| DISB-AC-004 | CFC authorisation is required. |
| DISB-AC-005 | UTR is required for success. |
| DISB-AC-006 | Duplicate UTR is blocked. |
| DISB-AC-007 | Successful disbursement activates loan. |
| DISB-AC-008 | Disbursement advice is generated. |

---

## 11.23 Repayment

### Requirements

1. The system must support direct repayment via RTGS/NEFT.
2. The system must support repayment through subsidiary deduction.
3. Repayment must capture amount, date, source, bank reference and evidence.
4. Subsidiary repayment must capture subsidiary, produce/payment reference and transfer reference.
5. Duplicate bank/subsidiary references must be blocked.
6. Partial repayment must be allocated first against principal.
7. SAP posting reference must be captured.
8. Repayment allocation must update outstanding.
9. Reconciliation exceptions must be visible.
10. Repayment audit logs must be created.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| REPAY-AC-001 | Direct repayment can be captured. |
| REPAY-AC-002 | Subsidiary repayment can be captured. |
| REPAY-AC-003 | Duplicate repayment reference is blocked. |
| REPAY-AC-004 | Partial repayment reduces principal first. |
| REPAY-AC-005 | SAP posting reference can be recorded. |
| REPAY-AC-006 | Outstanding amount updates correctly. |

---

## 11.24 Interest, Accrual and Capitalisation

### Requirements

1. The system must support floating interest rates using configured rate snapshots.
2. The system must generate annual interest invoices.
3. The system must support monthly interest accrual entries.
4. Duplicate accrual for same loan/month must be blocked.
5. If interest is unpaid up to 30 April of next financial year, unpaid interest must be eligible for capitalisation.
6. Capitalisation must increase principal by unpaid interest.
7. Duplicate capitalisation for same loan/financial year must be blocked.
8. Borrower must be informed by email/hard-copy letter after capitalisation.
9. Historical interest calculations must remain tied to rate snapshots.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| INT-AC-001 | Interest invoice can be generated. |
| INT-AC-002 | Monthly accrual can be generated. |
| INT-AC-003 | Duplicate monthly accrual is blocked. |
| INT-AC-004 | Capitalisation before 30 April is blocked. |
| INT-AC-005 | Capitalisation after 30 April increases principal. |
| INT-AC-006 | Duplicate capitalisation is blocked. |
| INT-AC-007 | Borrower intimation is created. |

---

## 11.25 Monitoring, DPD and MIS

### Requirements

1. The system must calculate DPD and bucket loans.
2. SOP buckets must include:
   - 1 year to 2 years;
   - 2 years to 3 years;
   - more than 3 years.
3. Operational buckets may be added for better monitoring.
4. Credit Manager must be able to view DPD dashboard.
5. System must support quarterly MIS generation for CFO.
6. System must support SMS/phone/email reminder logging.
7. Loans outstanding beyond 1 year at quarter-end should trigger reminder workflow.
8. Monitoring actions must be audit logged where material.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| MON-AC-001 | DPD is calculated correctly. |
| MON-AC-002 | SOP buckets are displayed. |
| MON-AC-003 | Quarterly MIS can be generated. |
| MON-AC-004 | Reminder queue is generated. |
| MON-AC-005 | Reminder communication is logged. |

---

## 11.26 Default and Extension

### Requirements

1. Missed principal repayment must open a default case or mark loan for review.
2. Company provides further tenure of 3 months from due date.
3. If unpaid after 3 months, Credit Assessment Team records reason and intentional/non-intentional classification.
4. Non-intentional default can receive one-year extension.
5. Extension Note must be generated and stored.
6. If unpaid after extension, loan is considered for scrutiny and Non-Payment Note.
7. Default stage changes must be audit logged.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| DEFAULT-AC-001 | Missed repayment opens default case. |
| DEFAULT-AC-002 | Grace period end date is due date + 3 months. |
| DEFAULT-AC-003 | Non-intentional classification allows extension. |
| DEFAULT-AC-004 | Extension Note is generated. |
| DEFAULT-AC-005 | Extension expiry triggers Non-Payment Note requirement. |

---

## 11.27 Recovery

### Requirements

1. Non-Payment Note must be prepared after required default/extension process.
2. Non-Payment Note must be submitted to Sanction Committee / configured authority.
3. Recovery decision must specify action:
   - sale/invocation of shares;
   - SH-4 execution;
   - CDSL invocation;
   - blank-dated cheque presentation;
   - other legal recovery action if configured.
4. Recovery action cannot start without approved recovery decision.
5. Company Secretary or authorised role must execute security instrument action.
6. Recovery evidence must be uploaded.
7. Recovery conduct must be logged to avoid coercive/uncontrolled action.
8. Grievances linked to recovery must be trackable.
9. Recovery procedure remains an open policy area where SOP is incomplete; system must support configurable approval route.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| REC-AC-001 | Recovery action is blocked without approval. |
| REC-AC-002 | Non-Payment Note can be generated. |
| REC-AC-003 | Recovery approval case can be created. |
| REC-AC-004 | Approved recovery action can invoke relevant security instrument. |
| REC-AC-005 | Recovery evidence is required. |
| REC-AC-006 | Recovery action is audit logged. |

---

## 11.28 Closure, NOC, Security Return and Archive

### Requirements

1. Loan closure requires full repayment of principal, interest and charges.
2. Closure readiness must show blockers.
3. NOC must be generated after closure.
4. SH-4 and blank-dated cheque must be returned to borrower after closure where applicable.
5. CDSL unpledge must be recorded for demat share security.
6. Security return acknowledgement must be stored.
7. Archive record must include physical/digital location.
8. Retention date must be at least 8 years after closure.
9. Closed loan records should be read-only except controlled archive/security actions.
10. Closure actions must be audit logged.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| CLOSE-AC-001 | Loan cannot close with outstanding amount. |
| CLOSE-AC-002 | Loan can close when outstanding is zero. |
| CLOSE-AC-003 | NOC can be generated after closure. |
| CLOSE-AC-004 | SH-4/blank cheque return can be recorded. |
| CLOSE-AC-005 | CDSL unpledge can be recorded. |
| CLOSE-AC-006 | Archive retention date is calculated. |

---

## 11.29 Compliance

### Requirements

1. The system must include a Compliance Dashboard.
2. The system must track Producer Company member-only lending controls.
3. The system must maintain Loan Register and policy evidence.
4. The system must include Section 186 tracker.
5. Section 186 tracker must calculate:
   - 60% of paid-up capital + free reserves + securities premium;
   - 100% of free reserves + securities premium;
   - higher of the two;
   - current exposure;
   - special resolution requirement if exceeded.
6. The system must include NBFC Principal Business Test:
   - financial assets >50% of total assets;
   - financial income >50% of gross income;
   - trigger if both exceed threshold.
7. The system must track KYC/re-KYC.
8. The system must track stamp duty evidence.
9. The system must track annual money-lending law review.
10. The system must track recovery conduct and grievances.
11. The system must track record retention and archive.
12. Compliance tasks must have owner, due date, evidence, reviewer, status and audit.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| COMP-AC-001 | Compliance tasks can be generated by frequency. |
| COMP-AC-002 | Section 186 tracker calculates limit correctly. |
| COMP-AC-003 | NBFC test calculates trigger correctly. |
| COMP-AC-004 | KYC/re-KYC overdue records are visible. |
| COMP-AC-005 | Stamp duty register is filterable/exportable. |
| COMP-AC-006 | Money-lending law review task can store legal opinion. |
| COMP-AC-007 | Compliance evidence review is audit logged. |

---

## 11.30 Communications

### Requirements

1. The system must support email, SMS and internal task notifications.
2. Templates must be configurable and versioned.
3. Communications must be linked to application, loan, default, closure or compliance entity.
4. Sensitive values must be blocked from SMS and broad communications.
5. Communication status must be tracked.
6. Failed communications must support retry.
7. Required communications include:
   - application acknowledgement;
   - deficiency notice;
   - rejection note;
   - approval/sanction notification;
   - disbursement advice;
   - interest invoice;
   - interest capitalisation notice;
   - repayment reminder;
   - default/grace/extension communication;
   - NOC;
   - grievance updates.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| COMM-AC-001 | Template-based email can be generated. |
| COMM-AC-002 | SMS template blocks sensitive data. |
| COMM-AC-003 | Failed communication can be retried. |
| COMM-AC-004 | Communication history is visible on loan/application. |
| COMM-AC-005 | Delivery status is recorded where available. |

---

## 11.31 Reports and Exports

### Requirements

1. The system must provide Reports and MIS Centre.
2. Reports must be generated from system data, not manual duplicate registers.
3. Reports must support filters, sorting and export.
4. Export must require permission.
5. Sensitive fields must be masked by default.
6. Sensitive export must require special permission and reason.
7. Export downloads must expire.
8. Export actions must be audit logged.

### Required Reports

| Report | Priority |
|---|---|
| Loan Request Register | High |
| Credit Sanction Register | High |
| Exception Register | High |
| Documentation Readiness Report | High |
| Security Custody Register | High |
| SAP Pending Report | High |
| Disbursement Report | High |
| Loan Register | High |
| Repayment Report | High |
| Interest Invoice Report | High |
| Interest Accrual Report | Medium |
| DPD Report | High |
| Quarterly MIS to CFO | High |
| Default Report | High |
| Recovery Report | High |
| Closure/NOC Report | High |
| Section 186 Report | High |
| NBFC Test Report | High |
| KYC/Re-KYC Report | High |
| Stamp Duty Register | High |
| Money-Lending Review Report | Medium |
| Grievance Report | Medium |
| Audit Log Export | Restricted |

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| REPORT-AC-001 | Report list is role-based. |
| REPORT-AC-002 | Exports require permission. |
| REPORT-AC-003 | Sensitive fields are masked by default. |
| REPORT-AC-004 | Export action is audit logged. |
| REPORT-AC-005 | Registers match source system records. |

---

## 11.32 Audit

### Requirements

1. Audit logs must be append-only.
2. Critical actions must generate audit logs.
3. Audit logs must include actor, role/team snapshot, action, entity, timestamp, outcome, request ID and reason where required.
4. Audit logs must redact sensitive values.
5. Audit Explorer must be available to authorised roles.
6. Workflow events must show lifecycle timeline.
7. Audit logs cannot be edited through UI.

### Critical Audit Events

- Login/logout/failure.
- User/role/permission change.
- Sensitive reveal.
- Restricted document download.
- Application submission.
- Completeness decision.
- Eligibility assessment.
- Loan limit calculation.
- Appraisal review.
- Approval action.
- Sanction decision.
- Exception approval.
- Document verification.
- Checklist approval.
- Security custody movement.
- SAP request/completion.
- Disbursement initiation/authorisation/success.
- Repayment capture/allocation.
- Interest invoice/accrual/capitalisation.
- Default opening.
- Extension.
- Recovery approval/action.
- Closure.
- NOC generation.
- Security return.
- Archive.
- Compliance evidence submission/review.
- Config changes.
- Export downloads.

### Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| AUDIT-AC-001 | Critical actions create audit log. |
| AUDIT-AC-002 | Audit logs cannot be edited through UI. |
| AUDIT-AC-003 | Audit logs redact sensitive values. |
| AUDIT-AC-004 | Audit Explorer supports filtering. |
| AUDIT-AC-005 | Workflow timeline shows key lifecycle events. |

---

# 12. Non-Functional Requirements

## 12.1 Security and Privacy

| Requirement | Description |
|---|---|
| NFR-SEC-001 | All protected APIs require JWT authentication. |
| NFR-SEC-002 | Backend enforces RBAC and object access. |
| NFR-SEC-003 | PAN, Aadhaar, bank account, cheque and BO account must be encrypted/masked. |
| NFR-SEC-004 | Sensitive reveal requires permission, reason and audit. |
| NFR-SEC-005 | Restricted document download requires permission and audit. |
| NFR-SEC-006 | Exports mask sensitive values by default. |
| NFR-SEC-007 | Secrets must not be stored in code. |
| NFR-SEC-008 | Production must use HTTPS and secure settings. |
| NFR-SEC-009 | Logs must not contain raw sensitive values. |
| NFR-SEC-010 | Privileged roles should support MFA. |

## 12.2 Performance

| Requirement | Target |
|---|---|
| NFR-PERF-001 | Login under 2 seconds. |
| NFR-PERF-002 | Dashboard under 3 seconds. |
| NFR-PERF-003 | Member search under 2–4 seconds for expected volume. |
| NFR-PERF-004 | Application detail under 3 seconds. |
| NFR-PERF-005 | Disbursement readiness under 3 seconds. |
| NFR-PERF-006 | Large exports run asynchronously. |
| NFR-PERF-007 | Scheduled jobs complete in agreed business windows. |

## 12.3 Availability and Operations

| Requirement | Description |
|---|---|
| NFR-OPS-001 | Health and readiness endpoints must exist. |
| NFR-OPS-002 | Celery worker and scheduler health must be monitored. |
| NFR-OPS-003 | Database backups must run automatically. |
| NFR-OPS-004 | Object storage must be backed up/replicated. |
| NFR-OPS-005 | Restore process must be tested. |
| NFR-OPS-006 | Production alerts must cover API, DB, workers, storage and backup failures. |
| NFR-OPS-007 | Deployment rollback must be possible. |

## 12.4 Accessibility and Usability

| Requirement | Description |
|---|---|
| NFR-UX-001 | Forms must have labels, help text and validation messages. |
| NFR-UX-002 | Status must not be conveyed by colour alone. |
| NFR-UX-003 | Key workflows must be keyboard accessible. |
| NFR-UX-004 | Error messages must explain the next corrective action. |
| NFR-UX-005 | Long workflows must show stage and blockers. |
| NFR-UX-006 | Dashboards must be role-specific. |

## 12.5 Audit and Retention

| Requirement | Description |
|---|---|
| NFR-AUD-001 | Critical actions must be audit logged. |
| NFR-AUD-002 | Loan files must be retained at least 8 years after closure. |
| NFR-AUD-003 | Historical calculations and approvals must be immutable. |
| NFR-AUD-004 | Config changes must be versioned and effective-dated. |
| NFR-AUD-005 | Audit logs must be retained according to compliance policy. |

---

# 13. User Stories

The following stories are intentionally detailed and extensive so this PRD can be converted into issue slices.

## 13.1 Authentication, Access and Administration

1. As an internal user, I want to log in securely, so that I can access only the platform functions assigned to me.
2. As an internal user, I want my session to refresh securely, so that I can continue work without repeatedly logging in.
3. As an internal user, I want to log out, so that my session cannot be reused.
4. As an inactive user, I should be prevented from logging in, so that former or suspended staff cannot access borrower data.
5. As an administrator, I want to create user accounts, so that new employees can access the platform.
6. As an administrator, I want to assign roles and teams, so that users receive correct access.
7. As an administrator, I want to remove or suspend access, so that exits and role changes are controlled.
8. As an IT Head, I want to review active users periodically, so that unnecessary access is removed.
9. As a system administrator, I want role changes audit logged, so that access governance is traceable.
10. As a privileged user, I want stronger authentication where required, so that high-risk actions are protected.
11. As a user, I want the navigation menu to show only relevant modules, so that I am not confused by unauthorised features.
12. As a user, I want unavailable actions to show blocker reasons, so that I know what must be completed next.
13. As an auditor, I want read-only access, so that I can inspect evidence without altering records.
14. As a management viewer, I want dashboards without edit permissions, so that I can monitor performance safely.

## 13.2 Member and Borrower Master

15. As a Credit user, I want to create an individual farmer member profile, so that the borrower can apply for a member loan.
16. As a Credit user, I want to create an FPC / Producer Institution profile, so that institutional members can apply for loans.
17. As a Credit user, I want to search members by safe identifiers, so that I can avoid duplicate applications.
18. As a Credit user, I want PAN/Aadhaar duplicate detection, so that duplicate borrower records are prevented.
19. As a Compliance user, I want PAN/Aadhaar masked by default, so that sensitive data is protected.
20. As an authorised user, I want to reveal sensitive fields with reason, so that I can complete necessary verification.
21. As an auditor, I want sensitive reveal actions logged, so that privacy access can be reviewed.
22. As a Credit Manager, I want to see a Borrower 360 view, so that I can understand the member’s KYC, shares, land, loans and defaults.
23. As a Credit user, I want to store shareholding details, so that loan limits and security can be assessed.
24. As a Credit user, I want to store whether shares are physical or demat, so that the right security workflow is triggered.
25. As a Credit user, I want to store landholding and crop plan details, so that land-based eligibility can be calculated.
26. As a Credit user, I want to attach 7/12 extracts and crop plans, so that the application has required evidence.

## 13.3 Nominee, Witness and KYC

27. As a Credit user, I want to add a nominee, so that the loan application and legal documents are complete.
28. As a Credit user, I want the system to block minor nominees, so that SOP requirements are enforced.
29. As a Compliance user, I want to add a witness, so that legal documents can be executed.
30. As a Compliance user, I want the system to verify that the witness is an existing SFPCL shareholder, so that witness rules are enforced.
31. As a Compliance user, I want to upload borrower KYC documents, so that KYC can be verified.
32. As a Compliance user, I want to upload nominee KYC documents, so that nominee requirements are complete.
33. As a Compliance user, I want to upload witness KYC documents, so that legal document execution is supported.
34. As a KYC reviewer, I want to verify or reject KYC documents, so that incomplete records do not proceed.
35. As a Compliance user, I want CKYC consent tracked, so that regulatory evidence is available.
36. As a Compliance user, I want re-KYC due dates, so that periodic KYC updates are not missed.
37. As a Compliance manager, I want overdue re-KYC tasks, so that follow-up can be planned.

## 13.4 Application Intake and Completeness

38. As a Credit user, I want to create a draft loan application, so that borrower requests can be captured.
39. As a Credit user, I want the system to assign a unique loan application reference, so that the application can be tracked.
40. As a Credit user, I want to capture required loan amount and purpose, so that credit assessment can start.
41. As a Credit user, I want to upload application documents, so that the file is complete.
42. As a Deputy Manager – Finance, I want a completeness checklist, so that I can verify the application.
43. As a Deputy Manager – Finance, I want to return incomplete applications with deficiencies, so that missing information is clearly communicated.
44. As a Credit user, I want to resolve deficiencies, so that the application can be resubmitted.
45. As a Credit Manager, I want to see incomplete applications by age, so that follow-up can be prioritised.
46. As a borrower-facing communication owner, I want deficiency notices generated, so that borrowers know what is missing.
47. As an auditor, I want deficiency history retained, so that application handling is traceable.
48. As a Credit Manager, I want to reject an application with a reason, so that failed applications are formally closed.
49. As a Credit Manager, I want to generate a Rejection Note, so that borrower communication is standardised.

## 13.5 Eligibility and Loan Limit

50. As a Deputy Manager – Finance, I want to run eligibility assessment, so that only qualified members proceed.
51. As a Deputy Manager – Finance, I want active member status calculated, so that membership criteria are enforced.
52. As a Deputy Manager – Finance, I want default status checked, so that defaulting borrowers are not given new loans.
53. As a Deputy Manager – Finance, I want required documents checked, so that incomplete files do not proceed.
54. As a Deputy Manager – Finance, I want loan purpose checked, so that loans are for crop production/agricultural activity.
55. As a Credit Manager, I want eligibility failure reasons, so that I can reject or request correction.
56. As an authorised approver, I want overrides to require reason and audit, so that exceptions are controlled.
57. As a Deputy Manager – Finance, I want shareholding-based loan limit calculated, so that member share value is considered.
58. As a Deputy Manager – Finance, I want land-based loan limit calculated, so that cultivation area and scale of finance are considered.
59. As a Deputy Manager – Finance, I want final eligible amount to be the lower of share and land limits, so that SOP rules are enforced.
60. As a Credit Manager, I want requested amount above eligible limit flagged, so that exception approval is required.
61. As a CFO, I want loan limit calculations to show policy version, so that approval decisions are auditable.
62. As an auditor, I want historical loan limit snapshots, so that later policy changes do not alter past decisions.

## 13.6 Appraisal and Credit Review

63. As a Deputy Manager – Finance, I want to prepare a Loan Appraisal Note, so that credit assessment is documented.
64. As a Deputy Manager – Finance, I want appraisal to include repayment capacity, risk rating and recommendation, so that Sanction Committee has complete context.
65. As a Credit Manager, I want to review appraisal notes, so that maker-checker control is enforced.
66. As a Credit Manager, I want to return appraisal for correction, so that incomplete assessments are fixed.
67. As a Credit Manager, I want to submit reviewed appraisals to Sanction Committee, so that approval can begin.
68. As a Credit Manager, I want appraisal TAT indicators, so that the 2-day SOP expectation can be monitored.
69. As an auditor, I want appraisal review actions logged, so that accountability is clear.

## 13.7 Sanction and Approval

70. As a Credit Manager, I want a sanction case created from a reviewed appraisal, so that approvers can decide.
71. As a CFO, I want to see all information needed for sanction approval, so that I can make an informed decision.
72. As a Director, I want to see assigned approval cases, so that I can approve only the cases assigned to me.
73. As a CFO, I want cases up to ₹5 lakh to require CFO + one Director, so that the SOP matrix is enforced.
74. As a CFO, I want cases above ₹5 lakh to require CFO + two Directors, so that higher-value loans receive additional approval.
75. As a CFO, I want loan-limit exceptions to require CFO + two Directors and a reason, so that policy deviations are controlled.
76. As an approver, I want to approve, reject or return a case with comments, so that decisions are clear.
77. As a system, I want rejection to require reason, so that borrowers and auditors can understand the decision.
78. As an auditor, I want approval actions immutable, so that decision evidence cannot be altered.
79. As a Credit Manager, I want a Credit Sanction Register generated from approvals, so that manual duplication is avoided.
80. As a CFO, I want an Exception Register, so that deviations are monitored.
81. As a Company Secretary, I want Director/relative borrower cases flagged, so that conflict rules and general meeting approval are enforced.
82. As a conflicted Director, I should be prevented from approving my own or relative’s case, so that governance is maintained.
83. As a Company Secretary, I want general meeting approval evidence attached for special cases, so that statutory requirements are documented.

## 13.8 Documentation and Security Package

84. As a Compliance user, I want documentation stage to start only after sanction approval, so that legal docs are prepared only for approved loans.
85. As a Compliance user, I want to generate a Power of Attorney, so that security enforcement authority is documented.
86. As a Compliance user, I want to generate a Tri-party Agreement, so that subsidiary deduction repayment is authorised.
87. As a Compliance user, I want to generate a Term Sheet, so that borrower terms are clearly disclosed.
88. As a Compliance user, I want to generate a Loan Agreement, so that loan terms are legally documented.
89. As a Compliance user, I want to upload executed legal documents, so that the final signed file is stored.
90. As a Company Secretary, I want stamp duty records, so that stamping compliance is documented.
91. As a Company Secretary, I want notarisation records, so that notarised document execution is evidenced.
92. As a Credit user, I want signature mismatch flagged, so that bank verification is obtained before disbursement.
93. As a Compliance user, I want a Bank Verification Letter workflow, so that signature mismatch can be resolved.
94. As a Company Secretary, I want a document checklist, so that all required documents are verified.
95. As a Company Secretary, I want to approve the checklist only after documents are complete, so that legal file integrity is maintained.
96. As a Credit Manager, I want to approve checklist after confirming disbursement limits, so that finance does not disburse incorrectly.
97. As a Sanction Committee member, I want final checklist approval, so that disbursement is formally authorised.
98. As a Senior Manager Finance, I want to sign checklist after disbursement, so that actual disbursement is evidenced.
99. As a Compliance user, I want physical share loans to require SH-4, so that share security is recorded.
100. As a Compliance user, I want demat share loans to require CDSL pledge, so that demat securities are controlled.
101. As a Company Secretary, I want blank-dated cheque custody tracked, so that security instruments are not lost or misused.
102. As a Company Secretary, I want security custody events, so that physical document movement is traceable.
103. As an auditor, I want restricted security documents protected and logged on download, so that privacy and legal risk are controlled.

## 13.9 SAP and Disbursement

104. As a Credit Manager, I want to create an SAP customer profile request after sanction, so that finance can create customer code.
105. As a Credit Manager, I want to generate SAP Excel details, so that the existing manual SAP process is supported.
106. As a Senior Manager – Finance, I want to confirm SAP customer code, so that disbursement readiness can proceed.
107. As a Senior Manager – Finance, I want existing SAP customer code reused, so that duplicate SAP profiles are avoided.
108. As a system, I want missing SAP customer code to block disbursement, so that accounting setup is complete.
109. As a Senior Manager – Finance, I want a disbursement readiness screen, so that I can see all pass/fail checks.
110. As a Senior Manager – Finance, I want to initiate disbursement only when ready, so that premature payment is prevented.
111. As a CFC, I want to review initiated payment requests, so that I can authorise the bank transfer.
112. As a CFC, I want to reject or hold a payment request, so that issues can be corrected before transfer.
113. As a Senior Manager – Finance, I want to record UTR and bank evidence, so that disbursement success is documented.
114. As a system, I want duplicate UTR blocked, so that duplicate payments are prevented.
115. As a borrower communication owner, I want disbursement advice generated, so that the borrower is informed.
116. As a Credit Manager, I want the Loan Register updated from system data, so that manual register maintenance is reduced.

## 13.10 Loan Account and Servicing

117. As a Credit Manager, I want a loan account created from sanction, so that the loan can be serviced.
118. As a Credit Manager, I want Loan Account 360, so that all loan information is visible in one place.
119. As an Accounts user, I want current outstanding principal, interest and status, so that I can reconcile accounting.
120. As a Credit Manager, I want loan status history, so that lifecycle changes are traceable.
121. As a Finance user, I want disbursement amount and bank details visible with masking, so that I can verify without exposing sensitive data.

## 13.11 Repayment and Interest

122. As a Credit/Accounts user, I want to record direct NEFT/RTGS repayments, so that borrower payments update the loan.
123. As a Credit/Accounts user, I want to record subsidiary deduction repayments, so that produce-payment deductions reduce outstanding.
124. As an Accounts user, I want duplicate bank references blocked, so that payments are not counted twice.
125. As an Accounts user, I want partial repayment allocated first to principal, so that SOP repayment allocation is enforced.
126. As an Accounts user, I want SAP receipt posting references captured, so that LMS and SAP can be reconciled.
127. As an Accounts user, I want bank statement lines matched to repayments, so that reconciliation exceptions are visible.
128. As a Credit Manager, I want repayment history on Loan Account 360, so that borrower status is clear.
129. As an Accounts user, I want yearly interest invoices generated, so that interest recovery is tracked.
130. As an Accounts user, I want monthly accrual entries, so that accounting is current.
131. As an Accounts user, I want duplicate monthly accrual blocked, so that accounting is not overstated.
132. As an Accounts user, I want unpaid interest capitalised after 30 April, so that new-year principal is updated according to SOP.
133. As a borrower communication owner, I want interest capitalisation notice generated, so that borrower is informed.
134. As an auditor, I want interest calculations tied to rate snapshots, so that historical calculations are explainable.

## 13.12 Monitoring, Default and Recovery

135. As a Credit Manager, I want DPD calculated, so that overdue loans can be monitored.
136. As a Credit Manager, I want SOP ageing buckets, so that loans outstanding 1–2 years, 2–3 years and 3+ years are visible.
137. As a CFO, I want quarterly MIS, so that portfolio risk is reviewed.
138. As a Credit Manager, I want reminder queues, so that overdue borrowers are contacted.
139. As a Credit Manager, I want default cases opened after missed principal repayment, so that follow-up begins.
140. As a Credit Manager, I want a 3-month grace period tracked, so that SOP extension is controlled.
141. As a Credit Manager, I want to classify default reason as intentional/non-intentional, so that next action is appropriate.
142. As a Credit Manager, I want non-intentional default to allow one-year extension, so that genuine hardship is handled.
143. As a Credit Manager, I want Extension Note generated, so that the file records the decision.
144. As a Credit Manager, I want Non-Payment Note after failed extension, so that recovery can be considered.
145. As a Sanction Committee member, I want to approve recovery decisions, so that security invocation is controlled.
146. As a Company Secretary, I want to invoke SH-4/CDSL/cheque only after recovery approval, so that legal safeguards are enforced.
147. As an auditor, I want recovery actions logged with evidence, so that conduct can be reviewed.
148. As a borrower-facing support user, I want grievances linked to recovery cases, so that complaints are handled transparently.

## 13.13 Closure, NOC and Archive

149. As a Credit Manager, I want closure readiness, so that loans close only after full settlement.
150. As a Company Secretary, I want NOC generated after closure, so that borrower receives formal clearance.
151. As a Company Secretary, I want SH-4 returned after closure, so that share security is released.
152. As a Company Secretary, I want blank-dated cheque returned after closure, so that borrower security documents are not retained unnecessarily.
153. As a Company Secretary, I want CDSL unpledge tracked, so that demat share security is released.
154. As a Compliance user, I want archive record created, so that loan documents are retained properly.
155. As an auditor, I want retention date at least 8 years after closure, so that records meet policy.

## 13.14 Compliance and Audit

156. As a CFO, I want Section 186 exposure tracker, so that statutory limits are monitored.
157. As a CFO, I want Section 186 special resolution flag, so that excess exposure is escalated.
158. As a CFO, I want NBFC principal business test, so that RBI registration risk is monitored.
159. As a Company Secretary, I want annual money-lending law review task, so that legal exemption status is reviewed.
160. As a Company Secretary, I want stamp duty register, so that document stamping compliance is visible.
161. As a Compliance user, I want KYC/re-KYC tracker, so that KYC obligations are monitored.
162. As a Compliance user, I want compliance evidence upload, so that review documentation is complete.
163. As a CFO/CS, I want overdue compliance tasks escalated, so that statutory controls are not missed.
164. As an Internal Auditor, I want audit logs and registers, so that I can verify process compliance.
165. As an Internal Auditor, I want audit exports restricted and logged, so that audit access is controlled.

## 13.15 Reports, Operations and Admin

166. As a CFO, I want a portfolio dashboard, so that total exposure, active loans and DPD are visible.
167. As a Credit Manager, I want application pipeline reports, so that bottlenecks are visible.
168. As a Compliance user, I want documentation readiness reports, so that blockers can be cleared.
169. As a Finance user, I want disbursement reports, so that bank transfers are tracked.
170. As an Accounts user, I want repayment and interest reports, so that accounting is reconciled.
171. As an Admin, I want configuration screens for loan policy, approval matrix and templates, so that rules can be updated without code changes.
172. As an Admin, I want configuration changes versioned and approved, so that historical calculations remain intact.
173. As DevOps, I want health checks and alerts, so that production issues are detected quickly.
174. As Support, I want runbooks and incident severity levels, so that operational incidents can be managed.
175. As QA, I want deterministic test data and public-interface tests, so that the platform can be tested reliably.
176. As an engineering agent, I want this PRD sliced into vertical issues, so that each issue is independently implementable and demoable.

---

# 14. Implementation Decisions

This section records implementation decisions suitable for issue planning. It intentionally avoids precise file paths and brittle code snippets.

## 14.1 Technology Decisions

| Area | Decision |
|---|---|
| Backend | Python + Django + Django REST Framework. |
| Frontend | React. |
| Database | PostgreSQL. |
| Auth | JWT access/refresh tokens. |
| Background jobs | Celery with Redis broker and Celery Beat scheduler. |
| Storage | Object storage or DMS behind storage adapter. |
| Integrations | Manual-first adapters for SAP, bank, CDSL and subsidiary flows; API-ready seams for future. |
| Deployment | Containerised deployment recommended. |
| API style | REST JSON APIs over HTTPS. |

## 14.2 Product Architecture Decisions

1. Build as one internal platform first, with future borrower portal as later extension.
2. Use lifecycle-first navigation: Applications, Members, Loans, Approvals, Documentation, Disbursement, Repayments, Monitoring, Default, Closure, Compliance, Reports and Admin.
3. Registers must be generated from system data rather than maintained as duplicate manual tables.
4. Every critical workflow action must produce audit evidence.
5. Every workflow detail page should show status, blockers and available actions.
6. Role dashboards should show task queues and ageing.
7. Business configuration must be versioned and effective-dated.

## 14.3 Codebase Design Decisions

1. Use modular Django apps aligned to business domains.
2. Place complex SOP logic in deep backend modules, not views or serializers.
3. React pages must not implement business rules; they display backend state/actions.
4. Use public module interfaces as testing seams.
5. Use adapters only for true external systems or boundary dependencies.
6. Use idempotency for disbursement, repayment, allocation, interest, communication and recovery actions.
7. Use transactions and row locks for financial state changes.
8. Use selectors for complex read/report queries.
9. Use immutable audit logs.
10. Use configuration resolver for policy/rate/document/template versions.

## 14.4 Deep Modules to Build

| Module | Responsibility |
|---|---|
| Permission Engine | RBAC, available actions, denial reasons. |
| Object Access | Scoped access to applications, loans, approvals and documents. |
| Sensitive Data Access | Mask/reveal sensitive fields with audit. |
| Document Storage | Upload, signed download, sensitivity, archive. |
| Active Member Status | Individual/FPC active member rules and relaxations. |
| Eligibility Assessment | SOP eligibility criteria and failures. |
| Loan Limit Calculator | Share/land/final limit and policy snapshots. |
| Appraisal Workflow | Maker-checker appraisal and sanction submission. |
| Approval Case Engine | Matrix, approvers, actions, sanctions and exceptions. |
| Conflict of Interest | Director/relative/committee conflicts and exclusions. |
| Document Generation | Template version, merge fields and PDF generation. |
| Document Checklist | Required documents, blockers and approval sequence. |
| Security Package | PoA, SH-4, CDSL, cheque, custody readiness. |
| SAP Customer Profile | Manual/API SAP request and code confirmation. |
| Loan Account Lifecycle | Account creation, status and ledger summary. |
| Disbursement Readiness | Readiness checks and blockers. |
| Disbursement Workflow | Initiation, CFC authorisation, UTR and activation. |
| Repayment Capture | Direct/subsidiary repayment creation. |
| Repayment Allocator | Principal-first allocation and ledger updates. |
| Interest Engine | Invoice, accrual, capitalisation and rate snapshots. |
| DPD Monitoring | Ageing buckets, reminders and MIS inputs. |
| Default Workflow | Missed repayment, grace, assessment and extension. |
| Recovery Workflow | Non-Payment Note, approval and security invocation. |
| Loan Closure | Closure, NOC, security return and archive. |
| Compliance Engines | Section 186, NBFC test and compliance task generation. |
| Report Export | Report generation, masking, async export and audit. |

## 14.5 Data Model Decisions

1. Use UUID internal IDs.
2. Use business-facing reference numbers for applications and loans.
3. Store money as decimal/numeric.
4. Store timestamps with timezone.
5. Encrypt sensitive fields.
6. Store hash columns for exact duplicate/search matching.
7. Store status history.
8. Store calculation snapshots.
9. Store document template versions.
10. Store configuration versions.
11. Use append-only approval actions and audit logs.
12. Use foreign keys to preserve traceability.
13. Use unique constraints for references, UTRs, SAP codes, monthly accruals and capitalisations.

## 14.6 API Decisions

1. Use explicit workflow action endpoints, not generic status patching.
2. Use standard success/error envelopes.
3. Include available actions and blocker reasons.
4. Return masked sensitive values by default.
5. Use idempotency keys for critical financial actions.
6. Use consistent error codes.
7. Use paginated lists.
8. Use async jobs for large reports.
9. Use signed URLs or proxied downloads for documents.
10. Use OpenAPI schema for API governance.

## 14.7 Security Decisions

1. Backend is authoritative for all permissions.
2. Sensitive data is masked by default.
3. Sensitive reveal requires reason and audit.
4. Restricted document downloads are audit logged.
5. Export permissions are separate from read permissions.
6. Critical roles should support MFA.
7. Logs must not contain raw sensitive values.
8. Document access depends on both object access and sensitivity.
9. Recovery and disbursement actions require strong workflow gates.
10. Role/permission changes invalidate or re-evaluate sessions.

## 14.8 Integration Decisions

1. SAP is manual-first in MVP with request, Excel and code confirmation.
2. Bank disbursement is manual-first in MVP with readiness, initiation, CFC and UTR.
3. CDSL is manual tracking in MVP with PRF, PSN, acceptance, invocation and unpledge.
4. Subsidiary deduction is manual/reconciliation-driven in MVP.
5. Email/SMS use provider adapters.
6. Object storage/DMS uses storage adapter.
7. CKYC, bureau and e-sign are future adapters unless confirmed in MVP.
8. External integration logs must redact sensitive values.
9. Manual evidence can satisfy workflow gates in MVP.

---

# 15. Testing Decisions

## 15.1 Testing Philosophy Decisions

1. Tests must verify observable behaviour through public interfaces.
2. Do not test private helper methods when public module behaviour can be tested.
3. Do not mock internal deep modules.
4. Mock/fake true external boundaries such as SAP, bank, SMS, email, storage, CDSL, CKYC, bureau and e-sign.
5. Use behaviour-first TDD for critical modules.
6. Use vertical tracer bullets for implementation issues.
7. Refactor after tests are green.
8. Every critical workflow must have happy path and blocked path tests.
9. Financial actions must test idempotency and duplicate prevention.
10. Permissions must be tested at backend/API level, not only frontend.

## 15.2 Modules Requiring P0 Tests

| Module | Test Priority |
|---|---|
| Permission Engine | P0 |
| Object Access | P0 |
| Sensitive Data Access | P0 |
| Eligibility Assessment | P0 |
| Loan Limit Calculator | P0 |
| Approval Case Engine | P0 |
| Document Checklist | P0 |
| Security Package | P0 |
| Disbursement Readiness | P0 |
| Disbursement Workflow | P0 |
| Repayment Allocator | P0 |
| Interest Engine | P0 |
| Recovery Workflow | P0 |
| Loan Closure | P0 |
| Audit Recorder | P0 |

## 15.3 Required Test Types

| Test Type | Required |
|---|---|
| Unit/module tests | Yes |
| API contract tests | Yes |
| Frontend component tests | Yes |
| Frontend page tests | Yes |
| E2E workflow tests | Yes |
| Permission tests | Yes |
| Security/privacy tests | Yes |
| Financial integrity tests | Yes |
| Integration fake tests | Yes |
| Report/export tests | Yes |
| Compliance tests | Yes |
| Performance tests | Yes before go-live |
| Migration tests | If migration is in scope |
| Operational tests | Yes |
| UAT scripts | Yes |

## 15.4 UAT Decisions

1. UAT must be role-based.
2. UAT scripts must map to SOP lifecycle.
3. Business users must validate document templates and reports.
4. CFO/CS must validate approval/compliance trackers.
5. Finance/CFC must validate disbursement workflow.
6. Accounts/Credit must validate repayment/interest workflow.
7. Auditor must validate audit evidence and registers.

---

# 16. Out of Scope

The following are explicitly out of scope for MVP unless later confirmed.

1. Borrower self-service portal.
2. Native mobile app.
3. Direct SAP API integration.
4. Direct RBL Bank payment API integration.
5. CKYC API integration.
6. Credit bureau API integration.
7. E-sign and e-stamping.
8. CDSL API integration.
9. AI-based document extraction.
10. Advanced data warehouse and BI.
11. Automated external legal recovery case management.
12. Multi-language borrower-facing portal.
13. Automated physical custody hardware integration.
14. Automatic legal validation of documents.
15. Replacing SAP as accounting system.
16. Replacing bank portal as payment system in MVP.
17. Final legal opinion on statutory provisions.
18. Final business credit decisioning beyond configured SOP rules.
19. Consumer-grade public borrower app.
20. Automated loan underwriting outside SFPCL policy.

---

# 17. Open Questions and Clarifications

These decisions must be resolved or explicitly configured before final MVP signoff.

## 17.1 Policy and Legal

1. Confirm operative loan limit rule: 30% of valuation vs 10% / ₹200 per share.
2. Confirm exact approval handling for amount exactly ₹5,00,000. Current assumption: up to ₹5 lakh = CFO + one Director.
3. Resolve Annexure K inconsistency: Credit Sanction Register vs Grievance Form.
4. Confirm legal documentation signer: Company Secretary vs CFO/designated Directors.
5. Confirm final interest benchmark, spread and reset cadence.
6. Confirm penal interest triggers, rate and fees.
7. Confirm whether NACH/ECS is required.
8. Confirm whether guarantors are required.
9. Confirm whether credit bureau checks are mandatory.
10. Define intentional vs non-intentional default criteria.
11. Define sale-of-shares / security invocation recovery procedure.
12. Confirm recovery approval authority: Sanction Committee, Board or both.
13. Confirm director/relative general meeting approval workflow.
14. Confirm state money-lending law annual review scope beyond Maharashtra.
15. Confirm final KYC retention period.

## 17.2 Operational

1. Confirm hosting model: cloud, private cloud or on-premise.
2. Confirm object storage/DMS provider.
3. Confirm email provider.
4. Confirm SMS provider.
5. Confirm SAP workflow owner and API/file/manual mode.
6. Confirm bank workflow owner and API/manual mode.
7. Confirm data migration scope.
8. Confirm production RPO/RTO.
9. Confirm support SLA.
10. Confirm MFA requirement.
11. Confirm training plan and UAT owners.
12. Confirm archive physical/digital locations.

---

# 18. Suggested Vertical-Slice Issue Breakdown

This PRD is structured for conversion into vertical tracer-bullet issues. The following issue map is a proposed starting point. Each issue should be independently demoable and include schema, backend, API, UI, permissions, audit and tests where relevant.

## 18.1 Foundation Issues

### Issue 1 — User Login, Session and Role-Aware Shell

**What to build:** A user can log in, see role-aware navigation and log out.

**Blocked by:** None.

**User stories covered:** 1–4, 11.

**Acceptance criteria:**

- JWT login works.
- Inactive user blocked.
- Current user endpoint returns roles/permissions.
- React shell renders role-aware nav.
- Logout revokes session.
- Basic audit log created.

### Issue 2 — User, Role, Team and Permission Administration

**What to build:** Admin can manage users, roles, teams and permissions.

**Blocked by:** Issue 1.

**User stories covered:** 5–10, 172.

**Acceptance criteria:**

- Admin can create/suspend user.
- Role assignment works.
- Permission checks work on backend.
- Role changes are audit logged.
- Auditor cannot edit business records.

### Issue 3 — Document Storage with Restricted Download Audit

**What to build:** Upload/download document files with sensitivity and audit.

**Blocked by:** Issue 1.

**User stories covered:** 31–33, 89, 103.

**Acceptance criteria:**

- File upload works.
- Restricted documents require permission.
- Download uses signed/proxied access.
- Restricted downloads are audit logged.
- Invalid file types rejected.

### Issue 4 — Audit Timeline and Immutable Audit Logs

**What to build:** Critical actions write audit logs and users can view entity timeline.

**Blocked by:** Issue 1.

**User stories covered:** 13, 21, 78, 164.

**Acceptance criteria:**

- Audit events store actor/action/entity/time.
- Sensitive values are redacted.
- Timeline visible on application/loan.
- Audit logs cannot be edited.

---

## 18.2 Member, KYC and Application Issues

### Issue 5 — Member Master and Borrower 360

**What to build:** Create/search/view individual and FPC members with masked sensitive fields.

**Blocked by:** Issues 1–3.

**User stories covered:** 15–26.

**Acceptance criteria:**

- Individual and FPC member creation.
- PAN/Aadhaar masked.
- Borrower 360 shows KYC/share/land/crop/loan sections.
- Duplicate PAN detection using secure hash.

### Issue 6 — Nominee, Witness and KYC Verification

**What to build:** Add nominee/witness and upload/verify KYC documents.

**Blocked by:** Issue 5.

**User stories covered:** 27–37.

**Acceptance criteria:**

- Minor nominee blocked.
- Witness must be shareholder.
- KYC documents upload and verification.
- Re-KYC due date calculated.
- KYC download restricted.

### Issue 7 — Loan Application Draft and Reference Number

**What to build:** Create draft application with unique LO reference.

**Blocked by:** Issue 5.

**User stories covered:** 38–41.

**Acceptance criteria:**

- Draft application created.
- Reference number unique.
- Required fields validated.
- Application status shown.

### Issue 8 — Completeness Check, Deficiencies and Resubmission

**What to build:** Deputy Manager can mark incomplete, create deficiencies and allow resubmission.

**Blocked by:** Issues 6–7.

**User stories covered:** 42–47.

**Acceptance criteria:**

- Required document checklist shown.
- Deficiencies created.
- Deficiency notice logged.
- Resolved deficiencies allow resubmission.
- Appraisal blocked until complete.

---

## 18.3 Credit and Approval Issues

### Issue 9 — Eligibility Assessment

**What to build:** Run SOP eligibility assessment with pass/fail reasons.

**Blocked by:** Issue 8.

**User stories covered:** 50–56.

**Acceptance criteria:**

- Active member/default/doc/purpose checks run.
- Failed checks shown.
- Eligibility result stored.
- Override requires permission and reason.

### Issue 10 — Active Member Status Engine

**What to build:** Calculate individual/FPC active member status and relaxation logic.

**Blocked by:** Issue 5.

**User stories covered:** 51, 57 indirectly; active member stories.

**Acceptance criteria:**

- Four-year rules work.
- One-year relaxation works.
- Three-year service route works.
- Result explanation stored.

### Issue 11 — Loan Limit Calculator

**What to build:** Calculate share/land/final eligible amount with policy snapshot.

**Blocked by:** Issues 5, 9.

**User stories covered:** 57–62.

**Acceptance criteria:**

- Share limit calculated.
- Land limit calculated.
- Lower-of-two rule applied.
- Exceeds-limit flag.
- Policy version stored.
- Ambiguous rule shown until config resolved.

### Issue 12 — Appraisal Note and Credit Manager Review

**What to build:** Deputy Manager prepares appraisal; Credit Manager reviews and submits.

**Blocked by:** Issues 9–11.

**User stories covered:** 63–69.

**Acceptance criteria:**

- Appraisal note can be drafted.
- Credit Manager review required.
- Return/review actions work.
- TAT visible.
- Submission to sanction creates next workflow.

### Issue 13 — Approval Matrix and Sanction Case

**What to build:** Create approval cases with correct CFO/Director requirements.

**Blocked by:** Issue 12.

**User stories covered:** 70–80.

**Acceptance criteria:**

- Up to ₹5 lakh requires CFO + one Director.
- Above ₹5 lakh requires CFO + two Directors.
- Exception route works.
- Approval actions immutable.
- Sanction decision created after required approvals.

### Issue 14 — Conflict-of-Interest and General Meeting Evidence

**What to build:** Director/relative borrower conflict handling.

**Blocked by:** Issue 13.

**User stories covered:** 81–83.

**Acceptance criteria:**

- Conflict flag visible.
- Conflicted approver blocked.
- General meeting evidence required.
- Remaining approvers complete case.

---

## 18.4 Documentation and Security Issues

### Issue 15 — Document Template and Generation

**What to build:** Generate key legal documents from templates.

**Blocked by:** Issue 13.

**User stories covered:** 84–90.

**Acceptance criteria:**

- Templates versioned.
- Documents generated and stored.
- Regeneration requires reason.
- Executed uploads linked.

### Issue 16 — Signature, Stamp Duty and Notarisation

**What to build:** Capture signatures, stamp duty, notarisation and signature mismatch resolution.

**Blocked by:** Issue 15.

**User stories covered:** 90–93.

**Acceptance criteria:**

- Stamp records.
- Notary records.
- Signature mismatch flag.
- Bank Verification Letter resolves mismatch.
- Missing required records block checklist.

### Issue 17 — Document Checklist Approval Sequence

**What to build:** Checklist required items and CS/Credit/Sanction/Finance approvals.

**Blocked by:** Issues 15–16.

**User stories covered:** 94–98.

**Acceptance criteria:**

- Required items generated.
- Blockers displayed.
- CS approval after completion.
- Credit Manager approval.
- Sanction final approval.
- Senior Manager post-disbursement signature.

### Issue 18 — Security Package: PoA, SH-4, Cheques and Custody

**What to build:** Physical share security package.

**Blocked by:** Issues 15–17.

**User stories covered:** 99, 101–103.

**Acceptance criteria:**

- PoA tracked.
- SH-4 required for physical shares.
- Blank cheque and cancelled cheque captured.
- Custody movements logged.
- Restricted access enforced.

### Issue 19 — Security Package: CDSL Pledge

**What to build:** Demat security path with CDSL pledge milestones.

**Blocked by:** Issues 15–17.

**User stories covered:** 100, 103.

**Acceptance criteria:**

- PRF submitted.
- PSN captured.
- Acceptance/rejection captured.
- Pledge acceptance marks security ready.
- Unpledge supported later.

---

## 18.5 SAP and Disbursement Issues

### Issue 20 — SAP Customer Request and Code Confirmation

**What to build:** Manual SAP request and customer code workflow.

**Blocked by:** Issue 13.

**User stories covered:** 104–108.

**Acceptance criteria:**

- Request after sanction.
- Excel generated.
- Senior Finance confirms code.
- Existing code reused.
- Missing code blocks readiness.

### Issue 21 — Loan Account Creation

**What to build:** Create loan account from sanction and show Loan Account 360 shell.

**Blocked by:** Issues 13, 20.

**User stories covered:** 117–121.

**Acceptance criteria:**

- Account created once.
- Sanction snapshot stored.
- Status visible.
- Loan Account 360 shell displays key sections.

### Issue 22 — Disbursement Readiness

**What to build:** Readiness checks for sanction, docs, security, SAP and bank verification.

**Blocked by:** Issues 17–21.

**User stories covered:** 109–110.

**Acceptance criteria:**

- Pass/fail checks shown.
- Blocker reasons shown.
- Missing SAP/checklist/security blocks readiness.
- Ready loan can proceed.

### Issue 23 — Payment Initiation, CFC Authorisation and UTR

**What to build:** Disbursement workflow from initiation to successful bank transfer.

**Blocked by:** Issue 22.

**User stories covered:** 110–116.

**Acceptance criteria:**

- Senior Manager initiates.
- CFC authorises.
- Success requires UTR.
- Duplicate UTR blocked.
- Loan activated.
- Disbursement advice generated.

---

## 18.6 Servicing Issues

### Issue 24 — Direct Repayment and Principal-First Allocation

**What to build:** Record direct repayment and allocate principal-first.

**Blocked by:** Issue 23.

**User stories covered:** 122, 124–128.

**Acceptance criteria:**

- Direct repayment recorded.
- Duplicate UTR blocked.
- Allocation principal-first.
- Outstanding updated.
- SAP posting reference captured.

### Issue 25 — Subsidiary Deduction Repayment

**What to build:** Record subsidiary repayment and reconciliation metadata.

**Blocked by:** Issue 23.

**User stories covered:** 123, 127–128.

**Acceptance criteria:**

- Subsidiary source captured.
- Produce/payment reference captured.
- Bank reference captured.
- Duplicate reference blocked.
- Reconciliation exceptions visible.

### Issue 26 — Interest Invoice, Accrual and Capitalisation

**What to build:** Annual interest invoice, monthly accrual and unpaid interest capitalisation.

**Blocked by:** Issues 24–25.

**User stories covered:** 129–134.

**Acceptance criteria:**

- Interest invoice generated.
- Monthly accrual unique.
- Capitalisation after 30 April.
- Principal increases.
- Duplicate capitalisation blocked.
- Borrower notice generated.

### Issue 27 — DPD, Reminders and Quarterly MIS

**What to build:** Monitoring dashboard, DPD buckets, reminders and MIS.

**Blocked by:** Issues 24–26.

**User stories covered:** 135–138.

**Acceptance criteria:**

- DPD calculated.
- SOP buckets displayed.
- Reminder queue generated.
- Quarterly MIS generated.

---

## 18.7 Default, Recovery and Closure Issues

### Issue 28 — Default Case, Grace and Extension

**What to build:** Missed repayment default workflow.

**Blocked by:** Issue 27.

**User stories covered:** 139–144.

**Acceptance criteria:**

- Missed repayment opens default.
- Three-month grace period.
- Non-intentional assessment.
- One-year extension.
- Extension Note generated.

### Issue 29 — Non-Payment Note and Recovery Approval

**What to build:** Recovery approval workflow after failed extension.

**Blocked by:** Issue 28.

**User stories covered:** 144–147.

**Acceptance criteria:**

- Non-Payment Note created.
- Recovery approval case created.
- Recovery action blocked until approval.
- Approval route configurable.

### Issue 30 — Security Invocation and Recovery Evidence

**What to build:** Execute approved recovery action using SH-4/CDSL/cheque.

**Blocked by:** Issue 29.

**User stories covered:** 146–148.

**Acceptance criteria:**

- Approved action selects instrument.
- Evidence required.
- Security invocation logged.
- Grievance linkage supported.

### Issue 31 — Closure, NOC, Security Return and Archive

**What to build:** Full closure workflow.

**Blocked by:** Issues 24–30.

**User stories covered:** 149–155.

**Acceptance criteria:**

- Closure blocked with outstanding.
- NOC generated after closure.
- SH-4/cheque returned.
- CDSL unpledge recorded.
- Archive with 8-year retention.

---

## 18.8 Compliance, Reports and Ops Issues

### Issue 32 — Compliance Dashboard and Task Engine

**What to build:** Compliance control/task/evidence framework.

**Blocked by:** Issue 4.

**User stories covered:** 156–165.

**Acceptance criteria:**

- Tasks generated by frequency.
- Evidence upload.
- Review workflow.
- Overdue dashboard.
- Audit logs.

### Issue 33 — Section 186 and NBFC Trackers

**What to build:** Statutory calculation trackers.

**Blocked by:** Issue 32.

**User stories covered:** 156–158.

**Acceptance criteria:**

- Section 186 calculation.
- Special resolution flag.
- NBFC ratio calculation.
- Trigger/warning status.

### Issue 34 — KYC/Re-KYC, Stamp Duty, Money-Lending and Grievance

**What to build:** Remaining compliance trackers.

**Blocked by:** Issue 32.

**User stories covered:** 159–165.

**Acceptance criteria:**

- KYC/re-KYC tracker.
- Stamp duty register.
- Annual money-lending review.
- Grievance register.

### Issue 35 — Reports Centre and Secure Exports

**What to build:** Reports and export framework.

**Blocked by:** Issues 13, 17, 23, 27, 31, 33.

**User stories covered:** 166–171.

**Acceptance criteria:**

- Core registers available.
- Export permissions enforced.
- Sensitive masking.
- Async large exports.
- Export audit.

### Issue 36 — Operational Readiness: Jobs, Monitoring, Backup and Runbooks

**What to build:** Production operations readiness.

**Blocked by:** Core foundation and major workflow modules.

**User stories covered:** 173–176.

**Acceptance criteria:**

- Health checks.
- Job run records.
- Celery Beat monitored.
- Backup/restore verified.
- Critical alerts configured.
- Runbooks available.

---

# 19. MVP Release Plan

## 19.1 Recommended Phases

| Release | Theme |
|---|---|
| R0 | Discovery finalisation and setup |
| R1 | Core platform foundation |
| R2 | Loan origination and credit assessment |
| R3 | Sanction and approval workflow |
| R4 | Documentation and security package |
| R5 | SAP and disbursement |
| R6 | Repayment, interest and monitoring |
| R7 | Default, recovery, closure and compliance |
| R8 | Reports, hardening, UAT and go-live |
| R9 | Post-go-live enhancements |

## 19.2 MVP Readiness Criteria

MVP can go live only when:

1. User login and RBAC are working.
2. Member, KYC, application and eligibility are working.
3. Loan limit rule is configured.
4. Approval matrix is working.
5. Documentation and security gates are working.
6. SAP customer code workflow is working.
7. Disbursement readiness, initiation, CFC authorisation and UTR are working.
8. Repayment and interest basics are working.
9. Default/recovery controls are present.
10. Closure/NOC/security return is present.
11. Compliance trackers are present.
12. Reports and audit logs are present.
13. Security/privacy tests pass.
14. UAT signoff is received.
15. Operational readiness is confirmed.

---

# 20. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Loan limit ambiguity unresolved | Incorrect eligibility or approvals | Make rule configurable and require final business signoff before production. |
| Document template delays | Documentation workflow delayed | Start legal template review early. |
| Manual SAP/bank processes cause bottlenecks | Disbursement delays | Dashboards, ageing, reminders and evidence workflow. |
| Approval conflicts not captured | Governance failure | Conflict module and UAT special-case scripts. |
| Sensitive data exposure | Privacy/legal risk | Encryption, masking, restricted access and audit. |
| Users bypass system through offline process | Audit gaps | Make system disbursement readiness mandatory. |
| Migration data quality poor | Go-live delay | Trial migrations and reconciliation reports. |
| Overbuilding APIs too early | Delivery delay | Manual-first adapter approach. |
| Recovery procedure unclear | Recovery module uncertainty | Configure approval route and capture open legal decision. |
| Reports not trusted | Business rejection | Reconcile reports in UAT. |
| Background jobs fail silently | Monitoring/compliance risk | Job run records and alerts. |
| Access permissions too broad | Privacy and fraud risk | Access review and least privilege. |

---

# 21. Further Notes

## 21.1 Product Design Notes

1. The system should feel like a lifecycle control centre, not merely a form system.
2. Every workflow stage must show:
   - current status;
   - required next action;
   - blockers;
   - owner;
   - due/ageing;
   - audit history.
3. Users should never need to guess why an action is unavailable.
4. Registers should be system-generated.
5. Exceptions should be visible and auditable, not hidden in notes.
6. Sensitive data should be masked unless a user has strong reason to reveal it.
7. Document readiness and disbursement readiness should be treated as first-class product experiences.

## 21.2 Engineering Notes

1. Use deep domain modules for workflow complexity.
2. Avoid shallow pass-through abstractions.
3. Avoid duplicating business logic in React.
4. Treat external systems as adapters.
5. Test through module interfaces.
6. Build vertical slices that can be demoed independently.
7. Keep policy/configuration versioned.
8. Preserve historical snapshots.
9. Use idempotency on financial actions.
10. Use audit logs consistently.

## 21.3 Issue Authoring Notes

When converting this PRD to issues:

1. Use vertical slices, not horizontal layers.
2. Each issue should be demoable.
3. Each issue should include acceptance criteria.
4. Each issue should identify blockers.
5. Each issue should mention user stories covered.
6. Each issue should avoid brittle file paths.
7. Each issue should include testing expectations.
8. Publish blockers before dependent issues.
9. Use domain vocabulary consistently.
10. Treat the PRD as the parent issue/source.

---

# 22. PRD Acceptance Criteria

This PRD is considered ready to convert into issues when:

| ID | Criteria |
|---|---|
| PRD-AC-001 | Problem statement is clear. |
| PRD-AC-002 | Solution scope is clear. |
| PRD-AC-003 | MVP and future scope are separated. |
| PRD-AC-004 | User roles are defined. |
| PRD-AC-005 | User stories cover full lifecycle. |
| PRD-AC-006 | Functional requirements cover SOP stages and compliance. |
| PRD-AC-007 | Implementation decisions are sufficient for issue slicing. |
| PRD-AC-008 | Testing decisions are sufficient for TDD/QA planning. |
| PRD-AC-009 | Open questions are visible. |
| PRD-AC-010 | Vertical slice issue map is present. |

---

# 23. Final Summary

SFPCL needs a secure, auditable and role-based platform that turns its member credit SOP into enforceable digital workflow. The platform must handle sensitive borrower/KYC data, legal/security documentation, multi-role approvals, SAP and bank handoffs, repayment and interest accounting, default/recovery controls, closure/NOC/security return and statutory compliance.

The MVP should prioritise:

1. Member/KYC/application foundation.
2. Eligibility and loan limit correctness.
3. Sanction governance.
4. Documentation and security readiness.
5. Disbursement controls.
6. Repayment and interest correctness.
7. Default/recovery safeguards.
8. Closure and compliance evidence.
9. Security, audit and operations readiness.

The product should be built using vertical tracer-bullet issues where each slice cuts through schema, backend, API, UI, permissions, audit and tests.

The most important product requirement is:

```text
No loan should be disbursed, no recovery action should be initiated and no sensitive data should be exposed unless the platform has verified the correct user, role, object access, workflow state, evidence, approvals, policy rules and audit requirements.
```

This PRD is ready to be used as the parent document for issue creation and delivery planning.
