# Quarterly MIS Evidence

## Focused behavior

- `terminal-logs/quarterly-mis-focused-green.log`: 7 API/catalogue tests pass, covering cutoff
  totals, typed snapshots, replay, frozen drill-down, permissions, validation, transitions/audits,
  document reconciliation, and reverse-owner reconciliation.
- `terminal-logs/quarterly-mis-postgresql-green.log`: the declared exact class collected and passed
  2 tests, retaining one report/snapshot/two documents under exact generation replay and one CFO
  review under changed-key terminal contention.
- `terminal-logs/quarterly-mis-reverse-consumers-green.log`: 7 owner-consumer tests pass.
- `terminal-logs/quarterly-mis-static-gates-green.log`: system check, migration drift, and diff check
  pass.
- RED logs retain the initial missing route/catalogue/transition/export/permission failures.

The seeded generation test asserts a query ceiling of 40 and exact totals of sanctioned/disbursed/
principal `400000.00`, interest and repayments `0.00`, plus a one-to-two-year DPD case. The repayment
reconciliation case retains `300000.00` principal and `100000.00` quarter repayments without
mutating allocation or ledger owner rows.

## Deterministic export samples

- `exports/quarterly-mis-sample.pdf`
  SHA-256: `b124f1f8ffda9f6ba092d568875ea006a8e4009e9429d0e6f973faa2005035d6`
- `exports/quarterly-mis-sample.xlsx`
  SHA-256: `b815abb430786d0aff13962717081f4c8db83b71d7c8b63a95c18d3160bbb9eb`

Both samples were regenerated from the final renderer with the same frozen totals, DPD dimension,
availability markers, drill-down row, and DPD calculation-version provenance.
