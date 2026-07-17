# Risk Assessment

Risk level: High

This slice changes money-workflow authorisation, object scope, bank evidence, and database
constraints. It runs under the owner's standing approval and is not revoked.

Primary risks and mitigations:

- Stale beneficiary/source evidence could authorise the wrong transfer. Mitigated by locked,
  application-owned bank-decision reconciliation and complete source-governance chain validation.
- Divergent read/action predicates could show an action that mutation rejects (or vice versa).
  Mitigated by one typed current-evidence decision used by both CFC scope and authorisation.
- Partial terminal rows or forged later-transfer facts could survive application failures. Mitigated
  by database constraints covering pending/terminal tuples, maker-checker, role/comment evidence,
  and approval-before-transfer truth.
- Concurrency could retain multiple decisions or loser artifacts. Mitigated by row locks, atomic
  writes, uniqueness, and two independent PostgreSQL runs of the two five-caller race rounds.
- Sensitive bank data could leak through audit/HTTP. Mitigated by identity/digest/checksum-only
  manifests, unchanged redacted response, and retained nondisclosing object errors.

Residual risk: 009G must extend the approved typed decision with exact terminal-authorisation and
transfer evidence before funding. 009F2 intentionally creates no UTR, transfer, balance, advice,
register, checklist, repayment, or communication truth.
