# Risk Assessment

Risk level: High

The slice changes financial-policy immutability, interest rounding, and an atomic balance
reclassification. Incorrect behavior could rewrite approved calculation truth, misstate borrower
principal, or partially update financial and operational owners.

## Controls Applied

- Approved calculation configurations are immutable at the model, queryset, bulk, deletion, and
  PostgreSQL trigger layers from creation; amendments are separate approved versions.
- Legacy approved rows remain readable but have nullable rounding fields and fail closed when a new
  calculation attempts to consume them. No rounding policy was inferred for retained history.
- Monetary rounding is centralized and requires a supported mode, two-decimal precision, and the
  whole-decision boundary. Segment evidence retains unrounded values and the aggregate rounds once.
- Capitalisation locks and reconciles eligible invoice interest, account interest, FY schedule
  interest, through-cutoff payment applications, and the latest through-cutoff servicing ledger.
  Accounts with no servicing ledger history record that explicit state and use the locked account
  owner as the opening balance; any retained-ledger disagreement fails closed.
- All exact schedule transfers are proven equal to the principal increment before financial or
  communication writes. The operation remains one database transaction.
- PostgreSQL tests exercised raw-SQL immutability and both exact-key and changed-key competing races
  twice. Focused tests assert zero changes to balances, schedules, evidence, communications,
  documents, tasks, and audits for account, schedule, ledger, and payment-owner mismatches.

## Residual Risks

- The retained servicing fixture adapter still constructs the established capitalisation API setup
  internally. Public consumers use a bounded builder, but deeper fixture/module separation remains
  the pre-existing servicing-seam debt explicitly outside this closure slice.
- The full backend suite and coverage were intentionally not run in the agent sandbox; the Ralph
  orchestrator owns those independent authoritative gates.

No revoked approval, forbidden change, new dependency, frontend change, or external-provider change
was introduced.
