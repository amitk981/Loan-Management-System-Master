# Spec Review

Reviewed the same bounded diff against slices 010N2, 010N3, 010N4, CR-015, and their cited source
contracts.

- High: CR-015 requirement 3 and 010N2 requirements 3/5 require one backend-owned direct-repayment
  command, but the new compatibility path restores the forbidden browser-owned substeps.
- High: 010N3 AC-E10-I1/I2 require loan 101 never to be silently omitted. Metadata-only page
  validation and per-batch-only membership validation accept 101 rows containing 100 unique loans.
- High: 010N4 requirements 1/2 require canonical sensitive-input permission and object scope before
  match existence. Security facades query all matching instruments without the canonical package
  scope decision.
- Medium: `available_actions` remains an alias of effective permissions rather than a resource/action
  projection, and the SAP/CDSL input matrix covers only invented prefixes.

The MIS `generated_at` correction and reminder provider race are individually green, but the
terminal repair episode remains grouped and therefore cannot close while the servicing seam fails.
