# Independent Standards and Spec Review

Two parallel read-only reviews inspected the full tracked and untracked diff against the selected
slice and repository standards.

## Initial findings

- The first checklist implementation created action/workflow evidence without linking the signature,
  account, or `ready` status on `DocumentChecklist`.
- The first evidence seam let `legal_documents` pull a transitive disbursement dependency through a
  shallow process wrapper.
- Inactive actor, aggregate persistence, ordered-stage, and missing relation coverage were partial.
- The pending advice model needed an explicit future legitimate `sent` state.

## Resolutions

- Signing now atomically links `senior_manager_finance_signature`, `loan_account_id`, `ready` status,
  action, audit, workflow, and version. Database constraints require the coherent ready tuple and
  prior sanction signature.
- The existing top-level `processes.document_checklist_actions` coordinator resolves and injects the
  immutable Finance decision; `legal_documents` imports no disbursement owner.
- Public tests now cover inactive, permission-only, role-only, cross-object, out-of-order, exact and
  changed replay, stale evidence, missing register/advice, and aggregate persistence.
- Advice intent allows only `pending` and `sent`; transfer/register identity remains coherent across
  that later authorised transition. This slice creates only `pending`.

The final spec re-review reported no remaining slice-fidelity issue. A standards follow-up repeated
the earlier pending-only concern, but the inspected final code explicitly accepts both `pending` and
`sent` in the model constraint and transfer coherence predicate.
