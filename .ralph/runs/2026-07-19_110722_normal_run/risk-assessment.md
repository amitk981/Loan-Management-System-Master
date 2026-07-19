# Risk Assessment

Risk level: High (as declared by slice 009L4).

- The change affects nondisclosing Loan Account counts/pages, staff authority projections, SAP
  evidence selection, and payment/advice action visibility. Incorrect inclusion could disclose an
  account or advertise an action its mutation would reject.
- Mitigation: list eligibility is composed from lifecycle-, SAP-, and transfer-owned queryset
  predicates; the requested window is reconciled through exact scalar/bulk evidence owners; the
  lifecycle bulk resolver checks the same singular history/audit/workflow bodies as detail reads.
- Mitigation: S36, S37, combined Senior Finance, and CFC branches apply database count/offset/limit
  before projection. The combined sequence uses disjoint S37-without-account and Loan Account
  counts, so an S37 row cannot displace or duplicate an account across page boundaries.
- Mitigation: transfer-success and advice action visibility now delegates to public mutation-owner
  predicates, including persisted actor authority, object scope, current evidence, and account
  state. Existing authorisation actions retain their public authority and current-initiation gate.
- Residual risk: workbook/storage integrity and transaction-race drift cannot be represented wholly
  in SQL. Projection therefore rechecks only the requested page plus a documented four-row
  reconciliation window and fails closed. Independent validation should retain adversarial evidence
  corruption and mixed-portfolio probes.
- No model/migration, dependency, protected-file, source-document, or hosted UI change was made.
- Owner standing approval applies; no `[revoked]` marker was found for this slice.
