# Bank and Source Reconciliation Manifest

The frozen initiation manifest now retains and later reconciles:

- Beneficiary: bank account, immutable bank-verification decision, cancelled cheque, retained
  document and checksum, verifier, request, workflow, audit, and version identities.
- Source: bank account, current governance/version/audit identities, activation request, and source
  facts digest. The source owner validates every predecessor activation/deactivation version and
  audit before returning the current decision.
- Loan: exact public-owner creation status-history, audit, workflow, terms, application, member,
  amount, status, and zero-balance facts.
- Initiation: exact audit body, workflow transition, CFC task, maker role/team, request/comment/
  readiness/idempotency digests, amount, bank identities, and current pending state.

Changed IFSC/account hash/status, a newer bank decision, changed file checksum/ledger, replacement
source decision, incomplete source history, changed creation evidence, funded account, or later
transfer/advice/register truth returns no typed decision.
