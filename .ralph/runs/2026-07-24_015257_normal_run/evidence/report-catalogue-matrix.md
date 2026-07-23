# 012A2 Report Catalogue Evidence Matrix

## Code, source owner, permission, and reconciliation

| Stable code | Persisted source owner reused | Required read authority | Filters | Reconciliation evidence |
|---|---|---|---|---|
| `credit-sanction` | `approvals.sanction_register.list_entries` | `approvals.sanction_register.read` plus approval-case scope | `financial_year`, `decision` | `ApprovalReportCatalogueApiTests` compares the report row identity to the canonical register entry and proves the filtered amount total |
| `exception` | `approvals.exception_register.list_entries` | `approvals.exception_register.read` plus approval-case scope | `status`, `exception_type` | `ApprovalReportCatalogueApiTests` compares the report row identity to the canonical exception entry |
| `security-custody` | Security evidence coordinator + public package projections | `security.package.read` plus canonical Stage-4/object scope | `instrument_type` | `SecurityCustodyReportCatalogueApiTests` compares held SH-4 truth and proves restricted evidence/custodian identity is absent |
| `sap-pending` | `sap_customer_profile.assigned_workspace_rows` | `finance.sap_code.read` plus exact assigned Senior Finance completion scope | `request_status` | `SapPendingReportCatalogueApiTests` compares the retained sent request and proves PAN/Aadhaar/customer code minimisation |
| `disbursement` | `Disbursement` rows constrained by `loan_account_read.scoped_account_candidates` | `finance.disbursement.readiness` plus `finance.loan_account.read`/account scope | inclusive dates, authorisation and transfer status | `DisbursementReportCatalogueApiTests` compares amount/reference/status/date/account truth and complete filtered total |
| `repayment` | `Repayment` rows constrained by `loan_account_read.scoped_account_candidates` | `finance.loan_account.read` plus account scope | inclusive dates, source, allocation and SAP status | `RepaymentReportCatalogueApiTests` compares receipt identity/money/reference/status and complete filtered total |
| `interest-invoice` | `interest_engine.list_invoices` and its serializer | `finance.loan_account.read` plus account scope | `financial_year`, `invoice_status` | `InterestInvoiceReportCatalogueApiTests` compares the complete report row with the owner generation projection |
| `interest-accrual` | `AccrualEntry` rows constrained by canonical account scope; `interest_engine.serialize_accrual` | `finance.loan_account.read` plus account scope | `accrual_month`, SAP status | `InterestAccrualReportCatalogueApiTests` compares the complete owner projection and filtered accrued-interest total |
| `cfo-quarterly-mis` | `quarterly_mis.list_reports` | `finance.loan_account.read` plus complete frozen portfolio scope | required financial year and quarter | `CfoQuarterlyMisReportCatalogueApiTests` compares the complete report row with the frozen owner generation projection |

## Cross-cutting evidence

- `ReportCatalogueApiTests.test_all_required_catalogue_codes_are_registered_and_default_deny`
  proves every named code resolves and returns a nondisclosing 403 without owning authority.
- Every seeded report GET is wrapped in `CaptureQueriesContext` with a maximum of 40 queries.
  The nine-test focused run passed in `evidence/terminal-logs/report-catalogue-query-bounds.log`.
- Standard pagination shape is asserted for every seeded report. Stable ordering is delegated to
  the owner projection or explicitly ends in the persisted UUID identity.
- `evidence/terminal-logs/focused-and-reverse-consumer-green.log` contains 28 passing focused and
  reverse-consumer tests, including the pre-existing report foundation, approval registers,
  interest invoice list, quarterly MIS list, and exact SAP-assignee workspace.
- Report reads contain no mutation calls. The report tests first create truth through public owner
  interfaces, then compare the report projection back to that retained truth.
- RED/GREEN logs are retained per tracer bullet under `evidence/terminal-logs/`.

## Source traceability

- `docs/source/implementation-roadmap.md` §17.3 and R8-AC-001 name the critical catalogue and
  require correct permissions/export readiness.
- `docs/source/screen-spec.md` S69 groups these reports under sanction, documentation/security,
  disbursement, repayment, interest, and monitoring.
- `docs/source/api-contracts.md` §40 supplies the common read-only report family and standard list
  conventions.
- `docs/source/auth-permissions.md` §§12.6-12.13 and §33 supply the existing owner permissions;
  no broad report grant was added.
- `docs/source/security-privacy.md` §32 requires minimisation/masking. The custody and SAP report
  tests prove restricted evidence and identity values are not projected.
