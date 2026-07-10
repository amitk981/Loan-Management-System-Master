# Risk Assessment

## Slice
`005A-loan-application-draft-create-update`

## Risk Level
Medium.

## Why
- Adds a new backend domain app, persistent `loan_applications` table, migration, and authenticated
  API endpoints.
- Touches borrower/member references, loan request amounts, bank metadata summaries, audit, and
  workflow-event foundations.
- Does not perform financial calculations, eligibility, reference sequencing, completeness,
  sanction, disbursement, payment, or external integrations.

## Controls Applied
- TDD red/green evidence saved for create/read and patch behavior.
- API tests cover create/read, patch, permissions, unknown member, malformed UUIDs, cross-member
  subresource references, non-positive amounts, metadata-only audit, and sensitive-value absence.
- Standard API envelopes are asserted with the existing contract test helpers.
- Draft responses and audit metadata include IDs and masked bank summaries only; no PAN, Aadhaar,
  full account numbers, encrypted token values, or hashes are serialized.
- `account_holder_name` remains the canonical bank holder field; no `holder_name` alias is added.
- One non-destructive migration was generated.
- A-035 records the intentional deferral of `LO...` reference generation and exact downstream
  submit/completeness behavior.

## Residual Risk
- Object-level loan-application access is still permission-only until assignment/ownership facts are
  modeled in later slices.
- Draft purpose category remains free text because the opened source sections do not define a
  complete enum table for this slice.
- Formal reference generation and loan request register behavior are deferred to 005C.
