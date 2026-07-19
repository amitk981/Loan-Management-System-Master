# Static 009L3 Contract Inspection

## Boundary

- Previous successful architecture review: `eacf85e3`.
- Reviewed product commit: `547c6835` (`009L3`).
- Proof-only follow-up: `692589f5`.
- Ralph-infrastructure commit `755525c2` was excluded from product findings.
- Product diff: 16 files, 381 insertions, 87 deletions.

## Findings reproduced from current source

- `sfpcl_credit/sap_workflow/modules/sap_customer_profile.py:305-350` selects the newest request for
  the member facade. Lines 353-393 independently select up to two completed rows restricted to the
  supplied application/member/code for the account facade. Both call an evidence helper, but they
  do not share one record-selection decision.
- `sfpcl_credit/processes/loan_account_360.py:46-60` evaluates `_project` for the entire candidate
  queryset, computes `len(projections)`, and only then applies the requested Python slice.
- `sfpcl_credit/processes/disbursement_workspace.py:62-74` calls the already-full-scanning Loan
  Account collection for page 1 and every subsequent 100-row page. Lines 125-130 then slice the
  composed workspace list again.
- The 009L3 diff adds no 21-row or 101-row mixed-scope pagination setup. Existing query ceilings in
  `test_loan_account_reads_api.py` and `test_disbursement_workspace_api.py` assert a one-row result.
- The diff adds one S36 allow case, one CFC governed-authority denial, one completion-digest drift,
  pending-only database rejection, and posting-count race assertions; it does not add the complete
  action/consumer/transport/error matrices declared by requirement 7.
- `sfpcl_credit/tests/test_epic009_postgresql_acceptance.py` subclasses the already-discovered race
  class without new behavior. The declared exact label passes, but the complete suite discovers the
  same inherited tests through both classes.
- The browser test titled “every governed tab” opens Loan Ledger and asserts two other tab buttons;
  it does not exercise the other unavailable bodies. The separate MP14 test does execute both list
  orders, but through fulfilled browser routes as permitted before `CR-012`'s real-Django proof.

## Contracts confirmed closed

- Migration/model constraints allow only `pending` with null reference/time for initial SAP posting.
- Transfer coherence requires exactly that pending shape, and retained PostgreSQL races assert one row.
- Loan Account 360 uses the established `Tabs` component with eleven fixture-free tab bodies.
