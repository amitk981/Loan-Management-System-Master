# Standards Review

Fixed point: `f8eb78be`; reviewed product commit: `3b31edc4`.

- Hard violation: `sap_customer_profile.py:209-249` reconstructs terminal sanction from approval
  tables inside the SAP owner instead of delegating to the approval-owner seam. This conflicts with
  `CONTEXT.md`'s immutable-evidence/facade direction and codebase-design §§16/42.
- Hard violation: `assigned_workspace_row_count` and the CFC workspace count broader candidate
  sets than their stricter projectors accept (`sap_customer_profile.py:252-386`,
  `disbursement_workspace.py:171-203`). Totals and reachability can therefore disagree with rows.
- Architecture drift: `loan_account_lifecycle.py:255-325` adds a second scalar lifecycle-evidence
  validator alongside the retained validator around lines 367-436, creating two implementations of
  the same owner invariant.
- Test-quality concern: the 101-row fixture copies Django private `_state` and ledger rows instead
  of using the public owner interface; the new MP14 test changes an explicit-id prop without
  modelling the claimed surrounding application list.

The parallel standards pass classified the first two as hard documented-standard violations and
the latter two as judgment calls. Tool-enforced formatting was excluded.
