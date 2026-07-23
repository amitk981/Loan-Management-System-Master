# 012A3 Complete Report Catalogue Matrix

## 23 product reports plus two fixed section-40 interfaces

| Stable code | Source owner | Required authority | Slice |
|---|---|---|---|
| `application-pipeline` | Loan Request Register | `reports.application_pipeline.read` plus application scope | 012A |
| `documentation-readiness` | Legal document checklist | `documents.checklist.read` plus sanctioned-documentation scope | 012A |
| `disbursement-pending` | Disbursement | `finance.disbursement.readiness` plus account scope | 012A |
| `loan-portfolio` | Loan account | `reports.portfolio.read` plus account scope | 012A |
| `dpd` | DPD status | `reports.dpd.read` plus account scope | 012A |
| `compliance-dashboard` | Section 186 and NBFC trackers | `reports.compliance.read` plus both statutory reads | fixed section-40 API |
| `credit-sanction` | Credit Sanction Register | `approvals.sanction_register.read` plus approval scope | 012A2 |
| `exception` | Exception Register | `approvals.exception_register.read` plus approval scope | 012A2 |
| `security-custody` | Security evidence coordinator | `security.package.read` plus Stage-4 scope | 012A2 |
| `sap-pending` | SAP assigned workspace | `finance.sap_code.read` plus exact assignee scope | 012A2 |
| `disbursement` | Disbursement | `finance.disbursement.readiness` plus account scope | 012A2 |
| `repayment` | Repayment | `finance.loan_account.read` plus account scope | 012A2 |
| `interest-invoice` | Interest invoice engine | `finance.loan_account.read` plus account scope | 012A2 |
| `interest-accrual` | Accrual owner | `finance.loan_account.read` plus account scope | 012A2 |
| `cfo-quarterly-mis` | Frozen quarterly MIS | `finance.loan_account.read` plus complete frozen scope | 012A2 |
| `default` | Default Case list interface | `defaults.case.read` plus canonical case scope | 012A3 |
| `recovery` | Recovery Decision/Action within canonical default scope | `defaults.case.read` plus canonical case scope | 012A3 |
| `closure-noc` | Closure/NOC/security-return/archive owners | `closure.readiness.read` plus closure role/audit scope | 012A3 |
| `section-186` | Section 186 tracker | `compliance.section186.read` plus auditor scope | 012A3 |
| `nbfc-test` | NBFC principal-business test | `compliance.nbfc_test.read` plus auditor scope | 012A3 |
| `kyc-rekyc` | KYC Review Tracker | governed KYC manage/task-read authority plus member scope | 012A3 |
| `stamp-duty` | Legal Stamp Duty Record | `documents.checklist.read` plus sanctioned-documentation scope | 012A3 |
| `money-lending-review` | Money-Lending Law Review | owner manage or scoped task read | 012A3 |
| `grievance` | Grievance Workflow | `compliance.grievance.read` plus member scope | 012A3 |
| `audit-log-export` | Restricted 012C export policy + 012D audit selector | metadata-only handoff; no generic selector | fixed section-40 API |

The registry test asserts exactly 25 definitions. No alias substitutes for a missing owner.

## Reconciliation, masking, totals, and denial

- Seeded tests reconcile Default, Recovery, Closure/NOC, Section 186, NBFC, KYC/Re-KYC,
  Stamp Duty, Money-Lending Review, and Grievance identities against canonical owner truth.
- Recovery approval/security evidence, document ids, and interaction logs are omitted.
- KYC encrypted identifiers/documents, stamp evidence/remarks, restricted legal/Board
  documents, grievance internals/history, and closure document/storage authority are omitted.
- Every new code participates in the default-deny registry matrix. Invalid controlled filters
  return `400 VALIDATION_ERROR`; seeded reads assert bounded pagination/query counts.
- `report-catalogue-final-green.log`: 19/19 report tests passed.
- `focused-reverse-consumers-green.log`: 95/95 focused owner/reverse-consumer tests passed
  (one pre-existing skip).

## Restricted audit-export handoff proof

`audit-log-export` has `selector=None` and the stable handoff marker
`012C-sensitive-export-policy+012D-audit-selector`. The generic route returns nondisclosing 403 even
to an actor holding `audit.audit_log.read`, `audit.export`, `reports.export`, and
`reports.export_sensitive`; it performs no audit query and creates no download/job route.
