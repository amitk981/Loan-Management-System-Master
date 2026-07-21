# Spec Axis

Boundary: CR-015, 010MB, and 010N since successful review commit `33f5e5df`.

- CR-015 requirements 2 and AC-E10-F-2 require immutable cutoff-valid invoice truth. Production
  checks the wrong timestamp field, so a post-cutoff-generated backdated invoice is present in the
  historical row. The required before/on/after matrix is absent.
- CR-015 requirement 5 and AC-E10-F-5 require public builders and complete repayment/statement/
  portal/MIS matrices. The permanent direct-repayment class still calls another `TestCase.setUp()`,
  while closure evidence maps F-5 to an unrelated reminder test.
- 010MB requirements 2 and 4 require canonical complete interest state and forbid deceptively
  partial truth. One page of 100 accounts drives the complete-looking bulk accrual, omitting 101+.
- 010N requirements 2–3 require input permission/object scope and no sensitive match-existence leak.
  Its own CFO fixture has no blank-cheque/security read yet the implementation accepts a mocked
  cheque owner and returns the matched member.
- Supporting Medium symptoms are bundled into those roots: scoped applications are capped before
  access evaluation, application/account search by borrower input depends on member-read authority,
  and the frontend/browser proofs do not cover the stated authority and boundary matrices.

The reminder provider-gap acceptance is independently GREEN and is closed without masking the two
remaining CR-015 roots.
