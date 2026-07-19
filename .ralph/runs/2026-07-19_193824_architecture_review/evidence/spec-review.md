# Spec Review

Fixed point: `e748f8ca085a9ad2e174c6295bddbdd6d3f9cc3e`

Commit: `4f8febd3 chore(009L7-epic-009-read-boundary-convergence-closure): complete Ralph AFK run`

## Findings

- **High — requirement 2-3 owner recurrence:** the spec requires one decision for count, pages,
  rows, actions, detail, and mutation over “every scalar fact.” The active-account selector does not
  consume the canonical transfer decision; a review-only public HTTP probe changes the retained
  transfer document checksum, proves `resolve_post_transfer_evidence(...)` returns `None`, then
  receives list `(total_count=1, one row)` and detail `200` instead of `(0, [])` and `404`.
  Combined Senior Finance also counts initiation candidates before `_project_account_rows` can
  silently drop a row after `_disbursement_is_current` fails. This is the same retained root, not a
  newly relabelled finding.
- **Medium — requirement 4 is partial:** only six new one-row regressions were added. The declared
  Loan Account/S36/S37/combined/CFC 1/21/101 portfolios, more than four adjacent invalids, all page
  edges, all scalar consumers, paired actions/mutations, stable query ceilings, and independent
  400/403/404/409 matrix are absent; 21/101 coverage remains Loan-Account-only.
- **Medium/Low — requirement 5 is not met:** the management command now calls a public-named
  builder, but that builder still imports `FinalDocumentationApprovalApiTests`, invokes `setUp`,
  `_real_owner_initiation_fixture`, and `_user`. This preserves the active private-test seam and its
  associated duplication.

No scope creep was found. The direct substitution of initiation permission for the public read
grant is fixed, and `playwright.seed.ts` plus its focused tests close the ordinary/full-suite fixture
union defect. The retained High recurrence at corrective generation 2 requires fail-closed review
termination and no further leaf slice.
