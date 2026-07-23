# Risk Assessment

Risk level: Medium

- Selected slice: 012A2-finance-and-servicing-report-catalogue
- Mode: normal_run
- Database/model impact: None. No migration or index was added.
- Permission impact: No permission or role grant was added. Every report reuses an existing
  owner read permission and canonical object scope. Missing scope returns a nondisclosing 403.
- Financial integrity: Reports project persisted money and owner snapshots. They do not calculate
  workflow outcomes, allocations, invoice/accrual amounts, or MIS totals. Filtered monetary totals
  use database sums over the same scoped queryset before pagination.
- Privacy: Security custody uses the security evidence coordinator's public projection and omits
  custody evidence/custodian ids. SAP pending reuses the masked/minimised assigned-workspace
  projection. No raw PAN, Aadhaar, bank account, cheque number, or BO account is emitted.
- Compatibility: Credit Sanction Register totals are opt-in to the report adapter; the established
  owner register endpoint retains its original pagination shape. The reverse-consumer pack caught
  and verified this compatibility condition.
- Performance: Every seeded report GET is asserted at no more than 40 queries. No index was added
  because the representative query-count evidence is bounded and the slice requires measured
  evidence before schema optimisation.
- Diff limits: 15 product/contract files and 1,244 changed product/contract lines, below the
  configured 30-file/2,000-line limits.
- Residual risk: Exact route/filter naming and custody timestamp placement were not specified by
  source and are recorded as A-169. The Security Custody and SAP Pending selectors deliberately
  preserve their restrictive owner scope; future governance may introduce dedicated bulk report
  selectors without widening access.
- Independent validation: Required. The orchestrator owns the authoritative selective backend lane.
